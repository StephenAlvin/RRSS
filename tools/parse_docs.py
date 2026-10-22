#!/usr/bin/env python3
"""Parse Drayano's Rising Ruby / Sinking Sapphire documentation (Documentation/*.txt) into data/rrss.json.

Usage: python3 -I tools/parse_docs.py
"""
import json
import re
import sys

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))  # allow running with python3 -I

from common import DATA, DOCS_SRC, read_doc_lines

WARNINGS = []


def warn(msg: str) -> None:
    WARNINGS.append(msg)


# ---------------------------------------------------------------- generic helpers

def is_rule(line: str) -> bool:
    s = line.strip()
    return len(s) > 3 and set(s) <= set("o-|")


def cells_of(line: str):
    s = line.strip()
    if not s.startswith("|"):
        return None
    s = s.strip("|")
    return [c.strip() for c in s.split("|")]


def parse_intro(lines):
    """Read the boxed introduction at the top of a document."""
    title = None
    paragraphs = []
    current = []
    files = []
    in_files = False
    seen_rows = 0
    for line in lines:
        if not line.strip():
            if seen_rows:
                break
            continue
        if is_rule(line):
            continue
        cells = cells_of(line)
        if cells is None:
            continue
        seen_rows += 1
        if seen_rows == 1:
            continue  # game title
        if seen_rows == 2:
            title = " — ".join(c for c in cells if c)
            continue
        if cells[0].startswith("Files mentioned"):
            in_files = True
            continue
        if in_files:
            if len(cells) >= 2:
                files.append({"file": cells[0], "description": cells[1]})
            continue
        text = " ".join(c for c in cells if c).strip()
        if text:
            current.append(text)
        elif current:
            paragraphs.append(" ".join(current))
            current = []
    if current:
        paragraphs.append(" ".join(current))
    return {"title": title, "paragraphs": paragraphs, "files": files}


def split_marks(s: str):
    """'Icicle Crash ** (note)' -> ('Icicle Crash', 2, 'note')."""
    m = re.match(r"^(.*?)\s*(\*{1,2})?\s*(?:\((.*)\))?\s*$", s)
    return m.group(1).strip(), len(m.group(2) or ""), m.group(3)


# ---------------------------------------------------------------- PokemonChanges.txt

HEADER_RE = re.compile(r"^#(\d{3}) (.+?)\s*$")
MOVE_RE = re.compile(r"^(\d+)\s+(\S.*?)\s*$")
STAT_RE = re.compile(r"^(HP|Attack|Defense|Sp\. Attack|Sp\. Atk|Sp\. Defense|Sp\. Def|Speed|Total)\s+(\d+)\s*>>\s*(\d+)\s*$")
STAT_KEYS = {"Sp. Atk": "Sp. Attack", "Sp. Def": "Sp. Defense"}
FIELD_RE = re.compile(
    r"^(L?ocation|Ability 1|Ability 2|Hidden Ability|New TM/HMs|Evolution Level|Evolution|Held Items?|Type|"
    r"Effort Values|EVs|Base Happiness|Move Tutor|Catch Rate):?\s+(.+?)\s*$"
)


def parse_ability_value(value: str):
    old = None
    if ">>" in value:
        old, value = [v.strip() for v in value.split(">>", 1)]
    name, mark, note = split_marks(value)
    return {"old": old, "new": name, "mark": mark, "note": note}


def parse_held_items(value: str):
    items = []
    for part in value.split(","):
        part = part.strip()
        m = re.match(r"^(.+?)\s*\((\d+)%\)$", part)
        if m:
            items.append({"item": m.group(1).strip(), "rate": int(m.group(2))})
        elif part:
            items.append({"item": part, "rate": None})
    return items


