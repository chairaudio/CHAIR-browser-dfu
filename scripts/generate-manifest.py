#!/usr/bin/env python3
"""Regenerate releases.json from the .bin files in ../releases.

Run this after dropping a new firmware build (produced by your existing
git-describe + dfu-suffix build step) into releases/, then commit both the
new .bin and the updated releases.json and push to publish via GitHub Pages.
"""
import json
import os
import re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RELEASES_DIR = os.path.join(ROOT, "releases")
OUTPUT = os.path.join(ROOT, "releases.json")

# Matches v1.2.3, v1.2.3-beta, v1.2.3-beta-2, etc. Doesn't try to handle
# git-describe's "-N-gHASH" commit-count suffix as a post-release — if that
# style shows up again, it'll sort like a pre-release, which is a known gap.
_VERSION_RE = re.compile(r"v(\d+)\.(\d+)\.(\d+)(.*?)(?:\.bin)?$", re.IGNORECASE)


def version_key(name):
    """Sortable key from a release filename, ascending order.

    Same major.minor.patch: a pre-release suffix (e.g. -beta) sorts before
    the plain release, and suffixes themselves sort naturally (beta before
    beta-2). Filenames that don't match the pattern sort first, by name.
    """
    m = _VERSION_RE.search(name)
    if not m:
        return (-1, -1, -1, 0, (name.lower(),))
    major, minor, patch = int(m.group(1)), int(m.group(2)), int(m.group(3))
    suffix = m.group(4).strip("-_")
    is_release = 1 if not suffix else 0
    suffix_key = tuple(
        int(chunk) if chunk.isdigit() else chunk
        for chunk in re.split(r"(\d+)", suffix) if chunk
    )
    return (major, minor, patch, is_release, suffix_key)


def main():
    entries = []
    for name in sorted(os.listdir(RELEASES_DIR)):
        if not name.lower().endswith(".bin"):
            continue
        path = os.path.join(RELEASES_DIR, name)
        if not os.path.isfile(path):
            continue
        stat = os.stat(path)
        entries.append({
            "name": name,
            "size": stat.st_size,
            "mtime": int(stat.st_mtime * 1000),
        })
    # Descending by version (newest first). Flip reverse=False for ascending.
    entries.sort(key=lambda e: version_key(e["name"]), reverse=True)

    with open(OUTPUT, "w") as f:
        json.dump(entries, f, indent=2)
        f.write("\n")

    print(f"Wrote {len(entries)} release(s) to {OUTPUT}")


if __name__ == "__main__":
    main()
