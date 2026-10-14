"""Once-only accounting freeze, before either headline execution."""
import hashlib
import json
from pathlib import Path
import sys
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'vendor'))
from checker import encode
from environment import capture


def run():
    assert not (ROOT / 'Freeze.json').exists() and not (ROOT / 'outputs').exists()
    files = [p for directory in ('code', 'vendor') for p in sorted((ROOT / directory).glob('*')) if p.suffix in ('.py', '.cc')]
    files += [ROOT / name for name in ('Protocol.md', 'Sources.md', 'Requirements.txt', 'Inputs.json',
        'Development-Audit.json', 'Development-Logical.json', 'Accounting-controls.json', 'Native-controls.json', 'Old-custody.json', 'Rejected-execution.json', 'Build.json', 'bridge.so',
        'Upstream-min_cost_flow.h', 'Upstream-min_cost_flow.cc', 'Upstream-OR-Tools-LICENSE.txt')]
    body = {'files': {str(p.relative_to(ROOT)): hashlib.sha256(p.read_bytes()).hexdigest() for p in files},
            'environment': capture(), 'predecessor': 'b01ecf337414ddb80854e83774a3a36d5bbf362f',
            'headline_not_executed_at_freeze': True, 'inputs_reused_from_152_explicitly': True}
    body['context'] = hashlib.sha256(encode(body)).hexdigest()
    (ROOT / 'Freeze.json').write_text(json.dumps(body, sort_keys=True, indent=2) + '\n')
    print(body['context'])


if __name__ == '__main__':
    run()