def parse_pokemon_doc(lines):
    intro = parse_intro(lines)
    text = "\n".join(lines)
    chunks = re.split(r"\n(?=#\d{3} )", text)
    entries = []
    for chunk in chunks[1:]:
        clines = chunk.split("\n")
        m = HEADER_RE.match(clines[0])
        if not m:
            warn(f"Bad Pokémon header: {clines[0]!r}")
            continue
        entry = {
            "num": int(m.group(1)),
            "doc_name": m.group(2).strip(),
            "location": None,
            "fields": {},
            "groups": [{"forms": None, "stats": {}, "moves": []}],
        }
        groups = entry["groups"]
        pending_headers = []
        first_rule_seen = False
        for raw in clines[1:]:
            s = raw.rstrip()
            if not s.strip():
                continue
            stripped = s.strip()
            if set(stripped) == {"="}:
                if not first_rule_seen:
                    first_rule_seen = True
                    continue
                groups.append({"forms": pending_headers or ["?"], "stats": {}, "moves": []})
                if not pending_headers:
                    warn(f"#{entry['num']}: form rule without header")
                pending_headers = []
                continue
            mm = MOVE_RE.match(s)
            if mm:
                name, mark, note = split_marks(mm.group(2))
                groups[-1]["moves"].append({"level": int(mm.group(1)), "name": name, "mark": mark, "note": note})
                continue
            sm = STAT_RE.match(s)
            if sm:
                key = STAT_KEYS.get(sm.group(1), sm.group(1))
                groups[-1]["stats"][key] = [int(sm.group(2)), int(sm.group(3))]
                continue
            fm = FIELD_RE.match(s)
            if fm:
                key, value = fm.group(1), fm.group(2).strip()
                f = entry["fields"]
                if key in ("Location", "ocation"):
                    entry["location"] = value
                elif key in ("Ability 1", "Ability 2", "Hidden Ability"):
                    f[{"Ability 1": "ability1", "Ability 2": "ability2", "Hidden Ability": "hidden_ability"}[key]] = parse_ability_value(value)
                elif key == "New TM/HMs":
                    f["new_tms"] = [v.strip() for v in value.split(",") if v.strip()]
                elif key == "Move Tutor":
                    f["tutor"] = [v.strip() for v in value.split(",") if v.strip()]
                elif key == "Evolution Level":
                    a, b = [int(x) for x in re.findall(r"\d+", value)[:2]]
                    f["evolution_level"] = [a, b]
                elif key == "Evolution":
                    f["evolution"] = value
                elif key in ("Held Item", "Held Items"):
                    f["held_items"] = parse_held_items(value)
                elif key == "Type":
                    old, new = [v.strip() for v in value.split(">>", 1)]
                    f["type"] = {"old": [t.strip() for t in old.split("/")], "new": [t.strip() for t in new.split("/")]}
                elif key in ("Effort Values", "EVs"):
                    old, new = [v.strip() for v in value.split(">>", 1)]
                    f["evs"] = {"old": old, "new": new}
                elif key == "Base Happiness":
                    a, b = [int(x) for x in re.findall(r"\d+", value)[:2]]
                    f["base_happiness"] = [a, b]
                elif key == "Catch Rate":
                    a, b = [int(x) for x in re.findall(r"\d+", value)[:2]]
                    f["catch_rate"] = [a, b]
                continue
            # Anything else is a form header (one or more lines before a '=' rule).
            if ":" in stripped or ">>" in stripped:
                warn(f"#{entry['num']}: unrecognised line {stripped!r}")
            pending_headers.append(stripped)
        if pending_headers:
            warn(f"#{entry['num']}: dangling header lines {pending_headers}")
        # Move lists that follow stat-only form groups apply to every form.
        named = [g for g in groups if g["forms"]]
        with_moves = [g for g in groups if g["moves"]]
        if len(named) > 1 and len(with_moves) == 1 and with_moves[0]["forms"]:
            groups[0]["moves"] = with_moves[0]["moves"]
            with_moves[0]["moves"] = []
        entry["groups"] = [g for g in groups if g["stats"] or g["moves"] or g["forms"] is None]
        entries.append(entry)
    nums = [e["num"] for e in entries]
    if nums != list(range(1, len(nums) + 1)):
        warn("Pokémon numbering is not contiguous")
    return {"intro": intro, "entries": entries}


# ---------------------------------------------------------------- AreaChanges.txt

AREA_BOX_RE = re.compile(r"^o-{5,40}o\s*$")
METHOD_NORMALISE = {"Surf": "Surfing"}


