#!/usr/bin/env python3
"""Download the PokeAPI CSV tables needed for the vanilla (ORAS) baseline into cache/pokeapi/.

Usage: python3 -I tools/fetch_pokeapi.py [--force]
"""
import sys
import urllib.request
from concurrent.futures import ThreadPoolExecutor

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))  # allow running with python3 -I

from common import CACHE

BASE_URL = "https://raw.githubusercontent.com/PokeAPI/pokeapi/master/data/v2/csv/"

FILES = [
    "abilities.csv", "ability_names.csv", "ability_prose.csv", "pokemon_abilities.csv", "pokemon_abilities_past.csv",
    "egg_groups.csv", "egg_group_prose.csv", "pokemon_egg_groups.csv",
    "evolution_triggers.csv", "pokemon_evolution.csv",
    "growth_rates.csv", "growth_rate_prose.csv",
    "items.csv", "item_names.csv", "pokemon_items.csv", "machines.csv",
    "locations.csv", "location_names.csv",
    "moves.csv", "move_names.csv", "move_effect_prose.csv", "move_changelog.csv", "move_damage_classes.csv",
    "pokemon_moves.csv", "pokemon_move_methods.csv",
    "pokemon.csv", "pokemon_species.csv", "pokemon_species_names.csv",
    "pokemon_stats.csv", "pokemon_stats_past.csv", "stats.csv",
    "pokemon_types.csv", "pokemon_types_past.csv", "types.csv", "type_names.csv", "type_efficacy.csv",
    "pokemon_forms.csv", "pokemon_form_names.csv",
    "version_groups.csv", "versions.csv",
]


def fetch(name: str, force: bool) -> str:
    target = CACHE / name
    if target.exists() and not force:
        return f"cached  {name}"
    with urllib.request.urlopen(BASE_URL + name, timeout=120) as resp:
        data = resp.read()
    target.write_bytes(data)
    return f"fetched {name} ({len(data)} bytes)"


def main() -> None:
    force = "--force" in sys.argv
    CACHE.mkdir(parents=True, exist_ok=True)
    with ThreadPoolExecutor(max_workers=8) as pool:
        for line in pool.map(lambda n: fetch(n, force), FILES):
            print(line)


if __name__ == "__main__":
    main()
