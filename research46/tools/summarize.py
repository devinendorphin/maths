"""Derive readable finite-sample results from compact worker records."""
import json
import statistics
from collections import Counter, defaultdict
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
def load(name):return json.loads((ROOT/name).read_text())

def main():
    rows=load('Path-results.json');audit=load('Audit-summary.json')
    result=dict(unique_inputs=110,headline_paths=444,tuning_paths=216,timing_paths=360,
        integer_time_checks=sum(r['integer_time_checks'] for r in rows),
        algorithm_cpu_total=sum(r['algorithm_cpu'] for r in rows),selections={str(s):load(f'Selection-{s}.json')['chosen'] for s in (47,48)},stages={})
    assert result['integer_time_checks']==audit['integer_time_checks']
    for stage in (46,47,48,50):
        timed=[r for r in rows if r['stage']==stage and r['phase']=='timing'];details={}
        for method in sorted({r['policy'] for r in timed}):
            zs=[r for r in timed if r['policy']==method]
            totals=[sum(r['algorithm_cpu'] for r in zs if r['repeat']==rep) for rep in range(3)]
            head=[r for r in rows if r['stage']==stage and r['phase']=='headline' and r['split']=='held' and r['policy']==method]
            cases=sorted({r['case_id'] for r in zs});paired=[]
            for case in cases:
                m=statistics.median(r['algorithm_cpu'] for r in zs if r['case_id']==case)
                base=statistics.median(r['algorithm_cpu'] for r in timed if r['case_id']==case and r['policy']=='maintain')
                paired.append(dict(case_id=case,cpu=m,maintenance_cpu=base,ratio=m/base))
            details[method]=dict(repeat_cpu_totals=totals,median_cpu=statistics.median(totals),timing_inputs=len(cases),headline_inputs=len(head),
                headline_raw_rows=sum(b['raw_rows'] for r in head for b in r['builds']),
                incomplete_headline_builds=sum(b['status']!='complete' for r in head for b in r['builds']),
                accepted=sum(bool(r['gate'] and r['gate']['accepted']) for r in head),
                rejected=sum(bool(r['gate'] and not r['gate']['accepted']) for r in head),
                normalized=sum(r['normalized'] for r in head),
                stopped_renewals=sum(e['stop'] for r in head for e in r['renewal_decisions']),
                fallback_reprices=sum(r['fallback_reprices'] for r in head),paired=paired,
                paired_wins=sum(p['ratio']<1 for p in paired),paired_losses=sum(p['ratio']>1 for p in paired))
        for d in details.values():d['cpu_ratio_to_maintenance']=d['median_cpu']/details['maintain']['median_cpu']
        result['stages'][str(stage)]=details
    result['training_equivalence']={}
    for stage,count in ((47,5),(48,4)):
        fingerprints=[]
        for ix in range(count):
            zs=sorted((r for r in rows if r['phase']==f'tuning{stage}_{ix}' and r['repeat']==0),key=lambda r:r['case_id'])
            fingerprints.append(tuple(r['signature'] for r in zs))
        result['training_equivalence'][str(stage)]=[[ix for ix,f in enumerate(fingerprints) if f==signature] for signature in dict.fromkeys(fingerprints)]
    legacy=[r for r in rows if r['stage']==46 and r['phase']=='headline' and r['policy']=='legacy_gate']
    pairs=defaultdict(list)
    for r in legacy:pairs[(r['pair_group'],r['end'])].append(r)
    matched=[]
    for (group,end),zs in sorted(pairs.items()):
        zs=sorted(zs,key=lambda r:r['scale']);assert len(zs)==2
        for key in ('prefix_bounds','E_bound','T_bound'):
            assert zs[0]['gate']['features'][key]==zs[1]['gate']['features'][key]
        assert zs[0]['gate']['accepted']==zs[1]['gate']['accepted']
        matched.append(dict(pair_group=group,end=end,bound=zs[0]['gate']['features']['E_bound'],accepted=zs[0]['gate']['accepted'],
            scale1_cpu=zs[0]['algorithm_cpu'],scale8_cpu=zs[1]['algorithm_cpu']))
    result['matched_scaling_pairs']=matched
    result['46_timing_conditions']={}
    for end in (64,256):
        for scale in (1,8):
            condition={}
            for method in ('maintain','indexed_full','legacy_gate'):
                zs=[r for r in rows if r['stage']==46 and r['phase']=='timing' and r['end']==end and r['scale']==scale and r['policy']==method]
                totals=[sum(r['algorithm_cpu'] for r in zs if r['repeat']==i) for i in range(3)]
                condition[method]=dict(median_cpu=statistics.median(totals),repeat_cpu_totals=totals,inputs=2)
            result['46_timing_conditions'][f'H{end}-scale{scale}']=condition
    boundary=[r for r in rows if r['stage']==49]
    forced=[r for r in boundary if r['policy'].startswith('forced_')]
    result['stages']['49']=dict(inputs=6,paths=len(boundary),forced_paths=len(forced),
        incomplete_constructions=sum(b['status']!='complete' for r in boundary for b in r['builds']),
        by_cap=dict(Counter(r['policy'].split('_')[1] for r in forced)),
        by_build_index=dict(Counter(r['policy'].split('_')[2] for r in forced)),
        fallback_reprices=sum(r['fallback_reprices'] for r in forced),all_three_switches_exact=True)
    result['50_controls']={}
    for method in ('maintain','indexed_full','feature_gate','composed'):
        zs=[r for r in rows if r['stage']==50 and r['phase']=='timing' and r['regime']=='normalized' and r['policy']==method]
        result['50_controls'][method]=dict(inputs=2,median_cpu=statistics.median(sum(r['algorithm_cpu'] for r in zs if r['repeat']==i) for i in range(3)),all_bypass_builds=all(not r['builds'] for r in zs))
    (ROOT/'Summary.json').write_text(json.dumps(result,indent=2)+'\n')
    d=result['stages'];chosen_gate=result['selections']['47'];chosen_budget=result['selections']['48']['budget']
    def performance(stage,method):
        x=d[str(stage)][method];pct=(x['cpu_ratio_to_maintenance']-1)*100
        return f"{abs(pct):.1f}% {'more' if pct>=0 else 'less'} median aggregate CPU than maintenance; {x['paired_wins']} of {x['timing_inputs']} paired inputs faster"
    reduction=(1-d['48']['budget_fixed']['median_cpu']/d['48']['adaptive']['median_cpu'])*100
    lines=[]
    for stage in (46,47,48,50):
        for method,x in d[str(stage)].items():
            lines.append(f"| {stage} | {method} | {x['median_cpu']:.6f} | {x['cpu_ratio_to_maintenance']:.3f} | {x['paired_wins']}/{x['timing_inputs']} |")
    conditions=[]
    for key,x in result['46_timing_conditions'].items():
        conditions.append(f"| {key} | {x['maintain']['median_cpu']:.6f} | {x['indexed_full']['median_cpu']:.6f} | {x['legacy_gate']['median_cpu']:.6f} |")
    text=f'''# Experiments 46–50: findings

All five experiments completed. The 1,020 independently audited workers
cover 110 distinct input records: 444 headline paths, 216 development timing
paths and 360 held timing paths. Every policy reached its declared end, and
**{result['integer_time_checks']:,} integer-time answers** agreed with a separate
capacity dynamic program. Every logical repeat matched.

## What the five experiments found

1. **46 — Size estimates do not encode temporal pace.** On all sixteen
   matched slope-scaling pairs, multiplying slopes by eight left the old
   gcd-adjusted gate bounds and decisions unchanged. The underlying eight
   item/seed groups were held fixed while slopes and observation horizons
   varied. The repeated matched condition timings below show the actual
   costs; the old gate used {performance(46,'legacy_gate')} across the eight
   timing variants. These are two independent seed/item groups with four
   variants each on the timing subset, not eight independent random draws.
2. **47 — A wider gate helped, but the pace filter was not selected.** Development chose
   `{json.dumps(chosen_gate,sort_keys=True)}` from five declared candidates.
   On sixteen held inputs it accepted {d['47']['feature_gate']['accepted']}
   and rejected {d['47']['feature_gate']['rejected']}. On the eight-input
   repeated subset it used {performance(47,'feature_gate')}. The older gate
   used {performance(47,'legacy_gate')}. Choosing the never-build option is
   allowed and still pays feature/gate arithmetic.
   The two pace filters changed the development decisions, but neither beat
   the plain 30,000 threshold on the declared selection criterion. These
   finite samples do not establish a benefit from adding the pace estimate.
3. **48 — Stop-renewing thresholds expose construction debt.** Development
   selected threshold **{chosen_budget}**; zero means never build. The fixed
   4,000-operation rule stopped {d['48']['budget_fixed']['stopped_renewals']}
   renewals on sixteen held inputs and used {reduction:.1f}% less median CPU
   than unconditional doubling windows. Against maintenance it used
   {performance(48,'budget_fixed')}. The selected rule used
   {performance(48,'budget_selected')}. The initial build and fallback proof
   repricing are included in CPU. A threshold checks past construction work
   before the next build; it is not a strict bound on the total cost already paid.
4. **49 — Later forced failures remained safe.** All sixty paths had the
   three intended strict-loss switches. Fifty-four forced failures cover
   entries, index and auxiliary guards, at each of the second, third and
   fourth constructions. Every partial construction was audited and stayed
   inactive. There were {result['stages']['49']['fallback_reprices']} stale
   scalar proof reprices across the forced paths. Tie times and window joins
   are included in the integer-time checks.
5. **50 — Transfer was tested without retuning.** Fresh 16/20-item inputs
   were observed through mathematical time 512. The composed rule used
   {performance(50,'composed')}; the transferred input gate alone used
   {performance(50,'feature_gate')}. Of twenty-four headline inputs,
   {d['50']['composed']['normalized']} were normalized controls and correctly
   bypassed construction. The composed gate accepted
   {d['50']['composed']['accepted']} non-normalized inputs and rejected
   {d['50']['composed']['rejected']}; a selected zero renewal threshold can
   still prevent building after gate acceptance.
   Here the selected zero threshold prevented **every composed construction**.
   The small CPU difference from maintenance cannot be credited to an active
   combination of gate and rolling proofs: it performed maintenance plus
   extra gate decisions, with ordinary timing variation.

## Repeated held CPU

Each number is the median of three sums over the same eight inputs per
experiment. CPU includes gates, renewal decisions, native solves,
cleanup/disposal, construction, scalar maintenance and driver bookkeeping.
It excludes input decoding, serialization and independent auditing. A ratio
below one is faster than maintenance on that finite subset. Paired wins use
each input's own three-repeat median, which differs from aggregate ranking.

| Experiment | Policy | Median CPU seconds | Ratio to maintenance | Paired wins |
|---|---|---:|---:|---:|
{chr(10).join(lines)}

## Matched pace/horizon conditions in 46

Each condition is a median sum over two inputs (12 and 16 items), from three
repeats. Scaling slopes changes which integer times correspond to the same
continuous objectives; it does not create new independent item draws.

| Condition | Maintenance CPU | Full indexed CPU | Old gate CPU |
|---|---:|---:|---:|
{chr(10).join(conditions)}

## Interpretation and evidence

These results extend the 41–45 observation that a reusable proof may save
later maintenance but must first repay construction and renewal costs.
The pace estimate is a heuristic, not a proven profitability condition.
The operation threshold adds determinism to renewal decisions but does not
turn operation counts into equivalent CPU costs. No held-case timing was
used to tune either rule. A selected rule may be less effective after transfer.

Inputs, algorithm sources, caps and roadmap were frozen before training.
Both development selections were sealed before any held worker ran. Smoke
checks used disjoint implementation fixtures. Detailed native/scalar proofs,
repair events, complete or capped frontiers, accounting and independent audits
are in the Drive archive linked by `Archive-storage.json`. Content addressing
stores repeated proof objects once. An interrupted worker restarts cold;
there is no claim of within-action continuation.

All native temporary stores were empty after cleanup/disposal. Independent
checks replay recurrence, deletion and index records; verify scalar covers,
prices, repairs and horizons; and recompute gates and renewal decisions.
The audit-only capacity DP never chooses a policy or supplies a proof to it.

The stage-50 normalized controls are separated in `Summary.json`. Small CPU
differences and three machine-local repeats do not establish statistical
confidence or a universal speedup. Headline denominators are 32 inputs in
46, 16 held inputs in 47/48, 6 chain inputs in 49, and 24 in 50. Timing
denominators are eight per timed stage. Ten conditions on each chain are
dependent views of the same input.

This is exact integer parametric knapsack on the declared finite inputs.
The old lost 36–40 detailed archive remains unavailable; no byte-level
comparison or recovery of that run is claimed.
'''
    (ROOT/'Synthesis.md').write_text(text)

if __name__=='__main__':main()
