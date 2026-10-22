"""Shared paths and helpers for the RR/SS wiki build tools."""
import re
import unicodedata
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DOCS_SRC = ROOT / "Documentation"
CACHE = ROOT / "cache" / "pokeapi"
DATA = ROOT / "data"
SITE_DOCS = ROOT / "docs"
IMG = SITE_DOCS / "img"

# Version group / generation used as the vanilla baseline (Omega Ruby / Alpha Sapphire).
ORAS_VERSION_GROUP = 16
ORAS_VERSIONS = {25, 26}
BASE_GENERATION = 6
ENGLISH = 9
MAX_SPECIES = 721

STAT_ORDER = ["HP", "Attack", "Defense", "Sp. Attack", "Sp. Defense", "Speed"]
STAT_SHORT = {"HP": "HP", "Attack": "Atk", "Defense": "Def", "Sp. Attack": "SpA", "Sp. Defense": "SpD", "Speed": "Spe"}

# Doc spelling -> PokeAPI spelling, after normalisation with norm().
MOVE_ALIASES = {
    "twinneedle": "twineedle",
    "petalblizard": "petalblizzard",
    "vicegrip": "visegrip",
    "faintattack": "feintattack",
    "hijumpkick": "highjumpkick",
    "smellingsalt": "smellingsalts",
    "ancientpower": "ancientpower",
    "extremespeed": "extremespeed",
    "dragonbreath": "dragonbreath",
    "softboiled": "softboiled",
    "selfdestruct": "selfdestruct",
    "thunderpunch": "thunderpunch",
    "sandattack": "sandattack",
    "doubleslap": "doubleslap",
    "featherdance": "featherdance",
    "grasswhistle": "grasswhistle",
    "poisonpowder": "poisonpowder",
    "visegrip": "visegrip",
    "bubblebeam": "bubblebeam",
    "solarbeam": "solarbeam",
    "thundershock": "thundershock",
    "dynamicpunch": "dynamicpunch",
    "lockon": "lockon",
    "uturn": "uturn",
    "wakeupslap": "wakeupslap",
    "flowershield": "flowershield",
}

ITEM_ALIASES = {
    "silverpowder": "silverpowder",
    "blackglasses": "blackglasses",
    "twistedspoon": "twistedspoon",
    "nevermeltice": "nevermeltice",
    "deepseatooth": "deepseatooth",
    "deepseascale": "deepseascale",
    "upgrade": "upgrade",
}


def norm(s: str) -> str:
    """Normalise a name for matching: lower-case, straight quotes, alphanumerics only (keeps ♀♂)."""
    s = s.replace("’", "'").replace("‘", "'").replace("é", "e").replace("É", "E")
    s = s.lower()
    s = re.sub(r"[^a-z0-9♀♂]", "", s)
    return s


def slugify(s: str) -> str:
    """File-name friendly slug (ASCII, lower-case, underscores)."""
    s = unicodedata.normalize("NFKD", s).encode("ascii", "ignore").decode("ascii")
    s = s.lower()
    s = re.sub(r"[^a-z0-9]+", "_", s).strip("_")
    return s or "page"


def read_doc_lines(path: Path):
    text = path.read_text(encoding="utf-8").replace("\r\n", "\n").replace("\t", "    ")
    return text.split("\n")

# Typos in the documentation -> canonical spellings (after norm()).
MOVE_ALIASES.update({
    "skullbush": "skullbash",
    "boomerang": "bonemerang",
    "bote": "bite",
    "imprision": "imprison",
    "pinmissle": "pinmissile",
})
SPECIES_ALIASES = {
    "darmantian": "darmanitan",
    "gifararig": "girafarig",
    "croocnaw": "croconaw",
    "ramaprdos": "rampardos",
}
ABILITY_ALIASES = {
    "lightingrod": "lightningrod",
}


def mega_stone_name(species_name: str, form_name: str):
    """Name of the Mega Stone (or orb) for a Mega/Primal form, or None if none exists."""
    if form_name.startswith("Primal"):
        return "Blue Orb" if species_name == "Kyogre" else "Red Orb"
    if species_name == "Rayquaza":
        return None
    suffix = ""
    if form_name.endswith(" X"):
        suffix = " X"
    elif form_name.endswith(" Y"):
        suffix = " Y"
    stem = {"Charizard": "Charizardite", "Mewtwo": "Mewtwonite"}.get(species_name, species_name + "ite")
    return stem + suffix
