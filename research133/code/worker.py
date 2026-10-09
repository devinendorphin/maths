"""One bounded process/session. No subprocesses; complete durable result record."""
import copy
import hashlib
import json
from pathlib import Path
import resource
import sys
import time
from fractions import Fraction
from checker import digest, encode, verify
from routes import answer, invalid_controls


ROOT=Path(__file__).resolve().parents[1]


def save(path,obj):path.write_text(json.dumps(obj,sort_keys=True,indent=2)+'\n')


def run(mode,index,method,repetition,output,cache_limit=4096):
    resource.setrlimit(resource.RLIMIT_AS,(256*1024*1024,256*1024*1024))
    started=time.perf_counter();cpu=time.process_time()
    freeze=json.loads((ROOT/'Freeze.json').read_text())
    for name,sha in freeze['files'].items():assert hashlib.sha256((ROOT/name).read_bytes()).hexdigest()==sha,name
    inputs=json.loads((ROOT/'Inputs.json').read_text());dependency=freeze['dependency']
    out=Path(output);out.mkdir(parents=True,exist_ok=True)
    records=[];previous=None;cache_peak=0;evictions=0
    def query(m,label):
        nonlocal previous,cache_peak,evictions
        t=time.perf_counter();qcpu=time.process_time()
        tick=time.perf_counter();m=json.loads(encode(m));decode=time.perf_counter()-tick
        p,timing,counters,attempts=answer(m,method,previous,dependency)
        timing['encoding_s']=timing.get('encoding_s',0)+decode
        tick=time.perf_counter();assert verify(m,p,dependency);timing['checker_s']=time.perf_counter()-tick
        tick=time.perf_counter();data=encode(p);proof_id=hashlib.sha256(data).hexdigest();timing['serialization_s']=time.perf_counter()-tick
        if len(data)>16384:raise RuntimeError('proof-storage limit')
        file=out/(label+'.json')
        tick=time.perf_counter();file.write_bytes(data);restored=json.loads(file.read_bytes());assert verify(m,restored,dependency);timing['io_replay_s']=time.perf_counter()-tick
        tick=time.perf_counter();size=len(data)
        if size<=cache_limit:previous=copy.deepcopy(p);cache_peak=max(cache_peak,size)
        else:previous=None;evictions+=1
        timing['maintenance_s']=time.perf_counter()-tick
        record={'label':label,'model':m,'proof':p,'proof_sha256':proof_id,'proof_bytes':size,'attempts':attempts,'counters':counters,'cache_bytes':size if previous is not None else 0,'evictions_so_far':evictions,'timing':timing,'query_wall_s':time.perf_counter()-t,'query_cpu_s':time.process_time()-qcpu}
        records.append(record);return record
    extras={}
    if mode=='static':
        for i,m in enumerate(inputs['static']):
            previous=None;r=query(m,str(i));r['controls']=invalid_controls(m,r['proof'],dependency)
    elif mode in ('updates','budget'):
        stream=inputs['heldout'][index]
        for i,m in enumerate(stream['models']):query(m,str(i))
    elif mode=='development':
        for i,m in enumerate(inputs['development']):previous=None;query(m,str(i))
    elif mode=='fairness':
        case=inputs['fairness'][index];base=case['model']
        scalar=query(base,'scalar')
        previous=None
        candidates=sorted({Fraction(i,d) for d in case['demands'] for i in range(d+1)},reverse=True)
        selected=None
        for k,rate in enumerate(candidates):
            m=copy.deepcopy(base);m['id']=base['id']+'/coverage/'+str(rate)
            for r,d in enumerate(case['demands']):
                floor=(rate.numerator*d+rate.denominator-1)//rate.denominator
                m['edges'][6+r]['l']=max(case['floors'][r],floor)
            rec=query(m,'coverage-'+str(k));rec['coverage_candidate']=str(rate)
            if rec['proof']['kind']=='optimal':selected=str(rate);break
        extras={'selected_coverage':selected,'demands':case['demands'],'floors':case['floors'],'scalar_cost_units':scalar['proof'].get('cost_units'),'fair_cost_units':records[-1]['proof'].get('cost_units') if selected is not None else None,'scalar_certificate_alone_establishes_max_min':False}
    elif mode=='counterexample':
        case=inputs['counterexample'];last=None;changes=0
        for k,c in enumerate(case['costs']):
            m=copy.deepcopy(case['model']);m['id']='counter/'+str(k);m['edges'][0]['c']=c
            r=query(m,str(k))
            if last is not None:assert last!=r['proof']['flow'];changes+=1
            last=r['proof']['flow']
        extras={'single_edge_updates':changes,'optimal_plan_changes':changes}
    else:raise ValueError(mode)
    summary={'mode':mode,'index':index,'method':method,'repetition':repetition,'cache_limit':cache_limit,'dependency':dependency,'records':records,'cache_peak_bytes':cache_peak,'evictions':evictions,'extras':extras,'worker_wall_s':time.perf_counter()-started,'worker_cpu_s':time.process_time()-cpu,'kernel_self_maxrss_kib':resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,'child_processes':0}
    save(out/'Worker.json',summary)
    print(json.dumps({'records':len(records),'worker_wall_s':summary['worker_wall_s']}))


if __name__=='__main__':run(sys.argv[1],int(sys.argv[2]),sys.argv[3],int(sys.argv[4]),sys.argv[5],int(sys.argv[6]) if len(sys.argv)>6 else 4096)