def parse_trainer_name(tr: str):
    mimic = None
    m = re.search(r"\s*\[(.+?)\]\s*$", tr)
    if m:
        mimic = m.group(1)
        tr = tr[: m.start()].rstrip()
    rematch = None
    m = re.search(r"\s*\(([0-9]|C)\)\s*$", tr)
    if m:
        rematch = m.group(1)
        tr = tr[: m.start()].rstrip()
    return tr.strip(), rematch, mimic


def parse_party(text: str):
    party, note = [], None
    for part in text.split(","):
        part = part.strip()
        if not part:
            continue
        m = re.match(r"^(.+?)\s+(\d+)$", part)
        if m and not part.startswith("See "):
            party.append({"name": m.group(1).strip(), "level": int(m.group(2))})
        else:
            note = part if note is None else note + ", " + part
    return party, note


def parse_area_doc(lines):
    intro = parse_intro(lines)
    areas = []
    area = None
    current_section = "Main Game"
    mode = None
    section = None
    special = None
    for i, raw in enumerate(lines):
        s = raw.rstrip()
        if not s.strip() or is_rule(s):
            continue
        cells = cells_of(s)
        if cells is None:
            continue
        prev = lines[i - 1].rstrip() if i else ""
        nxt = lines[i + 1] if i + 1 < len(lines) else ""
        boxed = len(cells) == 1 and re.match(r"^o-+o\s*$", prev.strip()) and is_rule(nxt)
        if boxed and len(prev.strip()) <= 40:
            area = {"name": cells[0], "section": current_section, "encounters": [], "notes": [], "trainer_sections": [], "special_battles": []}
            areas.append(area)
            mode = section = special = None
            continue
        if boxed and cells[0].isupper() and area is not None:
            current_section = cells[0].title()
            continue
        if area is None:
            continue
        c0 = cells[0]
        if len(cells) == 1:
            if c0.startswith(("Hint:", "Note:")):
                kind, text = c0.split(":", 1)
                area["notes"].append({"kind": kind, "text": text.strip(), "context": mode or "area"})
            elif c0.startswith("Special Battle"):
                special = {"title": c0, "pokemon": []}
                area["special_battles"].append(special)
                mode = "special"
            elif c0.startswith(("Trainers", "Rematches")):
                section = {"title": c0, "trainers": [], "mimic": False}
                area["trainer_sections"].append(section)
                mode = "trainer"
            else:
                warn(f"{area['name']}: unexpected single-cell row {c0!r}")
            continue
        if c0 == "Method":
            mode = "enc"
            continue
        if c0 == "ID":
            mode = "trainer"
            if section is None:
                section = {"title": "Trainers", "trainers": [], "mimic": False}
                area["trainer_sections"].append(section)
            section["mimic"] = "Mimicking" in cells[1]
            continue
        if c0 == "Pokemon" and len(cells) >= 5:
            mode = "special"
            continue
        if mode == "enc" and len(cells) == 3:
            method = METHOD_NORMALISE.get(c0, c0)
            species = []
            for part in cells[2].split(","):
                part = part.strip()
                if part:
                    species.append({"name": part.rstrip("*").strip(), "rare": part.endswith("*")})
            area["encounters"].append({"method": method, "level": cells[1], "species": species})
        elif mode == "trainer" and len(cells) == 3:
            name, rematch, mimic = parse_trainer_name(cells[1])
            party, note = parse_party(cells[2])
            if section is None:
                section = {"title": "Trainers", "trainers": [], "mimic": False}
                area["trainer_sections"].append(section)
            section["trainers"].append({"id": c0, "name": name, "rematch": rematch, "mimic": mimic, "party": party, "note": note})
        elif mode == "special" and len(cells) == 5:
            special["pokemon"].append({
                "name": c0, "level": int(cells[1]) if cells[1].isdigit() else cells[1], "item": cells[2] or None,
                "ability": cells[3] or None, "moves": [mv.strip() for mv in cells[4].split(",") if mv.strip()],
            })
        else:
            warn(f"{area['name']}: unparsed row in mode {mode}: {cells}")
    return {"intro": intro, "areas": areas}


# ---------------------------------------------------------------- AttackChanges.txt

