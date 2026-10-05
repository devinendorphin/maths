"""Reproduce stages from frozen snapshots in a fresh destination; never overwrites evidence."""
import argparse,subprocess,sys,shutil,json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
a=argparse.ArgumentParser();a.add_argument('stage',type=int,choices=range(31,36));a.add_argument('--destination',required=True);args=a.parse_args();dest=Path(args.destination).resolve();assert not dest.exists();dest.mkdir();shutil.copytree(ROOT/'stages'/str(args.stage)/'code',dest/'code');shutil.copy2(ROOT/'Handoff.md',dest/'Handoff.md')
if args.stage==35:
 p=dest/'stages/34';p.mkdir(parents=True);shutil.copy2(ROOT/'stages/34/Selection.json',p/'Selection.json')
subprocess.run([sys.executable,str(dest/'code/runner.py'),str(args.stage)],check=True)
