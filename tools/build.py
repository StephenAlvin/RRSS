#!/usr/bin/env python3
"""Run the whole data pipeline: fetch PokeAPI tables, parse the documentation, download sprites, generate pages.

Usage: python3 tools/build.py [--skip-fetch] [--skip-sprites]
"""
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
STEPS = [
    ("fetch_pokeapi.py", "--skip-fetch"),
    ("parse_docs.py", None),
    ("base_data.py", None),
    ("download_sprites.py", "--skip-sprites"),
    ("generate_site.py", None),
]


def main() -> None:
    for script, skip_flag in STEPS:
        if skip_flag and skip_flag in sys.argv:
            print(f"== skipping {script}")
            continue
        print(f"== {script}")
        subprocess.run([sys.executable, "-I", str(HERE / script)], check=True)
    print("== done. Run `mkdocs serve` to preview or `mkdocs build` to build the site.")


if __name__ == "__main__":
    main()
