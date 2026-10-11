"""One bounded complete session; raw writes and optional fsync are charged."""
import copy
import hashlib
import json
import os
from pathlib import Path
import resource
import sys
import time
from checker import digest, encode, verify
from delta import Captured
from producer import certificate, networkx_flow, potentials

ROOT = Path(__file__).resolve().parents[1]


def solve(m, context):
    value, x = networkx_flow(m)
    if x is None:
        from producer import feasibility
        _, cut = feasibility(m)
        p = certificate(m, context, cut=cut)
    else:
        pi, cycle = potentials(m, x)
        assert cycle is None
        p = certificate(m, context, flow=x, pi=pi)
        assert p['cost_units'] == value
    assert verify(m, p, context)
    return p


def run(root, index, route, rep, budget):
    resource.setrlimit(resource.RLIMIT_AS, (512*1024*1024,512*1024*1024))
    tick, cpu = time.perf_counter(), time.process_time()
    freeze = json.loads((ROOT/'Freeze.json').read_text())
    for path, sha in freeze['files'].items():
        assert hashlib.sha256((ROOT/path).read_bytes()).hexdigest() == sha
    context = freeze['context']
    entry = json.loads((ROOT/'Inputs.json').read_text())['heldout'][index]
    m = entry['model']
    out = Path(root); out.mkdir()
    durable = route == 'delta-fsync'
    written, io_s = 0, 0.0
    records, timing = [], {'initial':0.0,'updates':0.0,'recovery':0.0}
    def write(obj):
        nonlocal written, io_s
        start = time.perf_counter()
        data = encode(obj)+b'\n'
        log.write(data); log.flush()
        if durable: os.fsync(log.fileno())
        written += len(data)
        io_s += time.perf_counter()-start
    with (out/'Journal.jsonl').open('wb') as log:
        start = time.perf_counter()
        p = solve(m, context)
        state = Captured(m,p,context,budget=budget)
        write({'snapshot':state.checkpoint()})
        records.append({'step':0,'cost_units':p['cost_units'],'action':'initial',
                        'proof':copy.deepcopy(p),'version':0})
        timing['initial'] = time.perf_counter()-start
        for step, changes in enumerate(entry['changes'],1):
            start = time.perf_counter()
            message = {'version':step-1,'context':context,'changes':changes}
            # All routes read the same k-sized update. No raw-model delta scan.
            message = json.loads(encode(message))
            if route.startswith('delta'):
                r = state.patch(message)
                if r['accepted']:
                    if r['compacted']: write({'snapshot':state.checkpoint()})
                    else: write({'patch':r['record']})
                    rec = {'step':step,'version':state.version,'action':'patch',
                           'cost_units':state._p['cost_units'], 'edge_checks':r['edge_checks'],
                           'compacted':r['compacted'],'journal_bytes':state.bytes,'head':state.head}
                else:
                    m, old = state.export()
                    for z in changes: m['edges'][z['edge']]['c'] = z['new']
                    p = solve(m,context)
                    state = Captured(m,p,context,step,budget)
                    write({'snapshot':state.checkpoint()})
                    rec = {'step':step,'version':step,'action':'fallback',
                           'cost_units':p['cost_units'],'proof':copy.deepcopy(p),
                           'edge_checks':r['edge_checks'],'reason':r['reason']}
            else:
                for z in changes:
                    assert m['edges'][z['edge']]['c'] == z['old']
                    m['edges'][z['edge']]['c'] = z['new']
                rec = {'step':step,'version':step}
                if route == 'full-recheck':
                    candidate = certificate(m,context,flow=p['flow'],pi=p['pi'])
                    accepted = verify(m,candidate,context)
                else: accepted = False
                if accepted: p = candidate; rec['action']='full-recheck'
                else: p=solve(m,context); rec['action']='cold' if route=='cold' else 'fallback'
                write({'model_digest':digest(m),'proof':p,'version':step})
                rec.update(cost_units=p['cost_units'],proof=copy.deepcopy(p))
            assert not ('journal_bytes' in rec) or rec['journal_bytes'] <= budget
            records.append(rec)
            timing['updates'] += time.perf_counter()-start
        # All routes finish with a replayable full checkpoint and full admission.
        start = time.perf_counter()
        if not route.startswith('delta'): state=Captured(m,p,context,24,budget)
        bundle = state.checkpoint()
        data = encode(bundle)
        temporary=out/'Checkpoint.tmp'
        temporary.write_bytes(data)
        if durable:
            with temporary.open('rb') as f: os.fsync(f.fileno())
        os.replace(temporary,out/'Checkpoint.json')
        if durable:
            directory=os.open(out,os.O_RDONLY|os.O_DIRECTORY)
            try:os.fsync(directory)
            finally:os.close(directory)
        recovered = Captured.restore(json.loads((out/'Checkpoint.json').read_bytes()),context,
                                     expected_anchor=(state.version,state.head))
        rm,rp = recovered.export()
        assert verify(rm,rp,context)
        timing['recovery'] = time.perf_counter()-start
    result = {'index':index,'route':route,'repetition':rep,'budget':budget,
              'records':records,'timing':timing,'journal_write_bytes':written,
              'journal_io_s':io_s,'checkpoint_bytes':len(data),
              'final_model':digest(rm),'final_proof':hashlib.sha256(encode(rp)).hexdigest(),
              'context':context,'worker_wall_s':time.perf_counter()-tick,
              'worker_cpu_s':time.process_time()-cpu,
              'worker_peak_rss_kib':resource.getrusage(resource.RUSAGE_SELF).ru_maxrss}
    (out/'Worker.json').write_text(json.dumps(result,sort_keys=True,indent=2)+'\n')


if __name__ == '__main__':
    run(sys.argv[1],int(sys.argv[2]),sys.argv[3],int(sys.argv[4]),int(sys.argv[5]))
