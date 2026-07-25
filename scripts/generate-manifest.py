#!/usr/bin/env python3
"""Regenerate releases.json from the .bin files in ../releases.

Run this after dropping a new firmware build (produced by your existing
git-describe + dfu-suffix build step) into releases/, then commit both the
new .bin and the updated releases.json and push to publish via GitHub Pages.
"""
import json
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RELEASES_DIR = os.path.join(ROOT, "releases")
OUTPUT = os.path.join(ROOT, "releases.json")


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
    entries.sort(key=lambda e: e["mtime"], reverse=True)

    with open(OUTPUT, "w") as f:
        json.dump(entries, f, indent=2)
        f.write("\n")

    print(f"Wrote {len(entries)} release(s) to {OUTPUT}")


if __name__ == "__main__":
    main()
