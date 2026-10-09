"""Pristine imported parent: verification runs only in private fork children."""
import json
import os
import signal
import sys

sys.path.insert(0,sys.argv[1])
from veripb import run_cmd_main
print('READY',flush=True)
for line in sys.stdin:
    request=json.loads(line);sys.stdout.flush();sys.stderr.flush();pid=os.fork()
    if pid==0:
        signal.alarm(30)
        quiet=os.open('/dev/null',os.O_WRONLY)
        os.dup2(quiet,1);os.dup2(quiet,2);os.close(quiet)
        sys.argv=['veripb',request['formula'],request['proof']]
        try:code=run_cmd_main()
        except BaseException:code=99
        os._exit(int(code or 0))
    _,status,usage=os.wait4(pid,0)
    code=os.waitstatus_to_exitcode(status)
    print(json.dumps(dict(code=code,cpu=usage.ru_utime+usage.ru_stime)),flush=True)
