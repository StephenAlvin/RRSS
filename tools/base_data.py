#!/usr/bin/env python3
"""Build data/base.json: vanilla Omega Ruby / Alpha Sapphire (Generation 6) baseline data from the PokeAPI CSV cache.

Usage: python3 -I tools/base_data.py
"""
import csv
import json
import re
from collections import defaultdict

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))  # allow running with python3 -I

from common import (BASE_GENERATION, CACHE, DATA, ENGLISH, MAX_SPECIES, ORAS_VERSION_GROUP, ORAS_VERSIONS, STAT_ORDER, norm)


def load(name):
    with open(CACHE / name, newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def english(rows, key, name_key="name"):
    return {int(r[key]): r[name_key] for r in rows if int(r["local_language_id"]) == ENGLISH}


def main() -> None:
    vg_order = {int(r["id"]): int(r["order"]) for r in load("version_groups.csv")}
    oras_order = vg_order[ORAS_VERSION_GROUP]

    # ---- types
    types = {}
    type_names = english(load("type_names.csv"), "type_id")
    for r in load("types.csv"):
        tid = int(r["id"])
        if r["generation_id"] and int(r["generation_id"]) <= BASE_GENERATION and tid < 10000:
            types[tid] = {"name": type_names[tid], "identifier": r["identifier"]}
    efficacy = defaultdict(dict)
    for r in load("type_efficacy.csv"):
        a, d = int(r["damage_type_id"]), int(r["target_type_id"])
        if a in types and d in types:
            efficacy[a][d] = int(r["damage_factor"]) / 100
    type_by_norm = {norm(t["name"]): tid for tid, t in types.items()}

    # ---- abilities
    ability_names = english(load("ability_names.csv"), "ability_id")
    ability_effects = {int(r["ability_id"]): r["short_effect"] for r in load("ability_prose.csv") if int(r["local_language_id"]) == ENGLISH}
    abilities = {}
    for r in load("abilities.csv"):
        aid = int(r["id"])
        if aid in ability_names and int(r["is_main_series"]) == 1:
            abilities[aid] = {"name": ability_names[aid], "effect": ability_effects.get(aid, ""), "generation": int(r["generation_id"])}
    ability_by_norm = {norm(a["name"]): aid for aid, a in abilities.items()}

    # ---- moves (with Gen 6 values reconstructed from the changelog)
    move_names = english(load("move_names.csv"), "move_id")
    effect_prose = {int(r["move_effect_id"]): r["short_effect"] for r in load("move_effect_prose.csv") if int(r["local_language_id"]) == ENGLISH}
    damage_classes = {int(r["id"]): r["identifier"] for r in load("move_damage_classes.csv")}
    changelog = defaultdict(list)
    for r in load("move_changelog.csv"):
        changelog[int(r["move_id"])].append(r)
    moves = {}
    for r in load("moves.csv"):
        mid = int(r["id"])
        if mid not in move_names or int(r["generation_id"]) > BASE_GENERATION or mid >= 10000:
            continue
        vals = {k: r[k] for k in ("type_id", "power", "pp", "accuracy", "priority", "effect_id", "effect_chance")}
        future = sorted((c for c in changelog[mid] if vg_order[int(c["changed_in_version_group_id"])] > oras_order),
                        key=lambda c: vg_order[int(c["changed_in_version_group_id"])])
        for field in vals:
            for c in future:
                if c[field] != "":
                    vals[field] = c[field]
                    break
        effect = effect_prose.get(int(vals["effect_id"]), "") if vals["effect_id"] else ""
        chance = vals["effect_chance"]
        effect = effect.replace("$effect_chance", chance or "").replace("[", "").replace("]", "")
        effect = re.sub(r"\{[^}]*\}", "", effect).strip()
        moves[mid] = {
            "name": move_names[mid],
            "type": int(vals["type_id"]) if vals["type_id"] else None,
            "power": int(vals["power"]) if vals["power"] else None,
            "pp": int(vals["pp"]) if vals["pp"] else None,
            "accuracy": int(vals["accuracy"]) if vals["accuracy"] else None,
            "priority": int(vals["priority"]) if vals["priority"] else 0,
            "damage_class": damage_classes[int(r["damage_class_id"])],
            "effect": effect,
            "effect_chance": int(chance) if chance else None,
            "generation": int(r["generation_id"]),
        }
    move_by_norm = {norm(m["name"]): mid for mid, m in moves.items()}

    # ---- items
    item_names = english(load("item_names.csv"), "item_id")
    items = {}
    item_by_norm = {}
    for r in load("items.csv"):
        iid = int(r["id"])
        if iid in item_names:
            items[iid] = {"name": item_names[iid], "identifier": r["identifier"], "cost": int(r["cost"] or 0)}
            item_by_norm.setdefault(norm(item_names[iid]), iid)

    # ---- machines (TM/HM numbers in ORAS)
    machines = {}
    for r in load("machines.csv"):
        if int(r["version_group_id"]) == ORAS_VERSION_GROUP:
            ident = items[int(r["item_id"])]["identifier"].upper()
            machines[int(r["move_id"])] = ident

    # ---- species
    species_names = {}
    genera = {}
    for r in load("pokemon_species_names.csv"):
        if int(r["local_language_id"]) == ENGLISH:
            species_names[int(r["pokemon_species_id"])] = r["name"]
            genera[int(r["pokemon_species_id"])] = r["genus"]
    growth_names = english(load("growth_rate_prose.csv"), "growth_rate_id")
    egg_names = english(load("egg_group_prose.csv"), "egg_group_id")
    egg_groups = defaultdict(list)
    for r in load("pokemon_egg_groups.csv"):
        egg_groups[int(r["species_id"])].append(egg_names[int(r["egg_group_id"])])
    species = {}
    for r in load("pokemon_species.csv"):
        sid = int(r["id"])
        if sid > MAX_SPECIES:
            continue
        species[sid] = {
            "name": species_names[sid],
            "genus": genera.get(sid, ""),
            "identifier": r["identifier"],
            "generation": int(r["generation_id"]),
            "evolves_from": int(r["evolves_from_species_id"]) if r["evolves_from_species_id"] else None,
            "gender_rate": int(r["gender_rate"]),
            "capture_rate": int(r["capture_rate"]),
            "base_happiness": int(r["base_happiness"]) if r["base_happiness"] else None,
            "hatch_counter": int(r["hatch_counter"]) if r["hatch_counter"] else None,
            "growth_rate": growth_names[int(r["growth_rate_id"])],
            "egg_groups": egg_groups.get(sid, []),
            "is_legendary": r["is_legendary"] == "1",
            "is_mythical": r["is_mythical"] == "1",
        }
    species_by_norm = {norm(s["name"]): sid for sid, s in species.items()}

    # ---- pokemon (default + Gen 6 alternate forms)
    pokemon_rows = {int(r["id"]): r for r in load("pokemon.csv")}
    form_names = {int(r["pokemon_form_id"]): r for r in load("pokemon_form_names.csv") if int(r["local_language_id"]) == ENGLISH}
    default_form_of = {}  # pokemon_id -> form row
    for r in load("pokemon_forms.csv"):
        if r["is_default"] == "1":
            default_form_of[int(r["pokemon_id"])] = r

    stats_cur = defaultdict(dict)
    for r in load("pokemon_stats.csv"):
        stats_cur[int(r["pokemon_id"])][int(r["stat_id"])] = (int(r["base_stat"]), int(r["effort"]))
    stats_past = defaultdict(dict)  # (pokemon, stat) -> (gen, base, effort) with smallest gen >= BASE
    for r in load("pokemon_stats_past.csv"):
        gen = int(r["generation_id"])
        if gen < BASE_GENERATION:
            continue
        key = (int(r["pokemon_id"]), int(r["stat_id"]))
        cur = stats_past.get(key)
        if cur is None or gen < cur[0]:
            stats_past[key] = (gen, int(r["base_stat"]), int(r["effort"]))

    types_cur = defaultdict(dict)
    for r in load("pokemon_types.csv"):
        types_cur[int(r["pokemon_id"])][int(r["slot"])] = int(r["type_id"])
    types_past = {}
    for r in load("pokemon_types_past.csv"):
        gen = int(r["generation_id"])
        if gen < BASE_GENERATION:
            continue
        key = (int(r["pokemon_id"]), int(r["slot"]))
        if key not in types_past or gen < types_past[key][0]:
            types_past[key] = (gen, int(r["type_id"]))

    abil_cur = defaultdict(dict)
    for r in load("pokemon_abilities.csv"):
        abil_cur[int(r["pokemon_id"])][int(r["slot"])] = int(r["ability_id"])
    abil_past = {}
    for r in load("pokemon_abilities_past.csv"):
        gen = int(r["generation_id"])
        if gen < BASE_GENERATION:
            continue
        key = (int(r["pokemon_id"]), int(r["slot"]))
        if key not in abil_past or gen < abil_past[key][0]:
            abil_past[key] = (gen, int(r["ability_id"]) if r["ability_id"] else None)

    stat_ids = {1: "HP", 2: "Attack", 3: "Defense", 4: "Sp. Attack", 5: "Sp. Defense", 6: "Speed"}

    def build_pokemon(pid):
        r = pokemon_rows[pid]
        stats, evs = {}, {}
        for stid, name in stat_ids.items():
            base, effort = stats_cur[pid].get(stid, (0, 0))
            past = stats_past.get((pid, stid))
            if past:
                base, effort = past[1], past[2]
            stats[name] = base
            if effort:
                evs[name] = effort
        ptypes = []
        for slot in (1, 2):
            past = types_past.get((pid, slot))
            tid = past[1] if past else types_cur[pid].get(slot)
            if tid:
                ptypes.append(tid)
        abils = {}
        for slot in (1, 2, 3):
            past = abil_past.get((pid, slot))
            aid = past[1] if past else abil_cur[pid].get(slot)
            abils[{1: "ability1", 2: "ability2", 3: "hidden"}[slot]] = aid
        form = default_form_of.get(pid)
        fname = form_names.get(int(form["id"])) if form else None
        return {
            "species": int(r["species_id"]),
            "identifier": r["identifier"],
            "form_name": (fname["pokemon_name"] or fname["form_name"]) if fname else None,
            "is_default": r["is_default"] == "1",
            "is_mega": bool(form and form["is_mega"] == "1"),
            "is_battle_only": bool(form and form["is_battle_only"] == "1"),
            "height": int(r["height"]) if r["height"] else None,
            "weight": int(r["weight"]) if r["weight"] else None,
            "base_experience": int(r["base_experience"]) if r["base_experience"] else None,
            "types": ptypes,
            "abilities": abils,
            "stats": stats,
            "evs": evs,
        }

    pokemon = {}
    species_forms = defaultdict(list)
    for pid, r in pokemon_rows.items():
        sid = int(r["species_id"])
        if sid > MAX_SPECIES:
            continue
        if r["is_default"] == "1":
            pokemon[pid] = build_pokemon(pid)
            species_forms[sid].insert(0, pid)
    for pid, r in pokemon_rows.items():
        sid = int(r["species_id"])
        if sid > MAX_SPECIES or r["is_default"] == "1":
            continue
        form = default_form_of.get(pid)
        if not form or vg_order.get(int(form["introduced_in_version_group_id"]), 999) > oras_order:
            continue
        p = build_pokemon(pid)
        base = pokemon[sid]
        differs = p["is_mega"] or p["stats"] != base["stats"] or p["types"] != base["types"] or p["abilities"] != base["abilities"]
        if differs:
            pokemon[pid] = p
            species_forms[sid].append(pid)

    # ---- learnsets (ORAS)
    learnsets = defaultdict(lambda: {"level_up": [], "egg": [], "tutor": [], "machine": []})
    method_names = {1: "level_up", 2: "egg", 3: "tutor", 4: "machine"}
    with open(CACHE / "pokemon_moves.csv", newline="", encoding="utf-8") as f:
        for r in csv.DictReader(f):
            if int(r["version_group_id"]) != ORAS_VERSION_GROUP:
                continue
            pid = int(r["pokemon_id"])
            if pid not in pokemon:
                continue
            method = method_names.get(int(r["pokemon_move_method_id"]))
            if not method:
                continue
            mid = int(r["move_id"])
            if mid not in moves:
                continue
            if method == "level_up":
                learnsets[pid]["level_up"].append([int(r["level"]), mid])
            else:
                learnsets[pid][method].append(mid)
    for pid, ls in learnsets.items():
        ls["level_up"].sort()
        for k in ("egg", "tutor", "machine"):
            ls[k] = sorted(set(ls[k]), key=lambda m: (machines.get(m, "ZZ"), moves[m]["name"]))

    # ---- wild held items (ORAS)
    held_items = defaultdict(list)
    for r in load("pokemon_items.csv"):
        if int(r["version_id"]) in ORAS_VERSIONS:
            pid = int(r["pokemon_id"])
            if pid in pokemon:
                entry = {"item": int(r["item_id"]), "rate": int(r["rarity"])}
                if entry not in held_items[pid]:
                    held_items[pid].append(entry)

    # ---- evolutions (vanilla method text)
    location_names = english(load("location_names.csv"), "location_id")
    triggers = {int(r["id"]): r["identifier"] for r in load("evolution_triggers.csv")}

    def evo_text(r):
        trig = triggers[int(r["evolution_trigger_id"])]
        parts = []
        if trig == "level-up":
            if r["minimum_level"]:
                parts.append(f"Lv. {r['minimum_level']}")
            else:
                parts.append("Level up")
            if r["minimum_happiness"]:
                parts.append("with high friendship")
            if r["minimum_affection"]:
                parts.append("with high affection")
            if r["minimum_beauty"]:
                parts.append("with max Beauty")
            if r["time_of_day"]:
                parts.append(f"during the {r['time_of_day']}")
            if r["location_id"]:
                parts.append(f"at {location_names.get(int(r['location_id']), 'a special location')}")
            if r["known_move_id"]:
                parts.append(f"knowing {move_names.get(int(r['known_move_id']), '?')}")
            if r["known_move_type_id"]:
                parts.append(f"knowing a {type_names[int(r['known_move_type_id'])]}-type move")
            if r["held_item_id"]:
                parts.append(f"holding {item_names[int(r['held_item_id'])]}")
            if r["party_species_id"]:
                parts.append(f"with {species_names[int(r['party_species_id'])]} in the party")
            if r["party_type_id"]:
                parts.append(f"with a {type_names[int(r['party_type_id'])]}-type Pokémon in the party")
            if r["relative_physical_stats"]:
                parts.append({"1": "Attack > Defense", "-1": "Attack < Defense", "0": "Attack = Defense"}[r["relative_physical_stats"]])
            if r["needs_overworld_rain"] == "1":
                parts.append("while it is raining")
            if r["turn_upside_down"] == "1":
                parts.append("with the system held upside down")
        elif trig == "use-item":
            parts.append(f"Use {item_names[int(r['trigger_item_id'])]}")
        elif trig == "trade":
            parts.append("Trade")
            if r["held_item_id"]:
                parts.append(f"holding {item_names[int(r['held_item_id'])]}")
            if r["trade_species_id"]:
                parts.append(f"for {species_names[int(r['trade_species_id'])]}")
        elif trig == "shed":
            parts.append("Lv. 20 with an empty party slot and a Poké Ball")
        else:
            parts.append(trig)
        if r["gender_id"]:
            parts.append("(female only)" if r["gender_id"] == "1" else "(male only)")
        return " ".join(parts)

    evolutions = defaultdict(list)
    evo_rows = defaultdict(list)
    for r in load("pokemon_evolution.csv"):
        to = int(r["evolved_species_id"])
        if to <= MAX_SPECIES:
            evo_rows[to].append(r)
    for to, rows in evo_rows.items():
        frm = species[to]["evolves_from"]
        if frm is None:
            continue
        evolutions[frm].append({"to": to, "method": " / ".join(dict.fromkeys(evo_text(r) for r in rows))})
    for lst in evolutions.values():
        lst.sort(key=lambda e: e["to"])

    out = {
        "types": types,
        "type_by_norm": type_by_norm,
        "efficacy": efficacy,
        "abilities": abilities,
        "ability_by_norm": ability_by_norm,
        "moves": moves,
        "move_by_norm": move_by_norm,
        "items": items,
        "item_by_norm": item_by_norm,
        "machines": machines,
        "species": species,
        "species_by_norm": species_by_norm,
        "pokemon": pokemon,
        "species_forms": species_forms,
        "learnsets": learnsets,
        "held_items": held_items,
        "evolutions": evolutions,
    }
    DATA.mkdir(exist_ok=True)
    (DATA / "base.json").write_text(json.dumps(out, ensure_ascii=False, separators=(",", ":")), encoding="utf-8")
    print(f"types {len(types)}, abilities {len(abilities)}, moves {len(moves)}, items {len(items)}, machines {len(machines)}")
    print(f"species {len(species)}, pokemon (incl. forms) {len(pokemon)}, learnsets {len(learnsets)}, held item sets {len(held_items)}, evolution parents {len(evolutions)}")
    forms = [(pid, p['form_name']) for pid, p in pokemon.items() if not p['is_default']]
    print(f"alternate forms kept: {len(forms)}")
    print(", ".join(f"{pid}:{name}" for pid, name in forms))


if __name__ == "__main__":
    main()
