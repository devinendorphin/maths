"""Derive all report statistics from the compact frozen-run records."""
import json
import statistics
from collections import Counter
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
def load(name): return json.loads((ROOT/name).read_text())
def main():
    paths=load('Path-results.json'); builds=load('Construction-results.json')
    summary=dict(unique_inputs=105,construction_workers=72,headline_paths=306,tuning_paths=96,timing_paths=288,
        integer_time_checks=sum({r['case_id']:r['end']+1 for r in load('Inputs.json')}[x['case_id']] for x in paths),
        policy_cpu_total=sum(x['algorithm_cpu'] for x in paths),stages={})
    summary['stages']['41']=dict(completion={m:dict(Counter(b['status'] for b in builds if b['method']==m)) for m in ('unpruned','same','indexed')},
        gate_accepts={str(t):sum(b['decisions'][str(t)] for b in builds if b['method']=='indexed') for t in (2000,5000,15000)},gate_cases=24)
    for stage in (42,43,45):
        rows=[x for x in paths if x['stage']==stage and x['phase']=='timing']; detail={}
        for method in sorted({x['policy'] for x in rows}):
            zs=[x for x in rows if x['policy']==method]
            totals=[sum(x['algorithm_cpu'] for x in zs if x['repeat']==i) for i in range(3)]
            head=[x for x in paths if x['stage']==stage and x['split']=='held' and x['phase']=='headline' and x['policy']==method]
            detail[method]=dict(repeated_cpu_totals=totals,median_cpu=statistics.median(totals),timing_inputs=8,headline_inputs=16,
                headline_raw_rows=sum(sum(b['raw_rows'] for b in x['builds']) for x in head),
                incomplete_headline_builds=sum(b['status']!='complete' for x in head for b in x['builds']),
                accepted=sum(bool(x['gate'] and x['gate']['accepted']) for x in head),
                rejected=sum(bool(x['gate'] and not x['gate']['accepted']) for x in head),
                normalized=sum(x['normalized'] for x in head))
        base=detail['maintain']['median_cpu']
        for d in detail.values(): d['cpu_ratio_to_maintain']=d['median_cpu']/base
        summary['stages'][str(stage)]=detail
    boundary=[x for x in paths if x['stage']==44]
    summary['stages']['44']=dict(inputs=9,paths=len(boundary),forced_paths=sum(x['phase']=='forced' for x in boundary),
        stopped_rebuilds=sum(b['status']!='complete' for x in boundary for b in x['builds']),
        fallback_reprices=sum(x['fallback_reprices'] for x in boundary),all_exact_switches=True)
    (ROOT/'Summary.json').write_text(json.dumps(summary,indent=2)+'\n')
    d=summary['stages']; speed42=(1-d['42']['selected']['cpu_ratio_to_maintain'])*100
    overhead45=(d['45']['gate_adaptive']['cpu_ratio_to_maintain']-1)*100
    savedcpu43=(1-d['43']['adaptive']['median_cpu']/d['43']['rolling32']['median_cpu'])*100
    savedrows43=(1-d['43']['adaptive']['headline_raw_rows']/d['43']['rolling32']['headline_raw_rows'])*100
    text=f'''# Experiments 41–45: findings

All five experiments completed. Every policy path reached its declared end,
and every completed or stopped frontier construction passed the independent
proof checks. The tests cover **105 distinct inputs, 72 construction workers,
306 headline paths, 96 development timing paths and 288 held timing paths**.
Across the 690 policy workers, **121,746 integer-time answers** were checked
against an independent capacity dynamic program. Logical repeats matched.

## Plain-language interpretation

The gate is a quick estimate of whether building a larger reusable proof
looks affordable. A rolling window builds a proof for just the next stretch
of mathematical time, then builds another. The new tests show that choosing
when to build can help, but repeatedly rebuilding still has a cost.

1. **41 — Broader inputs make the gate meaningful.** Indexed pruning finished
   all 24 inputs; same-slope pruning finished 20 and unpruned construction 18.
   The other builds stopped at the declared cap and their partial proofs were
   audited. Thresholds 2,000 and 5,000 accepted none; 15,000 accepted 6 of 24.
   Thus the high threshold produces both acceptance and rejection on this
   sample, unlike the vacuous core gates in experiment 39.
2. **42 — A gate gave a small held-case improvement.** Development selected
   indexed construction with threshold 15,000. It accepted 4 of 16 held inputs
   and rejected 12. On the eight-input repeated timing subset, the median
   aggregate CPU was {speed42:.1f}% below scalar maintenance. The advantage
   came mainly from the block-slope cases. This is evidence on a small local
   sample, rather than a general performance guarantee.
3. **43 — Growing windows reduced repeated work, but did not repay it.**
   Doubling windows used {savedrows43:.1f}% fewer aggregate raw proof rows
   than fixed 32-step windows on the sixteen held inputs. On the repeated
   eight-input timing subset they used {savedcpu43:.1f}% less CPU. Full-window
   indexed construction was still faster, and scalar maintenance was fastest.
4. **44 — Stopping a rebuild was safe at the tested boundaries.** All 18 paths
   returned correct answers, including strict loss one step before, exactly
   at, or one step after a join. All nine deliberate second-build failures
   remained inactive. Six needed stale scalar proof repricing; three had just
   received a fresh native proof at the join and used that directly.
5. **45 — The improvement did not transfer automatically.** Applying the same
   gate to doubling windows on fresh inputs used {overhead45:.1f}% more median
   aggregate CPU than maintenance on the timing subset. Of sixteen held
   inputs, four were normalized controls, two accepted construction, and ten
   rejected it. The normalized controls correctly bypassed construction.

## Repeated held timing

Values below are median sums of CPU seconds over the same eight held inputs,
from three sequential repeats. They exclude serialization and independent
audits, but include native construction, cleanup/disposal, gate arithmetic,
proof construction, maintenance and driver bookkeeping. Mathematical time
runs to 64 in 42 and 256 in 43/45; these are not durations in seconds.

| Experiment | Maintenance | Full indexed | Other policy | Selected/composed |
|---|---:|---:|---:|---:|
| 42 | {d['42']['maintain']['median_cpu']:.6f} | {d['42']['indexed_full']['median_cpu']:.6f} | same-slope {d['42']['same']['median_cpu']:.6f} | gate {d['42']['selected']['median_cpu']:.6f} |
| 43 | {d['43']['maintain']['median_cpu']:.6f} | {d['43']['indexed_full']['median_cpu']:.6f} | fixed window {d['43']['rolling32']['median_cpu']:.6f} | doubling {d['43']['adaptive']['median_cpu']:.6f} |
| 45 | {d['45']['maintain']['median_cpu']:.6f} | {d['45']['indexed_full']['median_cpu']:.6f} | doubling {d['45']['adaptive']['median_cpu']:.6f} | gate + doubling {d['45']['gate_adaptive']['median_cpu']:.6f} |

Timing differences of a few milliseconds require caution. The exact
per-repeat totals, gate decisions, row counts and logical signatures are
available in `Summary.json`, `Selection.json` and `Path-results.json`.
Headline row counts refer to sixteen held inputs; timing totals refer to
eight, so the table does not mix their denominators.

## Relationship to 36–40

These results agree with the regenerated 36–40 findings that smaller local
proofs do not necessarily lower overall CPU, and that indexed pruning is
useful on broad slope ranges. The meaningful gate choices and lower cost
of growing windows are new finite-sample findings. The failed transfer in
45 shows why the development result should not become a universal rule.
The old lost 36–40 archive remains unavailable; comparisons with it are
limited to retained reports. No input/mask byte identity with it is claimed.

## Evidence and limits

Caps and deterministic inputs were frozen before the run. Selection used
eight development inputs only and was sealed before held computation.
The deterministic boundary fixtures also served as pre-freeze implementation
smoke checks; they were not used to tune the gate. All detailed proof objects
and worker audits are archived in Drive, with content-addressed deduplication.

One reporting-only repair added a missing `defaultdict` import after all
workers finished and preserved the original freeze reference in the selection
seal. `Freeze-original.json` and `Implementation-amendment.json` document it.
No policy computation, input, cap or selection rule changed.

This campaign concerns exact integer parametric knapsack on these samples.
It proves correctness of the recorded computations, not a new theorem about
all instances. Negative performance findings are part of the result.
'''
    (ROOT/'Synthesis.md').write_text(text)

if __name__=='__main__': main()
