"""Keep original seal formatting; change only receipted values/additions."""
import hashlib
import json
from pathlib import Path
import re

ROOT=Path(__file__).resolve().parents[1];REPO=ROOT.parent


def info(data):return {'bytes':len(data),'sha256':hashlib.sha256(data).hexdigest()}


def run():
    receipt_path=ROOT/'Navigation-amendment.json';receipt=json.loads(receipt_path.read_text())
    for entry in receipt['amendments']:
        text=(REPO/entry['preserved']).read_text();expected=json.loads(text);extra={}
        for name,change in entry['changed_entries'].items():
            fresh=info((REPO/name).read_bytes());old=change['old'];new=fresh['sha256'] if type(old) is str else fresh
            change['new']=new;expected['files'][name]=new
            if old is None:extra[name]=new;continue
            pattern=r'"'+re.escape(name)+r'":\s*(?:\{[^}]*\}|"[^"]*")'
            def amend(match):
                value=match[0];sha=old if type(old) is str else old['sha256'];assert value.count(sha)==1
                value=value.replace(sha,fresh['sha256'])
                if type(old) is dict:
                    value,n=re.subn(r'("bytes":\s*)'+str(old['bytes'])+r'\b',lambda m:m[1]+str(fresh['bytes']),value);assert n==1
                return value
            text,n=re.subn(pattern,amend,text);assert n==1
        if extra:
            match=re.search(r'"files":\s*',text);_,end=json.JSONDecoder().raw_decode(text,match.end())
            line_start=text.rfind('\n',0,end-1)+1
            lines=json.dumps(extra,sort_keys=True,indent=2).splitlines()[1:-1]
            fragment='\n'.join('  '+line for line in lines)
            text=text[:line_start].rstrip('\n')+',\n'+fragment+'\n'+text[line_start:]
        assert json.loads(text)==expected
        data=text.encode();(REPO/entry['path']).write_bytes(data);entry['after']=info(data)
    receipt_path.write_text(json.dumps(receipt,sort_keys=True,indent=2)+'\n');print('Preserved original seal ordering/whitespace outside receipted edits')


if __name__=='__main__':run()
