"""Pinned official VeriPB v2 checker; mixed native/Python deployment, no rule edits."""
import json,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
meta=json.loads((ROOT/'VeriPB2-source.json').read_text())
sys.path.insert(0,meta['folder'])
sys.path.append(json.loads((ROOT/'Dependency-setup.json').read_text())['tools_root']+'/python')
from veripb import run_cmd_main
sys.exit(run_cmd_main())
