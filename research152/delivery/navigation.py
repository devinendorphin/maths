"""Preserve original navigation seals and extend historical receipt verification."""
import copy
import hashlib
import json
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1];REPO=ROOT.parent
ANCESTORS=('research111/repairs','research121','research131','research133','research137','research141','research145','research148')


def info(data):return {'bytes':len(data),'sha256':hashlib.sha256(data).hexdigest()}


def run():
    assert not (ROOT/'Navigation-amendment.json').exists()
    old=(REPO/'README.md').read_bytes();(ROOT/'README-df734ad.md').write_bytes(old)
    for name in ANCESTORS:
        p=REPO/name/'Publication-seal.json';backup=p.with_name('Publication-seal-df734ad.json');assert not backup.exists();backup.write_bytes(p.read_bytes())
    helper=REPO/'research148/delivery/verify_publication.py';original=helper.read_bytes()
    saved=helper.with_name('verify_publication-df734ad.py');saved.write_bytes(original)
    text=original.decode();needle="        old=(REPO/entry['preserved']).read_bytes();current=(REPO/entry['path']).read_bytes()\n"
    replacement=needle+"        # Later sealed navigation retains the exact earlier receipt endpoint.\n        if hashlib.sha256(current).hexdigest()!=entry['after']['sha256']:\n            path=Path(entry['path'])\n            matches=[(REPO/name).read_bytes() for name in seal['files']\n                     if Path(name).parent==path.parent and Path(name).name.startswith('Publication-seal-')\n                     and hashlib.sha256((REPO/name).read_bytes()).hexdigest()==entry['after']['sha256']]\n            assert len(matches)==1;current=matches[0]\n"
    assert text.count(needle)==1;helper.write_text(text.replace(needle,replacement))
    text=old.decode();needle='The latest continuation, [experiments 148–151]';assert text.count(needle)==1
    paragraph=('The latest continuation, [experiments 152–155](research152/Synthesis.md), implements and measures a credited specialist incremental optimizer across costs, capacities, needs and lower bounds. Each of two fresh directories completed 72 workers and 3,528 certified observations. The audit checks actual retained residual flows, remaining node imbalances, object/solve counts, shortage recovery and complete proof/journal replication. The [findings](research152/Synthesis.md) report complete-session and query-only costs separately; the [roadmap](research152/Roadmap.md) carries the measured boundary forward. This is inspected residual-flow state reuse; upstream potentials reset at each solve.\n\n')
    text=text.replace(needle,paragraph+'The preceding continuation, [experiments 148–151]',1)
    text=text.replace('- `research148/`:','- `research152/`: specialist incremental state, external feasibility admission, matched SDK baselines and independent state audit. [Findings](research152/Synthesis.md), [roadmap](research152/Roadmap.md), [recovery](research152/REPRODUCE.md).\n- `research148/`:',1)
    (REPO/'README.md').write_text(text)
    amendments=[]
    for name in ANCESTORS:
        path=REPO/name/'Publication-seal.json';before=path.read_bytes();body=json.loads(before);targets=['README.md']
        targets += [r+'/Publication-seal.json' for r in ANCESTORS if r+'/Publication-seal.json' in body['files']]
        if name=='research148':
            targets += [str(helper.relative_to(REPO)),str(saved.relative_to(REPO))]
            targets += [r+'/Publication-seal-df734ad.json' for r in ANCESTORS[:-1]]
        changes={}
        for target in targets:
            previous=body['files'].get(target);fresh=info((REPO/target).read_bytes());new=fresh['sha256'] if type(previous) is str else fresh
            if previous!=new:changes[target]={'old':previous,'new':new};body['files'][target]=new
        after=(json.dumps(body,sort_keys=True,indent=2)+'\n').encode();path.write_bytes(after)
        amendments.append({'path':str(path.relative_to(REPO)),'preserved':str(path.with_name('Publication-seal-df734ad.json').relative_to(REPO)),
                           'before':info(before),'after':info(after),'changed_entries':changes})
    receipt={'baseline_commit':'df734ada2a5025bd01dd558b33c959175165e3b7','readme':{'preserved':'research152/README-df734ad.md','before':info(old),'after':info((REPO/'README.md').read_bytes())},
             'scope':'Current README/dependent seal navigation only, plus a delivery-only 148 verifier amendment that verifies original receipt endpoints using byte-preserved sealed snapshots. Scientific sources/freezes/archives unchanged.',
             'delivery_helper':{'path':str(helper.relative_to(REPO)),'preserved':str(saved.relative_to(REPO)),'before':info(original),'after':info(helper.read_bytes())},'amendments':amendments}
    (ROOT/'Navigation-amendment.json').write_text(json.dumps(receipt,sort_keys=True,indent=2)+'\n');print('Preserved',len(amendments),'navigation seals and original delivery verifier')


if __name__=='__main__':run()
