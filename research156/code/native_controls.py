"""Exercise inherited rejection/recovery controls with the observer installed."""
import json
from pathlib import Path
import sys
import time
from meter import Meter, install

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'vendor'))


if __name__ == '__main__':
    meter = Meter(time.perf_counter_ns(), True)
    install(meter)
    from controls import run
    result = run('development-observed-native-controls')
    assert result['passed'] and len(result['controls']) == 42
    receipt = meter.finish()
    assert sum(b - a for a, b, label in receipt['intervals']) == receipt['end_ns'] - receipt['origin_ns']
    result['excluded_from_headline'] = True
    result['observer_installed'] = True
    (ROOT / 'Native-controls.json').write_text(json.dumps(result, sort_keys=True, indent=2) + '\n')
    print('Passed all 42 inherited controls with the observer installed')
