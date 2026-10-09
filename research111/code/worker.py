"""DP-only verifier process; no solver import and no admission cache."""
import json,sys
from checker import verify as admit
for line in sys.stdin:
 request=json.loads(line);answer=admit(request['row'],request['time'],request['certificate']);print(json.dumps({'accepted':answer}),flush=True)