def parse_attack_doc(lines):
    intro = parse_intro(lines)
    moves = []
    i = 0
    # skip intro box
    while i < len(lines) and (lines[i].strip() == "" or lines[i].startswith(("o", "|"))):
        i += 1
    current = None
    prev_name = None
    while i < len(lines):
        s = lines[i].rstrip()
        i += 1
        if not s.strip():
            current = None
            continue
        if set(s.strip()) == {"="}:
            current = {"name": prev_name, "changes": []}
            moves.append(current)
            continue
        if current is None:
            prev_name = s.strip()
            continue
        m = re.match(r"^(\S.*?)\s{2,}(.+?)\s*$", s)
        if not m:
            warn(f"Attack changes: unparsed line {s!r}")
            continue
        key, value = m.group(1), m.group(2)
        if ">>" in value:
            old, new = [v.strip() for v in value.split(">>", 1)]
            current["changes"].append({"field": key, "old": old, "new": new})
        else:
            current["changes"].append({"field": key, "old": None, "new": value})
    return {"intro": intro, "moves": moves}


# ---------------------------------------------------------------- table documents (evolution, items, gifts)

KNOWN_SECTIONS = {
    "Trade Evolutions", "Trade with Item Evolutions", "Trade with Pokémon Evolutions", "Level Adjustments",
    "Item Usability Changes", "Item Price Changes", "Market Changes",
    "Gift Pokémon Changes", "Static Encounter Changes",
}


def parse_table_doc(lines):
    intro = parse_intro(lines)
    # skip intro box
    i = 0
    seen_blank = False
    while i < len(lines):
        if not lines[i].strip():
            seen_blank = True
        elif seen_blank:
            break
        i += 1
    sections = []
    section = None
    for raw in lines[i:]:
        s = raw.rstrip()
        if not s.strip() or is_rule(s):
            continue
        cells = cells_of(s)
        if cells is None:
            continue
        if len(cells) == 1:
            if cells[0] in KNOWN_SECTIONS:
                section = {"title": cells[0], "text": [], "header": None, "rows": []}
                sections.append(section)
            elif section is not None:
                section["text"].append(cells[0])
            else:
                warn(f"Table doc: text before first section {cells[0]!r}")
            continue
        if section is None:
            warn(f"Table doc: row before first section {cells}")
            continue
        if section["header"] is None:
            section["header"] = cells
            continue
        if cells[0] == "" and section["rows"]:
            prev = section["rows"][-1]
            for j, c in enumerate(cells):
                if c and j < len(prev):
                    prev[j] = (prev[j] + " " + c).strip()
            continue
        section["rows"].append(cells)
    return {"intro": intro, "sections": sections}


# ---------------------------------------------------------------- main

def main() -> None:
    out = {
        "pokemon": parse_pokemon_doc(read_doc_lines(DOCS_SRC / "PokemonChanges.txt")),
        "areas": parse_area_doc(read_doc_lines(DOCS_SRC / "AreaChanges.txt")),
        "attacks": parse_attack_doc(read_doc_lines(DOCS_SRC / "AttackChanges.txt")),
        "evolutions": parse_table_doc(read_doc_lines(DOCS_SRC / "EvolutionChanges.txt")),
        "items": parse_table_doc(read_doc_lines(DOCS_SRC / "ItemChanges.txt")),
        "gifts": parse_table_doc(read_doc_lines(DOCS_SRC / "GiftsStaticEncountersChanges.txt")),
    }
    DATA.mkdir(exist_ok=True)
    (DATA / "rrss.json").write_text(json.dumps(out, ensure_ascii=False, indent=1), encoding="utf-8")
    p = out["pokemon"]["entries"]
    a = out["areas"]["areas"]
    print(f"Pokémon entries: {len(p)}")
    print(f"Areas: {len(a)}; encounter rows: {sum(len(x['encounters']) for x in a)}; "
          f"trainers: {sum(len(sec['trainers']) for x in a for sec in x['trainer_sections'])}; "
          f"special battles: {sum(len(x['special_battles']) for x in a)}")
    print(f"Attack changes: {len(out['attacks']['moves'])}")
    for key in ("evolutions", "items", "gifts"):
        print(f"{key}: " + ", ".join(f"{s['title']} ({len(s['rows'])} rows)" for s in out[key]["sections"]))
    for w in WARNINGS:
        print("WARNING:", w, file=sys.stderr)


if __name__ == "__main__":
    main()
