# Roadmap: experiments 46–50

The 41–45 campaign found a small gate benefit on one sample, reduced repeated
work with growing windows, and correct fallback after a stopped second build.
The gate benefit did not transfer to the growing-window policy on fresh inputs.
This batch investigates those limitations, with new inputs and the same
independent proof checks. The roadmap is included in the pre-run freeze.

| Experiment | Question | Design | Evidence that matters |
|---|---|---|---|
| 46 | What changes when values evolve faster or we look farther ahead? | Eight matched item/seed groups, slopes multiplied by 1 or 8, horizons 64 or 256; maintenance, full indexed proof and old gate. | Paired CPU/work changes. Common slope scaling leaves the old gate's gcd-adjusted bound unchanged. The 32 variants are not 32 independent draws. |
| 47 | Can an input-only pace estimate improve the gate? | Five predeclared candidates, eight development inputs, then sixteen held inputs. Pace uses horizon × slope magnitude divided by profit magnitude. | Sealed development choice, both acceptance and rejection counts, and held timing versus maintenance and the old gate. |
| 48 | Does stopping renewal avoid repeated construction debt? | Four development thresholds; compare maintenance, growing windows, a fixed 4,000-operation threshold and the selected threshold. | CPU including the already-paid first build and fallback repricing. The threshold controls the next renewal, not a strict total cost guarantee. |
| 49 | Is fallback safe after later stopped builds and several answer changes? | Six four-item chains, three successive losses, normal rolling proof plus nine forced-cap conditions per input. | Correct answers and switch times; independently audited entries/index/auxiliary cap cursors at second, third and fourth builds. |
| 50 | Do the chosen rules transfer to larger, longer cases? | Twenty-four entirely fresh 16/20-item inputs through time 512, including normalized controls. | Gate and renewal selections transferred without retuning; performance and correctness, with controls shown separately. |

The frozen set has 110 distinct input records: 16 development inputs and 94
held inputs. It has 444 headline paths, 216 development timing workers and
360 held timing workers (1,020 workers total). Each selected rule is sealed
before any held-case computation. Three repeats rotate method order.

The exact algorithms optimize an integer parametric knapsack objective.
Mathematical time is not wall-clock time. Independent capacity DP answers are
audit-only and cannot guide gates, renewal choices or native solves.

Caps are fixed before execution. Incomplete proof constructions remain
inactive; the scalar fallback must still prove all recorded answers. A
negative timing result is useful evidence, and will not be hidden or tuned
away using held cases. This is a finite experiment, not a universal theorem.

GitHub retains sources, inputs, selections and small reports. Detailed
content-addressed proof objects and audited workers go to the selected Drive,
followed by a download and archive-member verification.
