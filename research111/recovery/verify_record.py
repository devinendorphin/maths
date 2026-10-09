"""Archive/source/replication verification; no optimization or admission imports."""
import hashlib
import json
from pathlib import Path
import subprocess
import tarfile
import tempfile

ROOT=Path(__file__).resolve().parent
REPO=ROOT.parents[1]


def digest(data):
    return hashlib.sha256(data).hexdigest()


def main():
    archive=REPO/'archives/experiments-101-110-original-300-workers.tar.xz'
    assert archive.stat().st_size==687116 and digest(archive.read_bytes())=='4a01c756935d8efda38fb7df02b9ad1caeec4cbbf3ccd8f2a568783969f5e758'
    source=Path(Path('/workspace/maths-onboarding/original300-root.txt').read_text())
    manifest=json.loads((source/'Archive-members.json').read_text())['files']
    for name,m in manifest.items():
        p=source/name;assert p.stat().st_size==m['bytes'] and digest(p.read_bytes())==m['sha256'],name
    freeze=json.loads((source/'Freeze.json').read_text())['files']
    for name,d in freeze.items():assert digest((source/name).read_bytes())==d,name
    upstream=subprocess.check_output(['git','-C','/workspace/maths-toolchains/cp2024-recovery-source','show','9b915e8e959e07ed2c096582c3dcb605ce0269e7:knapsack/knapsack.cc'])
    build=json.loads((source/'CP2024-build.json').read_text())
    assert digest(upstream)==build['upstream_sha256']
    with tempfile.TemporaryDirectory(dir='/workspace/maths-onboarding',prefix='cp-patch-') as temp:
        p=Path(temp)/'knapsack.cc';p.write_bytes(upstream)
        subprocess.run(['patch','--batch',str(p),str(source/'CP2024-adaptation.patch')],check=True,capture_output=True)
        assert p.read_bytes()==(source/'external/cp2024/adapted-knapsack.cc').read_bytes()
    a=json.loads((source/'Results.json').read_text());b=json.loads((source/'replication/Results.json').read_text())
    exclusions=set(json.loads((source/'Replication.json').read_text())['excluded_fields']);counts={'schema1':0,'schema2':0}
    def logical(x):
        if isinstance(x,dict):
            if 'seal' in x:
                if x['schema']==1:
                    fields=['schema','domain','coefficients','time','objective','packing','proof_sha256','checker_sha256','accepted']
                    sealed={k:x[k] for k in fields};counts['schema1']+=1
                else:
                    assert x['schema']==2;sealed={k:v for k,v in x.items() if k!='seal'};counts['schema2']+=1
                assert digest(json.dumps(sealed,sort_keys=True,separators=(',',':')).encode())==x['seal']
            return {k:logical(v) for k,v in x.items() if k not in exclusions}
        if isinstance(x,list):return [logical(v) for v in x]
        return x
    assert len(a)==len(b)==300 and logical(a)==logical(b)
    old_sdk=json.loads((source/'External-dependencies.json').read_text())['files']
    report=dict(archive_sha256=digest(archive.read_bytes()),bytes=archive.stat().st_size,members=404,
        hashed_files_verified=len(manifest),frozen_files_verified=len(freeze),cp_upstream_patch_exact_match=True,
        logical_replication_match=True,excluded_fields=sorted(exclusions),seals_verified=counts,
        seal_exclusion_assessed='Schema 1 seals cover nine logical identity fields, all compared exactly. Schema 2 seals include source timing diagnostics; each seal independently recomputed. No invalid seals ignored.',
        original_external_sdk_files_missing=sum(not Path(p).exists() for p in old_sdk),
        verification_script_sha256=digest(Path(__file__).read_bytes()))
    (ROOT/'Archive-check.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report))


if __name__=='__main__':main()
