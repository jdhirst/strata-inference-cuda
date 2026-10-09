#!/usr/bin/env python3
"""Update the existing package to the newest stable upstream version tag."""
import argparse
import hashlib
import json
from pathlib import Path
import re
import subprocess
import urllib.request

ROOT = Path(__file__).resolve().parents[1]
API = 'https://api.github.com/repos/Niko1221/Strata/tags'


def fetch(url):
    request = urllib.request.Request(url, headers={'User-Agent': 'strata-arch-release-updater'})
    with urllib.request.urlopen(request, timeout=120) as response:
        return response.read()


def version(tag):
    match = re.fullmatch(r'v(\d+(?:\.\d+){2,})', tag)
    return tuple(map(int, match.group(1).split('.'))) if match else None


def latest_tag():
    tags = []
    for page in range(1, 101):
        batch = json.loads(fetch(f'{API}?per_page=100&page={page}'))
        tags.extend(t['name'] for t in batch if version(t['name']) is not None)
        if len(batch) < 100:
            break
    else:
        raise RuntimeError('tag pagination limit reached')
    if not tags:
        raise RuntimeError('upstream has no stable version tags')
    return max(tags, key=version)


def checksum(url):
    digest = hashlib.sha256()
    request = urllib.request.Request(url, headers={'User-Agent': 'strata-arch-release-updater'})
    with urllib.request.urlopen(request, timeout=120) as response:
        while chunk := response.read(4 << 20):
            digest.update(chunk)
    return digest.hexdigest()


def update_text(text, tag, commit, sums):
    text = re.sub(r'^pkgver=.*$', f'pkgver={tag[1:]}', text, flags=re.M)
    text = re.sub(r'^pkgrel=.*$', 'pkgrel=1', text, flags=re.M)
    text = re.sub(r'^_llama_commit=.*$', f'_llama_commit={commit}', text, flags=re.M)
    value = 'sha256sums=(' + '\n            '.join(f"'{s}'" for s in sums) + ')'
    text, count = re.subn(r'^sha256sums=\(.*?\)', value, text, flags=re.M | re.S)
    if count != 1:
        raise RuntimeError('expected one sha256sums array')
    return text


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--check', action='store_true', help='report available version without changing files')
    args = parser.parse_args()
    path = ROOT / 'PKGBUILD'
    old = path.read_text()
    current = re.search(r'^pkgver=(\S+)$', old, re.M).group(1)
    tag = latest_tag()
    if version(tag) <= version('v' + current):
        print(f'Already current: {current}; latest stable tag: {tag}')
        return
    print(f'Available tagged release: {current} -> {tag[1:]}', flush=True)
    if args.check:
        return
    pin = fetch(f'https://raw.githubusercontent.com/Niko1221/Strata/{tag}/third_party/ggml/VERSION.txt').decode().split()[0]
    if not re.fullmatch(r'[0-9a-f]{40}', pin):
        raise RuntimeError('invalid upstream llama.cpp pin')
    sums = [checksum(f'https://github.com/Niko1221/Strata/archive/refs/tags/{tag}.tar.gz'),
            checksum(f'https://github.com/ggml-org/llama.cpp/archive/{pin}.tar.gz')]
    sums.extend(hashlib.sha256((ROOT / name).read_bytes()).hexdigest()
                for name in ('strata-inference', 'README.md', 'LICENSE'))
    new = update_text(old, tag, pin, sums)
    # Generate metadata successfully before replacing either tracked file.
    path.write_text(new)
    try:
        metadata = subprocess.check_output(['makepkg', '--printsrcinfo'], cwd=ROOT, text=True)
    except BaseException:
        path.write_text(old)
        raise
    (ROOT / '.SRCINFO').write_text(metadata)
    print(f'Updated PKGBUILD and .SRCINFO to {tag}; llama.cpp {pin}')


if __name__ == '__main__':
    main()
