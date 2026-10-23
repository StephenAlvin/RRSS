# Rising Ruby / Sinking Sapphire Wiki

A fan-made wiki for Drayano's **Pokémon Rising Ruby** and **Pokémon Sinking Sapphire** (enhancement hacks of Omega Ruby / Alpha Sapphire), in the style of the [Platinum Renegade Wiki](https://fredericdlugi.github.io/platinum-renegade-wiki/).

The site is generated from the documentation that ships with the hack (`Documentation/*.txt`), merged with vanilla game data from [PokeAPI](https://pokeapi.co/) so that every Pokémon page is complete. It is built with [Material for MkDocs](https://squidfunk.github.io/mkdocs-material/).

## What is in it

- **Pokédex**: one page per Pokémon (all 721) with types and defensive matchups, abilities, base stats per form (vanilla values shown where the hack changed them), training/breeding data, evolutions, wild held items, level-up / TM & HM / tutor / egg moves, every wild location, gift/static encounters and every trainer that uses it. Plus a sortable, filterable table of all Pokémon.
- **Wild Pokémon**: encounter tables for all 123 documented areas (grass, hordes, DexNav, Rock Smash, surfing, fishing, soaring).
- **Trainers**: all 765 trainer rosters and rematch rosters by area, with the 55 boss battles (Gym Leaders, Team admins, rivals, Elite Four, Champion) in full detail, plus a boss overview page.
- **Changes**: base stats, types, abilities, evolutions, moves, new TM/tutor compatibility, held items, EV/friendship/catch rate changes, item & shop changes, gift & static encounter changes.
- Search, light/dark mode, sortable tables with filter boxes, prev/next navigation.

## Repository layout

```
Documentation/   Drayano's original documentation (source of truth)
Logos/           Logos by kojiyomi
tools/           Build pipeline (see below)
data/            Generated JSON (parsed docs + vanilla baseline)
docs/            MkDocs content: hand-written pages (index, faq, about) + generated pages + images
mkdocs.yml       Site configuration (navigation comes from docs/SUMMARY.md)
```

The pipeline in `tools/`:

| Script | Purpose |
| --- | --- |
| `fetch_pokeapi.py` | Downloads the PokeAPI CSV tables into `cache/pokeapi/` |
| `parse_docs.py` | Parses `Documentation/*.txt` into `data/rrss.json` |
| `base_data.py` | Builds the vanilla ORAS (Generation 6) baseline into `data/base.json` |
| `download_sprites.py` | Downloads Pokémon sprites, icons and item icons into `docs/img/` |
| `generate_site.py` | Writes all generated Markdown pages and `docs/SUMMARY.md` |
| `build.py` | Runs all of the above in order |
| `mkdocs_hook.py` | MkDocs hook that re-parses and regenerates before every build (dev server and CI) |

Everything under `docs/pokemon/`, `docs/wild/`, `docs/trainers/` and `docs/changes/` is generated; edit the generator rather than those files.

## Quick start

You need Python 3 (macOS ships it) and, optionally, Node for the `npm run` shortcuts. The Python equivalents of Node concepts: `venv/` is like `node_modules/` (a local, ignored folder with the installed packages), `requirements.txt` is the dependency list, and `venv/bin/...` are the installed commands.

```bash
npm run setup     # one time: create venv/ and install MkDocs (like npm install)
npm run dev       # start the dev server at http://127.0.0.1:8000/ with live reload
npm run build     # full strict build into site/ (what the GitHub workflow runs)
```

No Node? The same commands exist as `make setup`, `make dev`, `make build`.

`npm run dev` regenerates the pages from the documentation before every build (see `tools/mkdocs_hook.py`), so editing anything below is picked up automatically while it runs. The first build takes about 30 seconds; later rebuilds only process changed pages.

## Making changes

| I want to… | Edit | Then |
| --- | --- | --- |
| Change the home page, FAQ or About text | `docs/index.md`, `docs/faq.md`, `docs/about.md` | Save; the dev server reloads |
| Change colours, badges, table styling | `docs/stylesheets/extra.css` | Save; the dev server reloads |
| Change table sorting, the filter box, or the sticky table header and scrollbar | `docs/javascripts/tablesort.js`, `docs/javascripts/table-scrollbar.js` | Save; the dev server reloads |
| Change the site title, theme or plugins | `mkdocs.yml` | Save; the dev server restarts the build |
| Fix a typo or value in the game data | `Documentation/*.txt` (the source of truth) | Save; pages regenerate automatically |
| Map a documentation typo to the right name | `SPECIES_ALIASES`, `MOVE_ALIASES`, `ITEM_ALIASES`, `ABILITY_ALIASES` in `tools/common.py` | Save; pages regenerate automatically |
| Change how a Pokémon, area, trainer or change page looks | `tools/generate_site.py` (one method per page type, e.g. `pokemon_page`, `wild_pages`, `trainer_pages`, `change_pages`) | Save; pages regenerate automatically |
| Change how the documentation is parsed | `tools/parse_docs.py` | Save; pages regenerate automatically |
| Add a new hand-written page | create `docs/my_page.md` and add it to `nav()` in `tools/generate_site.py` | Save |
| Refresh the vanilla game data or sprites | run `npm run data` (downloads the PokeAPI tables and sprites, then regenerates) | |

Never edit files under `docs/pokemon/`, `docs/wild/`, `docs/trainers/`, `docs/changes/` or `docs/SUMMARY.md` by hand: they are regenerated on every build and your edits will be overwritten.

Other scripts:

```bash
npm run generate  # regenerate pages without starting the server
npm run data      # full pipeline including PokeAPI download and sprites (needs internet)
npm run dev:full  # dev server that rebuilds every page on each change (slower, but always exact)
npm run clean     # delete site/
```

## Deploying

`.github/workflows/deploy.yml` builds the site on every push to `main` and publishes it to the `gh-pages` branch with `mkdocs gh-deploy`. After the first run, set **Settings → Pages → Source** to the `gh-pages` branch and the site will be served at `https://<user>.github.io/RRSS/` (update `site_url` in `mkdocs.yml` if the repository name differs).

The site is also on Netlify. `netlify.toml` holds its build settings (they override the ones in the Netlify UI): every push to `main` runs `mkdocs build --strict` and publishes `site/`. Netlify installs `requirements.txt` itself, and the build sets `site_url` to the Netlify address so the 404 page and sitemap point there.

## Credits

- Rising Ruby / Sinking Sapphire and its documentation: **Drayano** ([release thread](https://projectpokemon.org/home/forums/topic/38629-pok%C3%A9mon-rising-ruby-and-sinking-sapphire/)).
- Logos: **kojiyomi**.
- Game data: [PokeAPI](https://github.com/PokeAPI/pokeapi); sprites: [PokeAPI/sprites](https://github.com/PokeAPI/sprites).
- Inspired by Frederic Dlugi's [Platinum Renegade Wiki](https://github.com/FredericDlugi/platinum-renegade-wiki).

Pokémon is © Nintendo, Creatures Inc. and GAME FREAK inc. This is an unofficial fan project; no ROMs or game files are included.
