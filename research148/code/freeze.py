"""Create once, before any headline execution; no post-hoc source edits."""
import hashlib
import json
from pathlib import Path
from checker import encode
from environment import capture
from suite import make

ROOT=Path(__file__).resolve().parents[1]


def run():
    assert not (ROOT/'Freeze.json').exists() and not (ROOT/'outputs').exists()
    (ROOT/'Inputs.json').write_text(json.dumps(make(),sort_keys=True,indent=2)+'\n')
    files=sorted(ROOT.glob('code/*.py'))+[ROOT/p for p in ('Protocol.md','Development.json','Inputs.json','Requirements.txt','Sources.md',
                                                         'Upstream-min_cost_flow.h','Upstream-min_cost_flow.cc','Upstream-OR-Tools-LICENSE.txt')]
    body={'files':{str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in files},
          'environment':capture(),'predecessor':'84d7c8f1395b8fcf76960789e93fa2ba0dc402bf','headline_not_executed_at_freeze':True}
    body['context']=hashlib.sha256(encode(body)).hexdigest()
    (ROOT/'Freeze.json').write_text(json.dumps(body,sort_keys=True,indent=2)+'\n');print(body['context'])


if __name__=='__main__':run()
