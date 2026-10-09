import hashlib
import json
from pathlib import Path
import shutil
import sys

ROOT=Path(__file__).resolve().parents[1]
binary=Path('/workspace/maths-toolchains/repair-sdk/vipr_hold')
files={name:hashlib.sha256((ROOT/name).read_bytes()).hexdigest() for name in ['Memory-amendment.json','Inputs.json','code/vipr_hold.cpp','code/memory_repair.py','code/memory_observer.py','code/audit_memory.py','code/memory.py','code/core.py']}
freeze=dict(files=files,binary_sha256=hashlib.sha256(binary.read_bytes()).hexdigest(),headline_started=False)
(ROOT/'Memory-freeze.json').write_text(json.dumps(freeze,indent=2)+'\n')
for destination in sys.argv[1:]:
    target=Path(destination)
    for name in list(files)+['Memory-freeze.json']:
        p=target/name;p.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(ROOT/name,p)
