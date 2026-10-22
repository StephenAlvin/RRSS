# FAQ

Answers to common questions, mostly drawn from the notes in Drayano's documentation.

## Which version of the hack does this wiki cover?

The documentation bundled with **v2.1.0** (October 2016), the latest release. Rising Ruby and Sinking Sapphire share the same documents; the version differences are the same as between Omega Ruby and Alpha Sapphire (Team Magma or Team Aqua, Groudon or Kyogre), and the wild lists are shared.

## Should I turn off the Exp. Share?

Yes, unless you want an easier game. Trainer levels were designed for a full team of six **without** the Exp. Share. You still receive it in Petalburg Woods and it is on by default, so switch it off from the bag.

## Why does the DexNav not show every Pokémon on a route?

Each area has data for 10 or more species, but the DexNav only has a fixed number of slots, so it cannot display them all. The species that do appear are the ones earlier in the internal lists, and Drayano arranged these so that Pokémon with the most desirable hidden abilities are the ones you can search for.

## How do encounter rates work?

Every grass, cave or sand area has at least ten species with a 10% chance each. Areas with eleven species have two at 5% instead; those are marked as rare on this wiki. Pokémon in grass have a fixed level for the route, which the White and Black Flutes can modify.

## Where are the starters and other horde-only Pokémon?

Some species such as the starters of every region, Eevee, Plusle and Minun only appear in **horde battles**. Trigger hordes with Honey or Sweet Scent; early Pokémon that already know Sweet Scent include Bellsprout, Surskit, Swirlix and Spritzee.

## What are the DexNav-only Pokémon?

The species listed under the DexNav method only appear late in the game, after the Groudon or Kyogre conflict in the Cave of Origin is over. They replace the foreign Pokémon that appeared on routes in the original games and are usually high-levelled evolved forms of something native to that route.

## Where are the legendary Pokémon?

Most legendaries live on the **Mirage spots**, with a fixed set per terrain type (forest, cave, mountain, island) regardless of which island you visit. See the [Mirage Forest](wild/mirage_forest_any.md), [Mirage Cave](wild/mirage_cave_any.md), [Mirage Mountain](wild/mirage_mountain_any.md) and [Mirage Island](wild/mirage_island_any.md) pages. The static legendaries from the original games (the Regis, Rayquaza, the soaring encounters and so on) were kept, with higher levels; see [gifts and static encounters](changes/gifts_and_statics.md).

## What do the asterisks on moves and abilities mean?

- `*` (one asterisk): the Pokémon can learn this move in the official games, but not by level up. It comes from egg moves, TMs/HMs or tutors. These moves are also present in the legal-moves version.
- `**` (two asterisks): the Pokémon cannot normally learn this move or have this ability at all. These are removed in the legal-moves version of the hack.

## What is the "legal moves" version?

An alternate set of files that leaves out everything marked with two asterisks, so that Pokémon can be transferred or used without illegal movesets. Boss trainers have an alternate file too, with their illegal moves replaced by legal options. A version of the evolution file without the lowered evolution levels is also offered, but level-up movesets assume the lowered levels.

## What is the DllField.cro file and why does it matter?

The gift and static encounter changes (perfect-IV starters and fossils, higher-level legendaries, the soaring encounters) live in a modified `DllField.cro`. Using it requires a loader that can patch the RO module, which Luma3DS and Citra can do but Gateway and HANS cannot. Without the file the game still works; you just do not get those particular changes.

## How do trade evolutions work now?

Nothing needs to be traded. Pokémon that evolved by plain trading now evolve by level-up with high friendship **or** at a set level, whichever comes first. Trade-with-item evolutions now use the item like an evolution stone. Karrablast and Shelmet evolve by levelling up with the other species in your party. Trading still works as well. See [evolution changes](changes/evolutions.md).

## Where do I buy evolution items and Mega Stones?

Evolution stones are sold at the Slateport Poké Mart and Fallarbor Poké Mart; trade items such as the King's Rock and Metal Coat are at the Slateport Market; later items such as the Electirizer and Reaper Cloth are on the third floor of the Lilycove Department Store. Mega Stones appear in every Poké Mart once you have six badges, with more after eight. Salamencite and Diancite are held by wild Shelgon/Salamence and Diancie instead. See [items and shops](changes/items.md).

## Why can't I buy vitamins or X items?

Shop inventories are limited in size, so vitamins and X items were dropped to make room for evolution items, Mega Stones and TMs. Vitamins can still be bought from the Battle Resort stalls; X items that are not found on the ground are no longer available.

## Who do the Battle Resort trainers mimic?

The post-game trainers at the Battle Resort copy the teams of famous trainers from other regions, such as Cynthia, Lance and Diantha, as well as rematches that mirror Hoenn's own Gym Leaders. See the [Battle Resort](trainers/battle_resort.md) page.

## I found a mistake on this wiki

The pages are generated from the documentation, so errors are usually either typos in the original documents or bugs in the generator. Please open an issue on [GitHub](https://github.com/StephenAlvin/RRSS).
