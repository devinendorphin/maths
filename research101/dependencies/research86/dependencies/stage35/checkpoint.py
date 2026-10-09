"""Ordered stage checkpoint packaging and supported persistent upload."""
import json,zipfile,hashlib,subprocess,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];DEL=ROOT.parent/'deliverables';HELPER=Path('/root/.codex/plugins/cache/openai-curated-remote/openai-library/0.1.61/skills/library/scripts/library_upload.py')
def package(stage):
 DEL.mkdir(exist_ok=True);target=DEL/f'Temporal-proof-stage-{stage}-checkpoint.zip'
 paths=[p for p in ROOT.rglob('*') if p.is_file() and '__pycache__' not in p.parts and ('stages' not in p.parts or str(stage) in p.parts)]
 manifest={str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in paths}
 with zipfile.ZipFile(target,'w',zipfile.ZIP_DEFLATED,compresslevel=6) as z:
  for p in paths:z.write(p,'research/'+str(p.relative_to(ROOT)))
  z.writestr('Checkpoint-manifest.json',json.dumps(manifest,indent=2))
 return target
if __name__=='__main__':
 stage=int(sys.argv[1]);target=package(stage)
 req={'uploads':[{'local_path':str(target),'purpose':'create_library_file','library_artifact_type':'other'}]}
 proc=subprocess.run([sys.executable,str(HELPER)],input=json.dumps(req),text=True,capture_output=True)
 (DEL/f'stage{stage}-save-result.json').write_text(proc.stdout)
 if proc.returncode:raise RuntimeError('Checkpoint upload failed: '+proc.stderr)
 result=json.loads(proc.stdout);assert result.get('results') and all(x.get('status') in ('succeeded','success','saved') or x.get('library_file_id') for x in result['results']), result
 print('CHECKPOINT SAVED',stage,target.name,target.stat().st_size,flush=True)
