"""Checkpoint observer using PPid, because this runtime omits task/children.

The frozen initial sampler is preserved. This module is used only for the
declared memory supplement, not for any headline timing measurement.
"""
from pathlib import Path


def status(pid):
    try:
        fields = {}
        for line in Path(f'/proc/{pid}/status').read_text().splitlines():
            if line.startswith(('PPid:', 'VmRSS:')):
                key, value = line.split(':', 1)
                fields[key] = int(value.split()[0])
        return fields
    except (FileNotFoundError, ProcessLookupError):
        return {}


def observe(parent, checker):
    statuses = {int(p.name): status(int(p.name)) for p in Path('/proc').iterdir()
                if p.name.isdigit()}
    assert statuses[checker]['PPid'] == parent
    ids = {parent}
    while True:
        expanded = ids | {pid for pid, fields in statuses.items()
                          if fields.get('PPid') in ids}
        if expanded == ids:
            break
        ids = expanded
    assert checker in ids
    # The held verifier stays live throughout these reads. The checker source
    # does not spawn children; other discovered descendants remain included.
    values = {pid: status(pid).get('VmRSS', 0) for pid in ids}
    assert values[parent] > 0 and values[checker] > 0
    return ids, values
