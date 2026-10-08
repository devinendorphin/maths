"""Bounded, digest-checked standalone Lean setup outside the research repository."""
import hashlib, json, pathlib, subprocess, time, urllib.request
start=time.monotonic()
root=pathlib.Path('/workspace/maths-toolchains'); root.mkdir(exist_ok=True)
archive=root/'lean-4.24.0-linux.tar.zst'
receipt=pathlib.Path('/workspace/maths/research96/Lean-setup.json')
url='https://github.com/leanprover/lean4/releases/download/v4.24.0/lean-4.24.0-linux.tar.zst'
expected='b14f5e5159219dd1a1956c3b806813319f5e94ccd5bdfd56f54520609a5bb5ec'
r=dict(version='4.24.0',url=url,expected_sha256=expected,wall_cap=300,download_bytes_cap=512*1024**2,status='unavailable',bytes=0)
try:
 opener=urllib.request.build_opener(urllib.request.ProxyHandler({'https':'http://proxy:8080'}))
 h=hashlib.sha256()
 with opener.open(url,timeout=30) as response,archive.open('wb') as out:
  while True:
   if time.monotonic()-start>300:raise TimeoutError('Lean setup wall cap')
   b=response.read(1024*1024)
   if not b:break
   r['bytes']+=len(b)
   if r['bytes']>r['download_bytes_cap']:raise ValueError('Lean download byte cap')
   h.update(b);out.write(b)
 r['actual_sha256']=h.hexdigest();assert h.hexdigest()==expected
 subprocess.run(['tar','--zstd','-xf',str(archive),'-C',str(root),'--wildcards','lean-4.24.0-linux/bin/lean','lean-4.24.0-linux/lib/lean/*'],check=True,timeout=max(1,300-(time.monotonic()-start)))
 binary=root/'lean-4.24.0-linux/bin/lean'
 out=subprocess.run([str(binary),'--version'],capture_output=True,text=True,check=True,timeout=10)
 r.update(status='available',binary=str(binary),version_output=out.stdout.strip(),binary_sha256=hashlib.sha256(binary.read_bytes()).hexdigest())
except Exception as e:r['reason']=str(e)
r['setup_wall']=time.monotonic()-start;receipt.write_text(json.dumps(r,indent=2)+'\n');print(json.dumps(r),flush=True)
