import hashlib
import json
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
REPO=ROOT.parent
pb=json.loads((REPO/'research111/recovery/Checker-setup.json').read_text())
frozen=json.loads((REPO/'research111/recovery/Replay-freeze.json').read_text())
sdk=Path('/workspace/maths-toolchains/repair-sdk')
files={str(Path(pb['source'])/name):digest for name,digest in frozen['official_python_sources'].items()}
files.update({str(Path(pb['source'])/name):digest for name,digest in pb['binaries'].items()})
for p in [Path(pb['python']),sdk/'scip-build/bin/scip',sdk/'vipr-build-compatible/viprcomp',sdk/'vipr_fork']:
    files[str(p)]=hashlib.sha256(p.read_bytes()).hexdigest()
for name,digest in files.items():assert hashlib.sha256(Path(name).read_bytes()).hexdigest()==digest,name
data=dict(pb_source=pb['source'],pb_python=pb['python'],exact_scip=str(sdk/'scip-build/bin/scip'),completion=str(sdk/'vipr-build-compatible/viprcomp'),files=files,
    cp_commit='9b915e8e959e07ed2c096582c3dcb605ce0269e7',veripb_commit='5c485722194cbd9422d3eb169c8e621ca82aeb17',
    pb_deployment='official optimized core + unchanged interpreted checking rules; distinct from recovered fifteen-extension timing deployment',independent_sdk_installation=False)
data['identity']=hashlib.sha256(json.dumps(data,sort_keys=True,separators=(',',':')).encode()).hexdigest()
(ROOT/'SDK.json').write_text(json.dumps(data,indent=2)+'\n')
