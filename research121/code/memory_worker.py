import json
from pathlib import Path
import sys
from controls import memory_trial

spec=json.loads(Path(sys.argv[1]).read_text())
d,m=memory_trial(**spec)
print(json.dumps(dict(logical=d,measurements=m)))
