"""Bounded public dependency setup; all payloads stay outside the Git working set."""
import hashlib,json,pathlib,subprocess,time,urllib.request,tarfile
ROOT=pathlib.Path('/workspace/maths/research101');BASE=pathlib.Path('/workspace/maths-toolchains/batch101');BASE.mkdir(parents=True,exist_ok=True)
start=time.monotonic();log=[];opener=urllib.request.build_opener(urllib.request.ProxyHandler({'https':'http://proxy:8080'}))
def run(args,timeout,env=None):
 p=subprocess.run(args,capture_output=True,text=True,timeout=timeout,env=env);log.append(dict(args=args,code=p.returncode,stdout=p.stdout[-4000:],stderr=p.stderr[-2000:]));return p
receipt=dict(wall_cap=240,status='partial',sources={},tools_root=str(BASE))
try:
 p=run(['python3','-m','pip','install','--disable-pip-version-check','--no-deps','--target',str(BASE/'python'),'--proxy','http://proxy:8080','pyscipopt==6.0.0','pybind11==2.13.6','Cython==0.29.37','cmake==3.31.6'],120)
 receipt['python_dependencies_installed']=p.returncode==0
 for name,repo,commit in [('cp2024','ciaranm/cp2024-dynamic-programming-supplement','9b915e8e959e07ed2c096582c3dcb605ce0269e7'),('veripb','StephanGocht/VeriPB','01b7b5088c8a67f1611427174501191bc5f5b365')]:
  url=f'https://codeload.github.com/{repo}/tar.gz/{commit}';body=opener.open(url,timeout=30).read(32*1024**2+1)
  if len(body)>32*1024**2:raise ValueError('dependency archive cap')
  f=BASE/(name+'.tar.gz');f.write_bytes(body)
  with tarfile.open(f,'r:gz') as t:t.extractall(BASE/name,filter='data')
  folder=next((BASE/name).iterdir());receipt['sources'][name]=dict(repository=repo,commit=commit,url=url,archive_sha256=hashlib.sha256(body).hexdigest(),archive_bytes=len(body),folder=str(folder))
 receipt['status']='downloaded'
except Exception as e:receipt['reason']=str(e)
receipt['wall']=time.monotonic()-start;receipt['commands']=log
(ROOT/'Dependency-setup.json').write_text(json.dumps(receipt,indent=2)+'\n');print(json.dumps({k:v for k,v in receipt.items() if k!='commands'}),flush=True)
