# Experiments 137–140: sparse updates with charged recovery

The continuation implements the previously conditional sparse-delta path and
tests complete costs on six synthetic networks up to 128 nodes and 4,096 edges.
Read [Synthesis.md](Synthesis.md), [Protocol.md](Protocol.md),
[Mathematical-contract.md](Mathematical-contract.md), [Alignment.md](Alignment.md)
and [REPRODUCE.md](REPRODUCE.md).

Each accepted directory completed 78 workers, 1,950 observations and 887 invalid
certificate controls, with exact mathematical/log/checkpoint replication. The
largest case used about 37–38% less median session wall time than fresh solving
on the buffered delta route, but its raw journal was about twice as large.
Small-network comparisons remain mixed. Trusted complete updates and persistent
plan handles are explicit assumptions. This is not a fairness or deployment claim.
