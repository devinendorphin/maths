"""Post-run descriptive summaries; no fitting or exclusion of measurements."""
import collections
import json
from pathlib import Path
import statistics
import sys


def key(item):
    d=item['logical'];stage=item['stage'];row=d.get('row',{}).get('case_id')
    if stage==121:return (stage,d['method'])
    return (stage,row,d.get('bucket'),d.get('query_count'),d.get('requested_method',d.get('method')),d.get('selected_method'),d.get('route'),d.get('requested_route'),d.get('budget'),d.get('certificate_cap'),d.get('selector_repair',False),d.get('supplement',False))


def dataset(root):
    records=[]
    for name in ['Results.json','Supplement.json','Selector-results.json']:records+=json.loads((root/name).read_text())
    groups=collections.defaultdict(list)
    for r in records:groups[key(r)].append(r)
    medians=[]
    for k,items in groups.items():
        cpu=[r['measurements']['total']['cpu'] for r in items];wall=[r['measurements']['total']['wall'] for r in items]
        phases=collections.defaultdict(list)
        for r in items:
            for name,v in r['measurements'].get('phases',{}).items():phases[name].append(v)
        medians.append(dict(group=k,records=len(items),cpu_median=statistics.median(cpu),cpu_min=min(cpu),cpu_max=max(cpu),wall_median=statistics.median(wall),phase_medians={n:statistics.median(v) for n,v in phases.items()}))
    memory=[dict(case=r['logical']['row']['case_id'],route=r['logical']['route'],budget=r['logical']['budget'],hits=sum(e['hit'] for e in r['logical']['events']),evictions=r['logical']['events'][-1]['evictions'],measurements=r['measurements']) for r in records if r['stage']==127]
    return dict(execution=json.loads((root/'Execution.json').read_text()),audit=json.loads((root/'Audit.json').read_text()),selector_audit=json.loads((root/'Selector-audit.json').read_text()),groups=medians,memory=memory,cap_repair=[dict(bucket=r['logical']['bucket'],repeat=r['repeat'],facts=len(r['logical']['facts']),failed=r['logical']['failed_probes'],cpu=r['measurements']['total']['cpu']) for r in records if r['logical'].get('supplement')],total_measured_campaign_cpu=sum(r['measurements']['total']['cpu'] for r in records),residual_cpu_range=[min(r['measurements']['residual_cpu'] for r in records if 'residual_cpu' in r['measurements']),max(r['measurements']['residual_cpu'] for r in records if 'residual_cpu' in r['measurements'])])


def run(first,second,out):
    a=dataset(first);b=dataset(second);aa={json.dumps(g['group']):g for g in a['groups']};bb={json.dumps(g['group']):g for g in b['groups']}
    differences=[dict(group=g,primary_cpu=aa[g]['cpu_median'],replica_cpu=bb[g]['cpu_median'],ratio=bb[g]['cpu_median']/aa[g]['cpu_median']) for g in aa]
    report=dict(description='Descriptive complete CPU/wall medians and ranges, all cases retained; original 126/130 policy entries are method-only; selector_repair entries include routing selection. Three repetitions except one-run control/memory scenarios. No significance or general speed claims.',base_models=dict(training=2,heldout=4,crossing_control=1,total=7),record_counts=dict(training_once=72,campaign_per_directory=451,cap_repair_per_directory=6,selector_repair_per_directory=60,fresh_replicated=517),training=json.loads((first/'Training-execution.json').read_text()),policy=json.loads((first/'Policy.json').read_text()),primary=a,replica=b,measurement_differences=differences)
    out.write_text(json.dumps(report,indent=2)+'\n')


if __name__=='__main__':run(Path(sys.argv[1]),Path(sys.argv[2]),Path(sys.argv[3]))
