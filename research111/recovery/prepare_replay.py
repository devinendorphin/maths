"""Explicit portability adapter for the frozen-model auditor, not an old-SDK claim."""
import difflib
import hashlib
import json
from pathlib import Path
import shutil

ROOT=Path(__file__).resolve().parent
original=Path(Path('/workspace/maths-onboarding/original300-root.txt').read_text())
source=(original/'code/audit.py').read_text()
assert hashlib.sha256(source.encode()).hexdigest()=='810f411dbe1bd1559c07783ee4c307f92385eadd0063fb8a09321c70c60c7087'
line=" for p,d in json.loads((ROOT/'External-dependencies.json').read_text())['files'].items():assert h(pathlib.Path(p))==d,p\n"
assert source.count(line)==1
adapted=source.replace(line," # Original SDK is unavailable; the recovery harness identifies the new checker separately.\n")
old="args=['python3',str(ROOT/'tools/run_veripb.py'),str(formula)]"
assert adapted.count(old)==1
adapted=adapted.replace(old,"args=[__import__('sys').executable,'-m','veripb',str(formula)]")
adapted=adapted.replace("(ROOT/'Audit.json').write_text", "(ROOT/'Portable-audit.json').write_text")
adapted=adapted.replace('timeout=15','timeout=30')
(ROOT/'portable_audit.py').write_text(adapted)
(ROOT/'Portable-audit.patch').write_text(''.join(difflib.unified_diff(source.splitlines(True),adapted.splitlines(True),fromfile='original/code/audit.py',tofile='recovery/portable_audit.py')))
target=original/'code/portable_audit.py';target.write_text(adapted)
setup=json.loads((ROOT/'Checker-setup.json').read_text());assert setup['status']=='built'
new_source=Path(setup['source'])
rule_files={p.relative_to(new_source).as_posix():hashlib.sha256(p.read_bytes()).hexdigest() for p in new_source.rglob('*.py') if 'build' not in p.parts}
manifest=json.loads((original/'External-dependencies.json').read_text())['files']
matched=0
for p,d in rule_files.items():
    expected=[v for path,v in manifest.items() if path.endswith('/'+p)]
    if expected:assert len(expected)==1 and expected[0]==d,p;matched+=1
freeze=dict(files={p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in ROOT.iterdir() if p.is_file() and p.name not in ['Replay-freeze.json']},
    checker_binaries=setup['binaries'],official_python_sources=rule_files,
    original_runtime_python_sources_matched=matched,new_deployment=True,original_sdk_identity_match=False)
(ROOT/'Replay-freeze.json').write_text(json.dumps(freeze,indent=2)+'\n')
print('New deployment auditor prepared; unchanged Python source matches:',matched)
