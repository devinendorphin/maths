# Research import status

## Experiments 31–35: recovered and verified

All eight parts in `handoffs/` were joined with the inspected supplied `reassemble.py` on a GitHub runner. The restored archive is byte-identical to the expected checkpoint:

- Filename: `Temporal-proof-experiments-31-35-campaign.zip`.
- Bytes: 176,127,453.
- SHA256: `656930b55f767e811089a8b345abb1cbf228559dd13afaf4be770d4c7c4f7b9f`.
- All 8,275 manifest members verified; all 8,276 archive files imported.
- Imported member hashes checked again after checkout.
- Frozen entries verified: stage 31: 25; stage 32: 29; stage 33: 30; stage 34: 32; stage 35: 33.
- Both stage-34 retained prior sources verified against the amendment and initial freeze.
- The unchanged nested earlier campaign checksum verified.
- The saved top-level resume file has empty pending lists.

[Recovered campaign](campaigns/experiments-31-35/) and [machine-readable recovery verification](RECOVERY-31-35.json). [Reassembly run](https://github.com/devinendorphin/maths/actions/runs/37216974755) and [imported-source verification run](https://github.com/devinendorphin/maths/actions/runs/37217275719) both succeeded. No archived result or source was rewritten; no experiments or mathematical audits were replayed. Integrity verification is separate from reproducing research findings.

The attachment tool's 32 MiB limit and this workspace's unavailable network proxy initially blocked transfer. Recovery completed through the repository's GitHub runner. The complete original remains reconstructible from its eight preserved parts.

## Experiments 36–40: documents retained, campaign unavailable

The original [handoff](handoffs/Temporal-proof-experiments-36-40-handoff.md) and [three result documents](results/experiments-36-40/) are preserved unchanged. The handoff's SHA256 is `e63a9a21e845782d8e2a529abb263eb6e6e1ed638c2e2fccf607b392b61ebc4f` (38,078 bytes).

The user has directed that the 36–40 source code and detailed evidence be treated as unavailable due to technical difficulties. Their supplied verification report describes `Temporal-proof-experiments-36-40-campaign-verified.tar.xz`, 490,898,512 bytes, SHA256 `a2360b92cfa4df79b33c0107df674f2d54639d0c4dfb28f11392651ae18dec82`. That archive was not recovered; its verification claims and the synthesis's findings are retained prior-run reports only. Resume references into that archive are not executable checkpoints in this repository.

Use the recovered 31–35 source as the baseline for future work. Keep any new work in a separate directory and distinguish it from the unavailable prior 36–40 implementation.
