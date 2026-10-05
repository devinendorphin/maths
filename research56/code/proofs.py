"""Bounded external VIPR point/interval tests and explicit scope rejection."""
from fractions import Fraction
import resource
import subprocess
import time
from shared import ROOT,DEPS,SG,vipr_adapter,value,frac,digest,save


def connect(left,right,model):
    if model['objective_type']!='affine' or model['feasible_type']!='constant':return False
    if left['domain']!=right['domain'] or left['domain']!=model['domain']:return False
    if left['coefficients']!=right['coefficients'] or left['coefficients']!=model['coefficients']:return False
    return left['packing']==right['packing'] and Fraction(*left['time'])<=Fraction(*right['time'])


def run(row,curve,checker):
    folder=ROOT/'evidence/vipr';folder.mkdir(parents=True,exist_ok=True);records=[];bundles=[]
    domain=digest([row['n'],row['weights'],row['capacity']]);coefficients=digest([row['profits'],row['slopes']])
    model=dict(objective_type='affine',feasible_type='constant',domain=domain,coefficients=coefficients)
    def endpoint(t,mask=None):
        t=Fraction(t);q=[t.denominator*p+t.numerator*v for p,v in zip(row['profits'],row['slopes'])]
        start=time.process_time();source=SG.solve(row['weights'],q,row['capacity'],deadline=time.perf_counter()+30);native_cpu=time.process_time()-start
        if mask is None:mask=source['packing']
        assert value(q,mask)==source['objective']==checker.optimum(t)[0] and source['empty']
        start=time.process_time();text,info=vipr_adapter.certificate(row,t,mask,source['proof']);adapter_cpu=time.process_time()-start
        stem=row['case_id']+'-'+str(len(records));p=folder/(stem+'.vipr');p.write_text(text)
        before=resource.getrusage(resource.RUSAGE_CHILDREN);wall=time.perf_counter()
        checked=subprocess.run([str(DEPS/'vipr/viprchk'),str(p)],capture_output=True,text=True,timeout=30)
        after=resource.getrusage(resource.RUSAGE_CHILDREN);checker_wall=time.perf_counter()-wall
        checker_cpu=after.ru_utime+after.ru_stime-before.ru_utime-before.ru_stime
        assert checked.returncode==0 and 'Successfully verified optimal value range' in checked.stdout
        lines=text.splitlines();last=lines[-1].split();last[2]=str(info['scaled_objective']-1);lines[-1]=' '.join(last)
        bad=folder/(stem+'-invalid.vipr');bad.write_text('\n'.join(lines)+'\n')
        invalid=subprocess.run([str(DEPS/'vipr/viprchk'),str(bad)],capture_output=True,text=True,timeout=30)
        assert invalid.returncode!=0
        records.append(dict(time=frac(t),packing=mask,domain=domain,coefficients=coefficients,source=source,
                            native_cpu=native_cpu,adapter_cpu=adapter_cpu,checker_cpu=checker_cpu,checker_wall=checker_wall,
                            info=info,bytes=len(text.encode()),stdout=checked.stdout,invalid_stdout=invalid.stdout,
                            valid=checked.returncode==0,invalid_rejected=invalid.returncode!=0))
        return len(records)-1
    for t in (0,row['end']):endpoint(t)
    for piece in curve['intervals'][:2]:
        l=Fraction(*piece['left']);h=Fraction(*piece['right']);mask=piece['line'][2]
        pair=[endpoint(l,mask),endpoint(h,mask)];assert connect(records[pair[0]],records[pair[1]],model)
        checks=0
        for t in range((l.numerator+l.denominator-1)//l.denominator,h.numerator//h.denominator+1):
            assert value(row['profits'],mask)+t*value(row['slopes'],mask)==checker.optimum(t)[0];checks+=1
        bundles.append(dict(left=frac(l),right=frac(h),packing=mask,endpoints=pair,integer_checks=checks,accepted=True))
    assert bundles
    first=bundles[0];left,right=[records[j] for j in first['endpoints']]
    rejected=[]
    for reason,changed in [('changing_capacity',dict(model,feasible_type='varying')),
                           ('nonlinear_objective',dict(model,objective_type='quadratic')),
                           ('different_domain',dict(model,domain='different-domain'))]:
        assert not connect(left,right,changed);rejected.append(reason)
    unequal=dict(right,packing=right['packing']^1)
    assert not connect(left,unequal,model);rejected.append('different_packing')
    result=dict(case_id=row['case_id'],records=records,bundles=bundles,rejected_scopes=rejected,
                limitations='Metadata/theorem connector is ordinary Python. Scope rejection assumes an explicit truthful trajectory model; VIPR alone certifies points.')
    save(ROOT/'evidence'/('64-proof-'+row['case_id']+'.json.gz'),result)
    return dict(case_id=row['case_id'],certificates=len(records),invalid_rejected=len(records),bundles=len(bundles),
                rejected_scopes=len(rejected),integer_checks=sum(x['integer_checks'] for x in bundles),
                bytes=sum(x['bytes'] for x in records),derivations=sum(x['info']['derivations'] for x in records),
                **{k:sum(x[k] for x in records) for k in ('native_cpu','adapter_cpu','checker_cpu','checker_wall')})
