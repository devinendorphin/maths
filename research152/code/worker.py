"""Fresh process, full proof journal, transactional caller input, all costs charged."""
import copy
import hashlib
import json
from pathlib import Path
import resource
import sys
import time
from checker import digest, encode
from engine import Engine
from environment import capture

ROOT=Path(__file__).resolve().parents[1]


def run(destination,index,route,rep):
    resource.setrlimit(resource.RLIMIT_AS,(2*1024**3,2*1024**3))
    tick=time.perf_counter();cpu=time.process_time();f=json.loads((ROOT/'Freeze.json').read_text());ctx=f['context']
    for name,h in f['files'].items():assert hashlib.sha256((ROOT/name).read_bytes()).hexdigest()==h
    assert capture()==f['environment']
    entry=json.loads((ROOT/'Inputs.json').read_text())['heldout'][index];e=Engine(entry['model'],ctx,route)
    out=Path(destination);out.mkdir();records=[];nbytes=0;query_times=[];phase_times=[]
    with (out/'Evidence.jsonl').open('wb') as log:
        for step,q in enumerate([None]+[dict(copy.deepcopy(z['message']),context=ctx) for z in entry['updates']]):
            r=e.query(q);query_times.append(r.pop('query_wall_s'));phase_times.append(r.pop('timing'));r['step']=step
            data=encode(r)+b'\n';log.write(data);log.flush();nbytes+=len(data);records.append(copy.deepcopy(r))
    e.close()
    result={'index':index,'route':route,'repetition':rep,'context':ctx,'records':records,'evidence_bytes':nbytes,
            'final_model':digest(e.state.model),'final_proof':hashlib.sha256(encode(e.proof)).hexdigest(),
            'query_wall_s':query_times,'phase_times':phase_times,'worker_wall_s':time.perf_counter()-tick,'worker_cpu_s':time.process_time()-cpu,
            'worker_maxrss_kib':resource.getrusage(resource.RUSAGE_SELF).ru_maxrss}
    (out/'Worker.json').write_text(json.dumps(result,sort_keys=True,indent=2)+'\n')


if __name__=='__main__':run(sys.argv[1],int(sys.argv[2]),sys.argv[3],int(sys.argv[4]))
