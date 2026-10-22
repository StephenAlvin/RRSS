#!/usr/bin/env python3
"""Download Pokémon sprites, menu icons and item icons from the PokeAPI sprites repository into docs/img/.

Usage: python3 -I tools/download_sprites.py
"""
import json
import sys
import urllib.error
import urllib.request
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))  # allow running with python3 -I

from common import DATA, IMG, ITEM_ALIASES, mega_stone_name, norm

SPRITES = "https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/"


def get(url: str):
    try:
        with urllib.request.urlopen(url, timeout=60) as resp:
            return resp.read()
    except urllib.error.HTTPError as e:
        if e.code == 404:
            return None
        raise


def download(job):
    target, urls = job
    if target.exists():
        return None
    for url in urls:
        data = get(url)
        if data:
            target.write_bytes(data)
            return f"ok   {target.relative_to(IMG)}"
    return f"MISS {target.relative_to(IMG)}"


def main() -> None:
    base = json.loads((DATA / "base.json").read_text(encoding="utf-8"))
    rrss = json.loads((DATA / "rrss.json").read_text(encoding="utf-8"))
    for sub in ("pokemon", "icons", "items"):
        (IMG / sub).mkdir(parents=True, exist_ok=True)
    jobs = []
    for pid in base["pokemon"]:
        jobs.append((IMG / "pokemon" / f"{pid}.png", [
            f"{SPRITES}pokemon/versions/generation-vi/x-y/{pid}.png",
            f"{SPRITES}pokemon/{pid}.png",
        ]))
        jobs.append((IMG / "icons" / f"{pid}.png", [
            f"{SPRITES}pokemon/versions/generation-vii/icons/{pid}.png",
            f"{SPRITES}pokemon/versions/generation-viii/icons/{pid}.png",
        ]))
    # item icons for every item mentioned in the documentation
    names = set()
    for e in rrss["pokemon"]["entries"]:
        for h in e["fields"].get("held_items", []):
            names.add(h["item"])
    for a in rrss["areas"]["areas"]:
        for sb in a["special_battles"]:
            for p in sb["pokemon"]:
                if p["item"]:
                    names.add(p["item"])
                if p["ability"]:
                    names.add(p["ability"])
    for doc in ("items", "evolutions", "gifts"):
        for sec in rrss[doc]["sections"]:
            for row in sec["rows"]:
                for cell in row:
                    for part in cell.replace(" and ", ",").split(","):
                        names.add(part.strip())
            for text in sec["text"]:
                for part in text.split(","):
                    names.add(part.strip())
    for pid, lst in base["held_items"].items():
        for h in lst:
            names.add(base["items"][str(h["item"])]["name"])
    for pid, p in base["pokemon"].items():
        if p["is_mega"]:
            stone = mega_stone_name(base["species"][str(p["species"])]["name"], p["form_name"])
            if stone:
                names.add(stone)
    idents = {"poke-ball"}
    for name in names:
        n = norm(name)
        n = ITEM_ALIASES.get(n, n)
        iid = base["item_by_norm"].get(n)
        if iid:
            idents.add(base["items"][str(iid)]["identifier"])
    for ident in sorted(idents):
        jobs.append((IMG / "items" / f"{ident}.png", [f"{SPRITES}items/{ident}.png"]))
    print(f"{len(jobs)} files to check")
    missing = 0
    with ThreadPoolExecutor(max_workers=16) as pool:
        for i, line in enumerate(pool.map(download, jobs)):
            if line and line.startswith("MISS"):
                missing += 1
                print(line)
            if i % 200 == 0:
                print(f"... {i}/{len(jobs)}")
    print(f"done, {missing} missing")


if __name__ == "__main__":
    main()
