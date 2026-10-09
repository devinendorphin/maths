#!/usr/bin/env bash
set -euo pipefail
export PYTHONDONTWRITEBYTECODE=1
mkdir -p /workspace/maths-onboarding/allocation-downloads
if ! test -x /workspace/maths-toolchains/allocation-venv/bin/python; then
  python3 -m venv /workspace/maths-toolchains/allocation-venv
fi
python3 - <<'PY'
import hashlib,json,pathlib,urllib.request
wheel=pathlib.Path('/workspace/maths-onboarding/allocation-downloads/networkx-3.4.2-py3-none-any.whl')
expected='df5d4365b724cf81b8c6a7312509d0c22386097011ad1abe274afd5e9d3bbc5f'
if not wheel.exists():
 metadata=json.load(urllib.request.urlopen('https://pypi.org/pypi/networkx/3.4.2/json',timeout=30))
 entry=next(e for e in metadata['urls'] if e['filename']==wheel.name)
 assert entry['digests']['sha256']==expected
 with urllib.request.urlopen(entry['url'],timeout=30) as response:wheel.write_bytes(response.read())
assert hashlib.sha256(wheel.read_bytes()).hexdigest()==expected
PY
/workspace/maths-toolchains/allocation-venv/bin/pip install --no-index --no-deps /workspace/maths-onboarding/allocation-downloads/networkx-3.4.2-py3-none-any.whl
/workspace/maths-toolchains/allocation-venv/bin/python - <<'PY'
import hashlib,pathlib,networkx
import networkx.algorithms.flow.networksimplex as module
assert networkx.__version__=='3.4.2'
assert hashlib.sha256(pathlib.Path(module.__file__).read_bytes()).hexdigest()=='df6b9eb686568feffb28f3b6389a6eb4fd05a53aec43fa89c67b42f17c4856bd'
print('Verified allocation reference deployment')
PY
