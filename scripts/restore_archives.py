#!/usr/bin/env python3
"""Restore exact archived experiment records into a compact maths checkout."""
import argparse
import hashlib
import os
from pathlib import Path, PurePosixPath
import shutil
import tarfile
import zipfile

ARCHIVES = {
    'baseline': (176127453, '656930b55f767e811089a8b345abb1cbf228559dd13afaf4be770d4c7c4f7b9f', 'campaigns/experiments-31-35'),
    'rebuild': (1640269628, 'bf22f2b35df53b73a8f5bd3f92a2aa1b7c93af9a32725eeaf37e6c1f477dc2e4', 'research36-rebuild'),
}

def sha256(stream):
    h = hashlib.sha256()
    for block in iter(lambda: stream.read(1024 * 1024), b''):
        h.update(block)
    return h.hexdigest()

def relative_path(name):
    p = PurePosixPath(name)
    if p.is_absolute() or '..' in p.parts or '\\' in name or not p.parts:
        raise ValueError(f'Unsafe archive path: {name}')
    return p

def write_member(destination, name, source):
    target = destination.joinpath(*relative_path(name).parts)
    if target.is_symlink() or not target.parent.resolve().is_relative_to(destination.resolve()):
        raise ValueError(f'Archive target escapes destination: {name}')
    if target.exists():
        with target.open('rb') as current:
            if sha256(current) != sha256(source):
                raise ValueError(f'Existing file differs; preserve or move it first: {target}')
        return
    target.parent.mkdir(parents=True, exist_ok=True)
    temporary = target.with_name(target.name + '.restoring')
    with temporary.open('xb') as output:
        try:
            shutil.copyfileobj(source, output, 1024 * 1024)
        except BaseException:
            temporary.unlink(missing_ok=True)
            raise
    os.replace(temporary, target)

def restore(kind, archive, repo, verify_only):
    size, expected, subdirectory = ARCHIVES[kind]
    assert archive.stat().st_size == size, f'Wrong {kind} archive size'
    with archive.open('rb') as source:
        assert sha256(source) == expected, f'Wrong {kind} archive checksum'
    if verify_only:
        print(f'{kind}: original archive size and SHA256 verified')
        return
    destination = repo / subdirectory
    destination.mkdir(parents=True, exist_ok=True)
    seen = set()
    if kind == 'baseline':
        with zipfile.ZipFile(archive) as container:
            for member in container.infolist():
                relative_path(member.filename)
                if member.is_dir():
                    continue
                assert member.filename not in seen and (member.external_attr >> 16) & 0o170000 != 0o120000
                seen.add(member.filename)
                with container.open(member) as source:
                    write_member(destination, member.filename, source)
    else:
        with tarfile.open(archive, 'r|xz') as container:
            for member in container:
                relative_path(member.name)
                assert member.isfile() and member.name not in seen, member.name
                seen.add(member.name)
                with container.extractfile(member) as source:
                    write_member(destination, member.name, source)
    print(f'{kind}: restored or checked {len(seen)} files under {destination}')

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--baseline', type=Path)
    parser.add_argument('--rebuild', type=Path)
    parser.add_argument('--repo', type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument('--verify-only', action='store_true')
    args = parser.parse_args()
    if not args.baseline and not args.rebuild:
        parser.error('Provide --baseline and/or --rebuild with a reassembled archive path')
    for kind in ARCHIVES:
        archive = getattr(args, kind)
        if archive:
            restore(kind, archive.resolve(), args.repo.resolve(), args.verify_only)

if __name__ == '__main__':
    main()
