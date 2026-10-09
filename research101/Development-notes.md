# Development and execution record

DP/SCIP smoke on a three-variable signed model passed before the first execution attempt. The packaged SCIP exact-mode probe reported that exact solve support was absent.

The first frozen execution attempt aborted in experiment 108: the zero-capacity fixture requested restriction to zero, which is an unchanged model and correctly admitted its old certificate. The experiment incorrectly required rejection. Corrected the driver to test only changed capacities; unchanged admission remains covered by 101. No results from the aborted attempt enter the completed headline dataset. The original attempted source, freeze and log are retained in the evidence archive. Refroze the corrected design without changing mathematical inputs or intended hypotheses.
