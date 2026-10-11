"""One-time navigation-only amendment with byte-preserved predecessor receipts."""
import copy
import hashlib
import json
from pathlib import Path
import re

ROOT=Path(__file__).resolve().parents[1];REPO=ROOT.parent
ANCESTORS=('research111/repairs','research121','research131','research133','research137','research141','research145')


def info(data):return {'bytes':len(data),'sha256':hashlib.sha256(data).hexdigest()}


def run():
    receipt=ROOT/'Navigation-amendment.json';assert not receipt.exists()
    readme=REPO/'README.md';old=readme.read_bytes();(ROOT/'README-84d7c8f.md').write_bytes(old)
    for name in ANCESTORS:
        path=REPO/name/'Publication-seal.json';backup=path.with_name('Publication-seal-84d7c8f.json')
        assert not backup.exists();backup.write_bytes(path.read_bytes())
    text=old.decode()
    paragraph=('The latest continuation, [experiments 148–151](research148/Synthesis.md), extends the larger changing-allocation inquiry to transactional capacity, need and lower-bound updates. Each of two directories completed 48 workers and 1,200 certified observations, including 240 shortage cuts and 48 recoveries from cuts; all 150 model outcomes, 239 distinct proofs, controls and raw journals reproduce. Retained primal-flow repair is correct within the frozen interface, but the native cold solver is faster on cyclic cases and full certificate guards add overhead. The [next roadmap](research148/Roadmap.md) therefore targets actual specialist incremental optimizer state. This stage does not claim noncost spanning-tree maintenance or a general speed advantage.\n\n')
    old_latest='The latest continuation, [experiments 145–147]'
    assert text.count(old_latest)==1
    text=text.replace(old_latest,paragraph+'The preceding continuation, [experiments 145–147]',1)
    working='- `research145/`:';assert text.count(working)==1
    text=text.replace(working,'- `research148/`: transactional noncost changes, checked primal repair, native cold comparison and exact replication. [Findings](research148/Synthesis.md), [roadmap](research148/Roadmap.md), [recovery](research148/REPRODUCE.md).\n'+working,1)
    readme.write_text(text)
    amendments=[]
    for name in ANCESTORS:
        path=REPO/name/'Publication-seal.json';before=path.read_bytes();body=json.loads(before);changed={};new_text=before.decode()
        targets=['README.md']+[r+'/Publication-seal.json' for r in ANCESTORS if r+'/Publication-seal.json' in body['files']]
        for target in targets:
            previous=body['files'][target];fresh=info((REPO/target).read_bytes());new=fresh['sha256'] if type(previous) is str else fresh
            if previous==new:continue
            pattern=r'"'+re.escape(target)+r'":\s*(?:\{[^}]*\}|"[^"]*")'
            def amend(match):
                entry=match[0];old_hash=previous if type(previous) is str else previous['sha256']
                assert entry.count(old_hash)==1;entry=entry.replace(old_hash,fresh['sha256'])
                if type(previous) is dict:
                    entry,n=re.subn(r'("bytes":\s*)'+str(previous['bytes'])+r'\b',lambda m:m[1]+str(fresh['bytes']),entry)
                    assert n==1
                return entry
            new_text,n=re.subn(pattern,amend,new_text);assert n==1
            changed[target]={'old':previous,'new':new};body['files'][target]=copy.deepcopy(new)
        after=new_text.encode();assert json.loads(after)==body
        path.write_bytes(after)
        amendments.append({'path':str(path.relative_to(REPO)),'preserved':str(path.with_name('Publication-seal-84d7c8f.json').relative_to(REPO)),
                           'before':info(before),'after':info(after),'changed_entries':changed})
    receipt.write_text(json.dumps({'baseline_commit':'84d7c8f1395b8fcf76960789e93fa2ba0dc402bf',
                                   'readme':{'preserved':'research148/README-84d7c8f.md','before':info(old),'after':info(readme.read_bytes())},
                                   'scope':'Only current README navigation and existing dependent seal entries. All other seal fields and prior scientific evidence unchanged.',
                                   'amendments':amendments},sort_keys=True,indent=2)+'\n')
    print('Preserved and amended',len(amendments),'navigation seals')


if __name__=='__main__':run()
