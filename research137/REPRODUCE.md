# Inspect, recover and repeat

Run `PYTHONDONTWRITEBYTECODE=1 python3 research137/code/verify_publication.py`
from the repository first. This standard-library verifier checks compact seals,
every archive member and all 3,900 headline certificates across the two accepted
directories, including altered-cost rejection and terminal recovery. The archive
contains primary/, replica/, reports/ and rejected-custody/. The rejected directory
has four inconsistent raw journals and must not be passed off as an accepted run.

Extract into a new directory only after verification, using Python tarfile with
`filter='data'`. Do not overwrite archived evidence or rerun a campaign in an
already populated directory. Archive-storage.json binds the compressed bytes;
Archive-manifest.json binds every member, its mode and its bytes.

The measured environment is Freeze.json: Python 3.12.14, NetworkX 3.4.2 and a
specified official network-simplex source hash. A fresh venv was installed for
this continuation. To reproduce, create a venv outside Git, install the pinned
version with verified TLS (`pip install networkx==3.4.2`), and verify version,
Python build and module hash against Freeze.json. The archived installed primary
module source is also preserved for inspection. Setup cost is outside repeated
session totals; primary and replica share this environment. A different build
requires a new explicit context, not a claim of identical historical identities.

To re-audit retained copies, run each extracted primary/code/audit.py and
replica/code/audit.py with that environment. Expected per directory: 78 workers,
1,950 queries, 150 distinct models, 175 headline proof identities, 887 invalid
certificate controls, 12 transaction controls, ten recovery controls and three
non-cost cases. Expected accepted delta records: 805; forced compactions: 115.
All audit outputs are written into the extracted copies, preserving the archive.

To execute afresh, copy ONLY each file named by Freeze.json plus Freeze.json into
two new empty directories. Verify those hashes; run code/campaign.py and then
code/audit.py in each directory. Run the published code/summarize.py with those
two paths and a new report directory. Its supplemental full-field comparison
checks exact jobs, all meaningful Worker/Sessions fields and all mathematical,
raw-log, checkpoint and control identities. It excludes only the measured
timing/CPU/RSS fields listed in Replication.json and retains both measurement sets.

On this machine each campaign used roughly 29–32 summed worker-wall seconds;
each audit took roughly 17–18 seconds. These are observations, not promises.
The frozen worker guards are 60 seconds and 512 MiB; failed/timed-out work is
retained and stops the campaign. Earlier caps and source freezes remain intact.

During the first workspace execution four raw journal sizes failed the custody
check, despite successful workers. Their saved bytes are retained. No causal
claim about that corruption is established. The accepted repetitions used new
run directories under /tmp, then verified and packaged their complete evidence.
Do not combine timings or silently repair the rejected raw journals.

Only delta-fsync requests file/directory fsync. Correct replay and atomic rename
were tested; actual power-loss behavior and hardware persistence were not.
The live serialized delta budget does not bound the admitted base, Python heap
or retained raw evidence file. Recovery requires a trusted terminal anchor for
rollback detection and a complete trusted change source for authoritative truth.

Prior archive checks remain available at research133/code/verify_publication.py,
research131/code/verify_publication.py, research121/code/verify_publication.py,
research111/repairs/code/verify_publication.py and scripts/verify_compact.py.
README navigation changes only update the current seals' README entry; original
seal bytes and the old README are preserved and this amendment is recorded.
