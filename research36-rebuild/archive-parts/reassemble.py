#!/usr/bin/env python3
"""Restore the unchanged campaign ZIP from eight GitHub-sized ZIP parts."""
import argparse
import hashlib
import json
from pathlib import Path
import sys
import zipfile


def reassemble(directory, output):
    manifest = json.loads((directory / 'Parts-manifest.json').read_text())
    if output.exists():
        raise ValueError(f'Output already exists: {output}; choose another --output path.')
    temporary = output.with_name(output.name + '.assembling')
    if temporary.exists():
        raise ValueError(f'Temporary output already exists: {temporary}')
    for part in manifest['parts']:
        if not (directory / part['file']).is_file():
            raise ValueError(f'Missing part: {part["file"]}')
    total_hash = hashlib.sha256()
    total_bytes = 0
    try:
        with temporary.open('xb') as target:
            for part in manifest['parts']:
                source = directory / part['file']
                container_hash = hashlib.sha256()
                with source.open('rb') as f:
                    for block in iter(lambda: f.read(1024 * 1024), b''):
                        container_hash.update(block)
                if source.stat().st_size != part['file_bytes'] or container_hash.hexdigest() != part['file_sha256']:
                    raise ValueError(f'ZIP part checksum/size mismatch: {source.name}')
                payload_hash = hashlib.sha256()
                payload_bytes = 0
                with zipfile.ZipFile(source) as container:
                    with container.open(part['payload']) as f:
                        for block in iter(lambda: f.read(1024 * 1024), b''):
                            payload_hash.update(block)
                            total_hash.update(block)
                            payload_bytes += len(block)
                            total_bytes += len(block)
                            target.write(block)
                if payload_bytes != part['payload_bytes'] or payload_hash.hexdigest() != part['payload_sha256']:
                    raise ValueError(f'Payload checksum/size mismatch: {source.name}')
                print(f'Checked and joined {source.name}')
        if total_bytes != manifest['original']['bytes'] or total_hash.hexdigest() != manifest['original']['sha256']:
            raise ValueError('Reassembled archive checksum/size mismatch')
        temporary.rename(output)
    except BaseException:
        temporary.unlink(missing_ok=True)
        raise
    print(f'Restored {output}\nBytes: {total_bytes}\nSHA256: {total_hash.hexdigest()}')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--directory', type=Path, default=Path(__file__).resolve().parent,
                        help='Directory containing Parts-manifest.json and all eight part ZIPs')
    parser.add_argument('--output', type=Path, help='Destination campaign ZIP (must not already exist)')
    args = parser.parse_args()
    directory = args.directory.resolve()
    output = args.output or directory / json.loads((directory / 'Parts-manifest.json').read_text())['original']['filename']
    try:
        reassemble(directory, output.resolve())
    except (OSError, ValueError, KeyError, zipfile.BadZipFile, RuntimeError) as error:
        print(f'Cannot reassemble: {error}', file=sys.stderr)
        return 1
    return 0


if __name__ == '__main__':
    sys.exit(main())
