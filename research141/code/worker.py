"""Matched full/compact storage sessions; active recovery and raw evidence differ."""
import copy
import hashlib
import json
import os
from pathlib import Path
import resource
import sys
import time
from checker import digest,encode,verify
from delta import Captured
from predecessor_worker import solve
from recovery import hashed,image,proof_change,replay

ROOT=Path(__file__).resolve().parents[1]


def run(destination,index,fmt,policy,repetition):
    resource.setrlimit(resource.RLIMIT_AS,(512*1024*1024,512*1024*1024))
    start,cpu=time.perf_counter(),time.process_time()
    freeze=json.loads((ROOT/'Freeze.json').read_text());context=freeze['context']
    for path,h in freeze['files'].items():assert hashlib.sha256((ROOT/path).read_bytes()).hexdigest()==h
    inputs=json.loads((ROOT/'Inputs.json').read_text());entry=inputs['heldout'][index];cfg=inputs['policies'][policy]
    base=copy.deepcopy(entry['model']);m=copy.deepcopy(base)
    out=Path(destination);out.mkdir();active=out/'active';active.mkdir()
    (active/'base.json').write_bytes(encode(base))
    p=solve(m,context);state=Captured(m,p,context,budget=10**9)
    head=hashlib.sha256(encode({'base':digest(base),'context':context})).hexdigest()
    version=0;live=[];live_bytes=0;records=[];snapshots=0;written=len(encode(base));peak=0;recovered=0
    def footprint():return sum(f.stat().st_size for f in active.iterdir() if f.is_file())
    def checkpoint():
        nonlocal live,live_bytes,snapshots,written,peak,recovered
        mm,pp=state.export();snap=image(base,mm,pp,version,head,fmt,context);data=encode(snap)
        tmp=active/'snapshot.tmp';tmp.write_bytes(data);peak=max(peak,footprint());os.replace(tmp,active/'snapshot.json')
        (active/'journal.jsonl').write_bytes(b'');(active/'anchor.json').write_bytes(encode([version,head]))
        live=[];live_bytes=0;snapshots+=1;written+=len(data)+len(encode([version,head]))
        peak=max(peak,footprint())
        assert replay(base,json.loads((active/'snapshot.json').read_bytes()),[],context,[version,head])==(mm,pp)
        recovered+=1
        return snap
    snap=checkpoint()
    with (out/'Evidence.jsonl').open('wb') as raw:
        raw.write(encode({'snapshot':snap})+b'\n');raw.flush()
        records.append({'step':0,'action':'initial','value':p['cost_units'],'proof':p,'live_bytes':0})
        for step,changes in enumerate(entry['changes'],1):
            msg={'version':version,'context':context,'changes':changes}
            decision=state.patch(msg)
            if decision['accepted']:
                payload={'message':msg,'action':'patch','cost_units':state._p['cost_units']}
                proof=None
            else:
                m,old=state.export()
                for z in changes:m['edges'][z['edge']]['c']=z['new']
                p=solve(m,context);state=Captured(m,p,context,step,10**9)
                payload={'message':msg,'action':'recertify','cost_units':p['cost_units']}
                if fmt=='compact':payload['difference']=proof_change(old,p)
                else:payload.update(model=m,proof=p)
                proof=p
            event={'previous':head,'payload':payload,'head':hashed(head,payload)}
            head=event['head'];version=step;data=encode(event)+b'\n'
            raw.write(encode({'event':event})+b'\n');raw.flush()
            # Oversized event goes directly into a full checked recovery image.
            reason=None
            if live_bytes+len(data)>cfg['budget']:reason='byte-budget'
            elif step%cfg['cadence']==0:reason='cadence'
            if reason:
                snap=checkpoint();raw.write(encode({'snapshot':snap,'reason':reason})+b'\n');raw.flush()
            else:
                with (active/'journal.jsonl').open('ab') as journal:journal.write(data);journal.flush()
                live.append(event);live_bytes+=len(data);written+=len(data)
                (active/'anchor.json').write_bytes(encode([version,head]));written+=len(encode([version,head]))
                peak=max(peak,footprint())
            rec={'step':step,'action':payload['action'],'value':payload['cost_units'],'edge_checks':decision['edge_checks'],
                 'head':head,'live_bytes':live_bytes,'checkpoint_reason':reason}
            if proof:rec['proof']=copy.deepcopy(proof)
            records.append(rec)
        before=state.export()
        restored=replay(base,json.loads((active/'snapshot.json').read_bytes()),
                        [json.loads(line) for line in (active/'journal.jsonl').read_bytes().splitlines()],context,[version,head])
        assert restored==before;recovered+=1
        snap=checkpoint();raw.write(encode({'snapshot':snap,'reason':'terminal'})+b'\n')
    result={'index':index,'format':fmt,'policy':policy,'repetition':repetition,'context':context,
            'records':records,'snapshots':snapshots,'recovery_checks':recovered,'active_peak_bytes':peak,
            'active_final_bytes':footprint(),'active_written_bytes':written,
            'raw_evidence_bytes':(out/'Evidence.jsonl').stat().st_size,
            'final_model':digest(before[0]),'final_proof':hashlib.sha256(encode(before[1])).hexdigest(),
            'worker_wall_s':time.perf_counter()-start,'worker_cpu_s':time.process_time()-cpu,
            'worker_maxrss_kib':resource.getrusage(resource.RUSAGE_SELF).ru_maxrss}
    (out/'Worker.json').write_text(json.dumps(result,indent=2,sort_keys=True)+'\n')


if __name__=='__main__':run(sys.argv[1],int(sys.argv[2]),sys.argv[3],int(sys.argv[4]),int(sys.argv[5]))
