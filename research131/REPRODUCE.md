# Recovery and reproducibility

Run `PYTHONDONTWRITEBYTECODE=1 python3 research131/code/verify_publication.py` in the repository for read-only verification of compact files, the compressed archive and every archived member's bytes/hash/mode. Archive-storage.json and Archive-manifest.json identify the evidence. Earlier 121–130 and 111–120 archive verifiers remain valid; no original archive was overwritten.

After verification, safely extract the archive into a new directory using `tarfile.extractall(..., filter='data')`. The `primary/` and `replica/` roots contain preserved source/dependency freezes, fixtures, full results, logs, proofs and independent controls. The `reports/` root contains post-run products. The large external SDKs are excluded and identified by SDK.json; use [121–130 recovery](../research121/REPRODUCE.md) if they are absent. This is a shared-deployment fresh-directory replication, not independent toolchain installation.

In either extracted run root:

```bash
PYTHONDONTWRITEBYTECODE=1 python3 code/audit.py
PYTHONDONTWRITEBYTECODE=1 python3 code/audit_axes.py
```

These are the independent original-model/polygon/kernel-accounting and rank-two audits. They import no producer or admission code. Expected results are 27 original records with 23 valid/false-bound proof pairs, then one rank-two scenario with eleven valid/false-bound proof pairs. The two proof sets are disjoint. The underlying objective is checked in its original two-parameter form before comparison with the integer point encoding.

For a new execution, copy only the frozen source/input/fixture/dependency files plus Freeze.json, Axes-freeze.json and Axes-import-amendment.json into a fresh directory. Preserve executable modes. Check the shared SDK hashes and run serially:

```bash
PYTHONDONTWRITEBYTECODE=1 python3 code/campaign.py
PYTHONDONTWRITEBYTECODE=1 python3 code/audit.py
PYTHONDONTWRITEBYTECODE=1 python3 code/independent_axes_v2.py
PYTHONDONTWRITEBYTECODE=1 python3 code/audit_axes.py
```

The original independent_axes.py intentionally retains its recorded import-order failure; use v2. The C launcher was built with `gcc -O2 -Wall -Wextra -Werror code/wait_account.c -o code/wait_account`. A compiler/platform change can change binary identity; preserve the frozen expected identity and disclose a new deployment rather than silently editing hashes. Linux wait4 reports individual lifetime high-water RSS, with the scope and inherited-launcher history described in Synthesis.md.

The original campaign is capped at 120 wall seconds, 32 MiB evidence and per-checker/producer limits in Protocol.json. The rank-two supplement is a single modest scenario under the same per-proof limits. Replication compares all logical, proof/formula hash, packing, admission and fallback fields; only measurements differ. Summary.json keeps both kernel and sampled measurements. Counts do not merge with preceding evidence sets.

The larger project's illustrative example runs with the Python standard library: `PYTHONDONTWRITEBYTECODE=1 python3 projects/certified-allocation/worked_example.py`. It checks nine scenarios, four invalid controls and 121 rational parameter points using residual potentials and a separate tiny transportation enumerator. This is not an external-proof benchmark or a formally verified checker. Plot regeneration additionally requires Matplotlib and writable `MPLCONFIGDIR`/`XDG_CACHE_HOME`, for example directories under `/workspace/maths-onboarding/`; no home-directory modification or running service is required.
