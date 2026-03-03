"""
World definitions for The Forgotten Depths.
All rooms, items, scenery, and NPCs.
"""


class Item:
    def __init__(self, id, name, description, examine, aliases=None,
                 takeable=True, hidden=False, read_text=None):
        self.id = id
        self.name = name
        self.description = description  # shown in room listing
        self.examine = examine          # shown on 'examine'
        self.aliases = aliases or []
        self.takeable = takeable
        self.hidden = hidden
        self.read_text = read_text

    def matches(self, noun):
        noun = noun.lower()
        if noun == self.id:
            return True
        if noun == self.name.lower():
            return True
        return any(noun == a for a in self.aliases)


class Scenery:
    """Non-takeable objects that can be examined."""
    def __init__(self, id, name, examine, aliases=None):
        self.id = id
        self.name = name
        self.examine = examine
        self.aliases = aliases or []

    def matches(self, noun):
        noun = noun.lower()
        if noun == self.id:
            return True
        if noun == self.name.lower():
            return True
        return any(noun == a for a in self.aliases)


class Room:
    def __init__(self, id, name, description, short_desc=None,
                 exits=None, items=None, scenery=None,
                 dark=False, first_visit_extra=None,
                 blocked=None):
        self.id = id
        self.name = name
        self.description = description
        self.short_desc = short_desc or description
        self.exits = exits or {}
        self.items = items or []
        self.scenery = scenery or []
        self.dark = dark
        self.first_visit_extra = first_visit_extra
        self.visited = False
        self.blocked = blocked or {}  # direction -> (condition_key, message)

    def get_item(self, noun):
        for item in self.items:
            if item.matches(noun):
                return item
        return None

    def get_scenery(self, noun):
        for s in self.scenery:
            if s.matches(noun):
                return s
        return None

    def find_anything(self, noun):
        return self.get_item(noun) or self.get_scenery(noun)


# ---------------------------------------------------------------------------
#  ITEM DEFINITIONS
# ---------------------------------------------------------------------------

def create_items():
    return {
        "lantern": Item(
            "lantern", "brass lantern",
            "Your trusty brass lantern sits here.",
            "A well-worn brass lantern with a glass chimney. The flame flickers "
            "steadily behind the glass. A small gauge on the side shows the oil "
            "level. It looks about three-quarters full.",
            aliases=["brass lantern", "lamp", "light"],
        ),
        "journal": Item(
            "journal", "field journal",
            "Your leather-bound field journal lies here.",
            "A battered leather journal filled with your research notes. Several "
            "pages are bookmarked:\n\n"
            "  Page 12: 'The monastery records mention a complex beneath the "
            "foundations,\n  predating the building by millennia.'\n\n"
            "  Page 34: 'Professor Whitmore believes the builders possessed "
            "knowledge of\n  celestial mechanics far beyond their era. He "
            "sketched a diagram showing\n  planetary positions: Mercury closest "
            "to the sun, then Venus, Earth,\n  Mars -- with Jupiter at the "
            "outermost ring.'\n\n"
            "  Page 51: 'The local legend speaks of \"The Heart\" -- a chamber "
            "where the\n  builders kept their greatest secret. It can only be "
            "opened by one who\n  understands the heavens and speaks the old "
            "words.'",
            aliases=["field journal", "notes", "book"],
            read_text=(
                "You flip through the journal. Three entries catch your eye:\n\n"
                "  Page 12: The monastery was built atop something far older.\n\n"
                "  Page 34: Whitmore's diagram shows planetary order from the sun:\n"
                "  Mercury, Venus, Earth, Mars, Jupiter -- innermost to outermost.\n\n"
                "  Page 51: 'The Heart' requires knowledge of the heavens and\n"
                "  'the old words' to open."
            ),
        ),
        "rope": Item(
            "rope", "coil of rope",
            "A sturdy coil of rope hangs from a wall hook.",
            "About thirty feet of thick hemp rope, well-preserved despite its age. "
            "It looks strong enough to support a person's weight.",
            aliases=["coil of rope", "hemp rope", "coil"],
        ),
        "iron_key": Item(
            "iron_key", "iron key",
            "A heavy iron key lies here.",
            "A large iron key, blackened with age. Its bow is shaped like a "
            "Celtic knot. It looks like it would fit a substantial lock.",
            aliases=["key", "iron key", "heavy key", "black key"],
            hidden=True,
        ),
        "oil_flask": Item(
            "oil_flask", "flask of oil",
            "A small flask of lamp oil sits on the shelf.",
            "A copper flask with a screw-top lid, about half full of clear lamp "
            "oil. Enough to keep a lantern burning for quite some time.",
            aliases=["flask", "oil", "oil flask", "lamp oil", "flask of oil"],
        ),
        "stone_tablet": Item(
            "stone_tablet", "stone tablet",
            "A carved stone tablet rests on the pedestal.",
            "A flat piece of dark stone, about the size of a dinner plate. "
            "Strange symbols are carved into its surface in a grid pattern. "
            "The symbols appear to be: Sun, Moon, Star, Wave -- arranged in "
            "a specific sequence.\n\n"
            "Below the grid, barely legible text reads:\n"
            "  'Walk the path as the sky turns:\n"
            "   First the Sun that lights the day,\n"
            "   Then the Moon that guides the night,\n"
            "   Next the Stars that mark the way,\n"
            "   Last the Wave that shows its might.'",
            aliases=["tablet", "stone tablet", "carved tablet", "stone"],
            read_text=(
                "The tablet reads:\n\n"
                "  'Walk the path as the sky turns:\n"
                "   First the Sun that lights the day,\n"
                "   Then the Moon that guides the night,\n"
                "   Next the Stars that mark the way,\n"
                "   Last the Wave that shows its might.'"
            ),
        ),
        "crystal_lens": Item(
            "crystal_lens", "crystal lens",
            "A polished crystal lens glints in the light.",
            "A perfectly ground lens of clear crystal, about four inches across. "
            "It refracts light into tiny rainbows. One edge has a notch that "
            "looks designed to slot into some kind of mechanism.",
            aliases=["lens", "crystal", "crystal lens"],
        ),
        "bronze_gear": Item(
            "bronze_gear", "bronze gear",
            "A heavy bronze gear lies here.",
            "A thick bronze gear about six inches in diameter, with precisely "
            "cut teeth. Despite its age, the metal is barely tarnished. One "
            "side is stamped with a maker's mark -- a spiral within a circle.",
            aliases=["gear", "bronze gear", "cog"],
            hidden=True,
        ),
        "ancient_coin": Item(
            "ancient_coin", "ancient coin",
            "An ancient coin gleams beneath the water.",
            "A heavy gold coin, far older than any currency you've ever seen. "
            "One side bears a symbol of a sun with seven rays. The other "
            "side shows a spiral -- the same mark as on the bronze gear.",
            aliases=["coin", "ancient coin", "gold coin"],
        ),
        "star_chart": Item(
            "star_chart", "star chart",
            "A star chart lies here, freshly revealed.",
            "A thin sheet of hammered metal, etched with a map of the night sky. "
            "Five constellations are highlighted with special markings. Below "
            "them, symbols spell out a sequence:\n\n"
            "  The Serpent, The Crown, The Flame, The River, The Eye\n\n"
            "These must correspond to positions on some kind of mechanism.",
            aliases=["chart", "star chart", "metal sheet", "constellation chart"],
            read_text=(
                "The star chart shows five highlighted constellations:\n\n"
                "  The Serpent, The Crown, The Flame, The River, The Eye\n\n"
                "They appear to indicate a specific sequence or combination."
            ),
        ),
        "chisel": Item(
            "chisel", "chisel",
            "A well-worn chisel lies here.",
            "A sturdy mason's chisel with a wooden handle. The steel edge "
            "is still surprisingly sharp. Good for prying or breaking stone.",
            aliases=["chisel", "mason's chisel"],
            hidden=True,
        ),
        "whitmore_notebook": Item(
            "whitmore_notebook", "Whitmore's notebook",
            "Professor Whitmore's notebook lies here.",
            "Whitmore's personal research notebook. Most pages are filled with "
            "meticulous observations, but the last entry is hastily scrawled:\n\n"
            "  'I've found it -- The Heart! But I was captured before I could\n"
            "  enter. The final step requires speaking the Invocation aloud\n"
            "  while standing at the altar. The words are carved above the\n"
            "  entrance to the Sanctum:\n\n"
            "     ASTRA CORDIS APERITE\n\n"
            "  Stars, open the Heart. So simple. So elegant.\n"
            "  -- R. Whitmore'",
            aliases=["notebook", "whitmore's notebook", "professor's notebook",
                     "whitmore notebook"],
            read_text=(
                "Whitmore's last entry reads:\n\n"
                "  'The final step requires speaking the Invocation aloud:\n\n"
                "     ASTRA CORDIS APERITE\n\n"
                "  Stars, open the Heart.'"
            ),
        ),
    }


# ---------------------------------------------------------------------------
#  ROOM DEFINITIONS
# ---------------------------------------------------------------------------

def create_rooms(items):
    rooms = {}

    rooms["monastery_ruins"] = Room(
        "monastery_ruins", "Monastery Ruins",
        "You stand among the crumbling walls of an ancient monastery, high in "
        "the Scottish Highlands. Grey stone walls rise around you like broken "
        "teeth against a slate sky. Wind howls through empty window frames. "
        "In the floor of what was once the nave, a dark opening yawns -- a "
        "stairway spiralling down into the earth. Fresh bootprints in the "
        "dust lead downward. Whitmore's prints.",
        short_desc="The crumbling monastery ruins. A dark stairway leads down.",
        exits={"down": "stone_stairway"},
        scenery=[
            Scenery("walls", "crumbling walls",
                    "The monastery walls are made of rough grey granite, crumbling "
                    "with centuries of neglect. Moss and lichen cover the lower stones.",
                    aliases=["wall", "stone walls", "ruins"]),
            Scenery("bootprints", "bootprints",
                    "Fresh bootprints in the dust, size eleven. Whitmore's, unmistakably. "
                    "They lead directly to the stairway.",
                    aliases=["prints", "footprints", "tracks"]),
            Scenery("sky", "sky",
                    "A leaden grey sky threatens rain. The Highland peaks are "
                    "shrouded in mist.",
                    aliases=["clouds", "mist"]),
            Scenery("stairway", "dark stairway",
                    "A narrow stone stairway spirals down into darkness. The steps "
                    "are worn smooth by countless feet over the millennia.",
                    aliases=["stairs", "opening", "entrance", "hole"]),
        ],
    )

    rooms["stone_stairway"] = Room(
        "stone_stairway", "Stone Stairway",
        "A narrow spiral staircase carved from living rock descends into the "
        "earth. The walls are damp and the air grows warmer with each step. "
        "Strange carvings line the walls -- spirals, stars, and symbols in no "
        "language you recognize. The stairway opens into a chamber below.",
        short_desc="The narrow spiral stairway. Up leads to the ruins, down to the antechamber.",
        exits={"up": "monastery_ruins", "down": "antechamber"},
        scenery=[
            Scenery("carvings", "wall carvings",
                    "Spirals and star-patterns are carved deeply into the stone. "
                    "They seem to depict celestial events -- eclipses, planetary "
                    "alignments, perhaps seasons. The craftsmanship is extraordinary.",
                    aliases=["symbols", "spirals", "stars", "markings"]),
            Scenery("walls", "damp walls",
                    "The walls weep with moisture. The stone is ancient -- far "
                    "older than the monastery above.",
                    aliases=["wall", "stone"]),
        ],
    )

    rooms["antechamber"] = Room(
        "antechamber", "The Antechamber",
        "A vaulted chamber opens before you, the first true room of the "
        "underground complex. The ceiling arches fifteen feet overhead, "
        "supported by carved pillars. Three passages lead away: west into a "
        "long hall, east through a low archway, and south into a greenish "
        "glow. A coil of rope hangs from an iron hook on the wall. "
        "The stone stairway rises to the north.",
        short_desc="The vaulted antechamber. Passages lead west, east, and south. Stairs go up.",
        exits={
            "up": "stone_stairway",
            "west": "hall_of_echoes",
            "east": "scriptorium",
            "south": "fungal_grotto",
        },
        items=[items["rope"]],
        scenery=[
            Scenery("pillars", "carved pillars",
                    "Four thick pillars support the ceiling. Each is carved "
                    "with a different motif: flames, waves, stars, and moons. "
                    "They're worn but still beautiful.",
                    aliases=["pillar", "columns", "column"]),
            Scenery("ceiling", "vaulted ceiling",
                    "The ceiling is a perfect stone vault, fitted without mortar. "
                    "How it has stood for millennia is a mystery.",
                    aliases=["vault", "roof"]),
            Scenery("hook", "iron hook",
                    "A sturdy iron hook driven into the wall. A rope hangs from it.",
                    aliases=["wall hook"]),
        ],
    )

    rooms["hall_of_echoes"] = Room(
        "hall_of_echoes", "Hall of Echoes",
        "A long, high-ceilinged corridor stretches before you. The acoustics "
        "are remarkable -- every sound bounces and multiplies into ghostly "
        "whispers. Bronze pipes of varying lengths line the walls, like the "
        "pipes of a vast organ. A breeze passes through them, producing a "
        "low, eerie hum. Three notes seem to dominate: a deep bass drone, "
        "a middle tone, and a high whistle.\n\n"
        "Passages lead east back to the antechamber, south toward a domed "
        "room, and west into a shadowy alcove.",
        short_desc="The long corridor with its whispering echoes. East, south, and west.",
        exits={
            "east": "antechamber",
            "south": "observatory",
            "west": "archive",
        },
        scenery=[
            Scenery("pipes", "bronze pipes",
                    "Dozens of bronze pipes line the walls, ranging from finger-thin "
                    "to arm-thick. Air moves through them constantly, creating tones. "
                    "You notice three pipes are slightly larger and brighter than the "
                    "rest. Their tones correspond to: LOW, MIDDLE, HIGH. The sequence "
                    "seems to repeat: LOW, HIGH, MIDDLE.",
                    aliases=["pipe", "organ pipes", "bronze pipe"]),
            Scenery("echoes", "echoes",
                    "Your own breathing comes back to you in waves. The hall "
                    "amplifies and distorts every sound into something otherworldly.",
                    aliases=["whispers", "sounds", "hum"]),
        ],
    )

    rooms["scriptorium"] = Room(
        "scriptorium", "The Scriptorium",
        "A compact room lined with stone shelves and a heavy writing desk. "
        "This was clearly a place of record-keeping. Stone tablets and "
        "clay cylinders fill the shelves, covered in the same mysterious "
        "script you saw on the stairway. A wooden toolbox sits in the "
        "corner. The desk has a single drawer, slightly ajar.\n\n"
        "The archway leads west back to the antechamber, and a narrow "
        "passage continues south.",
        short_desc="The record-keeping room with its stone desk. West and south.",
        exits={
            "west": "antechamber",
            "south": "forge",
        },
        items=[items["iron_key"], items["chisel"]],
        scenery=[
            Scenery("desk", "writing desk",
                    "A massive stone desk, its surface worn smooth by use. The "
                    "single drawer is slightly open. Inside you can see a heavy "
                    "iron key resting on a bed of dust.",
                    aliases=["stone desk", "writing desk", "table"]),
            Scenery("drawer", "desk drawer",
                    "The drawer slides open with a grinding sound. Inside lies "
                    "a heavy iron key on a bed of ancient dust.",
                    aliases=["desk drawer"]),
            Scenery("shelves", "stone shelves",
                    "Rows of stone tablets and clay cylinders. Most of the "
                    "writing is indecipherable, but some symbols match those "
                    "in your field journal.",
                    aliases=["shelf", "tablets", "cylinders"]),
            Scenery("toolbox", "wooden toolbox",
                    "A surprisingly well-preserved wooden toolbox. Inside you "
                    "find a variety of stone-working tools, most crumbled to "
                    "rust. One chisel, however, remains in excellent condition.",
                    aliases=["box", "tools"]),
        ],
    )

    rooms["fungal_grotto"] = Room(
        "fungal_grotto", "Fungal Grotto",
        "The passage opens into a natural cavern suffused with an eerie "
        "blue-green glow. Enormous fungi -- some taller than you -- sprout "
        "from every surface, their caps pulsing with bioluminescence. The "
        "air is thick and humid, sweet with the smell of decay. A shallow "
        "pool of dark water fills a depression in the floor, and something "
        "glints beneath the surface.\n\n"
        "Passages lead north to the antechamber, south toward the sound "
        "of rushing water, and east into a glittering cavern.",
        short_desc="The bioluminescent fungal cavern. North, south, and east.",
        exits={
            "north": "antechamber",
            "south": "underground_river",
            "east": "crystal_cavern",
        },
        items=[items["ancient_coin"]],
        scenery=[
            Scenery("fungi", "giant fungi",
                    "Enormous mushrooms and shelf fungi cover every surface. Their "
                    "caps pulse with a soft blue-green bioluminescence, bright "
                    "enough to see by even without your lantern. Some caps are "
                    "four feet across.",
                    aliases=["mushrooms", "fungus", "mushroom", "bioluminescence", "glow"]),
            Scenery("pool", "shallow pool",
                    "A shallow pool of dark, still water fills a natural depression. "
                    "The water is surprisingly clear once you look closely. An "
                    "ancient gold coin glints at the bottom, half-buried in silt.",
                    aliases=["water", "dark water", "depression"]),
        ],
    )

    rooms["observatory"] = Room(
        "observatory", "The Observatory",
        "A circular chamber with a high domed ceiling. The dome is covered "
        "in thousands of tiny reflective stones set into the rock, forming "
        "a breathtaking map of the night sky. In the center of the room "
        "stands a magnificent brass orrery -- a mechanical model of the "
        "solar system -- though several of its arms hang limp and one "
        "socket where a lens should sit is conspicuously empty.\n\n"
        "Passages lead north to the Hall of Echoes and south to another "
        "chamber.",
        short_desc="The domed observatory with its brass orrery. North and south.",
        exits={
            "north": "hall_of_echoes",
            "south": "puzzle_chamber",
        },
        scenery=[
            Scenery("dome", "domed ceiling",
                    "Thousands of tiny quartz crystals are embedded in the dome, "
                    "each one positioned to mirror a real star. The effect is "
                    "stunning -- like standing beneath the open sky.",
                    aliases=["ceiling", "stars", "sky", "crystals"]),
            Scenery("orrery", "brass orrery",
                    "A beautiful mechanical orrery on a stone pedestal. Five "
                    "concentric brass rings represent planetary orbits. Small "
                    "spheres sit on arms at various positions. The innermost "
                    "ring is empty -- a socket waits for something round, "
                    "like a lens. A crank on the side would rotate the rings.\n\n"
                    "The current positions look random and wrong.",
                    aliases=["mechanism", "model", "brass orrery", "solar system",
                             "pedestal", "rings", "crank"]),
        ],
    )

    rooms["archive"] = Room(
        "archive", "The Archive",
        "A small, dry chamber lined floor to ceiling with narrow stone "
        "shelves. Hundreds of stone cylinders rest in their slots, each "
        "one a record of something long forgotten. In the center of the "
        "room, a low stone pedestal holds a single carved tablet, "
        "displayed as if it were the most important text in the collection.\n\n"
        "The only exit leads east.",
        short_desc="The archive of stone cylinders. A tablet sits on the central pedestal. East.",
        exits={"east": "hall_of_echoes"},
        items=[items["stone_tablet"]],
        scenery=[
            Scenery("pedestal", "stone pedestal",
                    "A waist-high pedestal of polished black stone. The carved "
                    "tablet resting on it has been placed with obvious reverence.",
                    aliases=["plinth", "stand"]),
            Scenery("cylinders", "stone cylinders",
                    "Hundreds of cylinders, each about a foot long, carved with "
                    "fine text in that same unknown script. These must be the "
                    "records of an entire civilization.",
                    aliases=["records", "scrolls", "shelves", "shelf"]),
        ],
        dark=True,
    )

    rooms["forge"] = Room(
        "forge", "The Forge",
        "Waves of warmth wash over you. This chamber houses an ancient "
        "forge -- and impossibly, it still radiates heat, though no fire "
        "burns. The anvil gleams as if recently used. Racks of tools line "
        "one wall, most corroded beyond use. A heavy workbench dominates "
        "the far side, its drawers sealed shut with age. A shelf near "
        "the entrance holds several containers.\n\n"
        "Passages lead north to the scriptorium and south deeper into "
        "the complex.",
        short_desc="The warm forge. Tools, a workbench, and an impossible heat. North and south.",
        exits={
            "north": "scriptorium",
            "south": "mechanism_room",
        },
        items=[items["oil_flask"], items["bronze_gear"]],
        scenery=[
            Scenery("forge_itself", "the forge",
                    "The forge basin is empty -- no coals, no fuel -- yet it "
                    "radiates steady heat. You can feel it from several feet "
                    "away. Whatever powers it is beyond your understanding.",
                    aliases=["forge", "basin", "fire", "heat"]),
            Scenery("anvil", "anvil",
                    "A heavy iron anvil, its surface mirror-smooth from use. "
                    "Not a speck of rust.",
                    aliases=["iron anvil"]),
            Scenery("workbench", "workbench",
                    "A massive wooden workbench, somehow preserved. One of its "
                    "drawers is jammed but could be forced open. Through a gap "
                    "you can see something bronze inside.",
                    aliases=["bench", "drawers", "drawer"]),
            Scenery("shelf", "shelf",
                    "A stone shelf near the entrance. Among the debris you "
                    "spot a small copper flask that looks intact.",
                    aliases=["shelves", "containers", "rack"]),
            Scenery("tools", "tool racks",
                    "Racks of ancient tools. Hammers, tongs, files -- most "
                    "have corroded to uselessness, but the craftsmanship "
                    "was clearly extraordinary.",
                    aliases=["racks", "tool rack", "tool"]),
        ],
    )

    rooms["crystal_cavern"] = Room(
        "crystal_cavern", "Crystal Cavern",
        "A natural cave glittering with enormous crystal formations. "
        "Translucent pillars of quartz and amethyst rise from floor "
        "to ceiling, splitting your lantern light into a thousand "
        "prismatic fragments. The effect is dazzling. Embedded in the "
        "wall at eye level, set into a niche as if placed there "
        "deliberately, is a perfectly round crystal lens.\n\n"
        "The passage leads west back to the Fungal Grotto.",
        short_desc="The dazzling crystal cave. A crystal lens is set in the wall. West.",
        exits={"west": "fungal_grotto"},
        items=[items["crystal_lens"]],
        scenery=[
            Scenery("formations", "crystal formations",
                    "Massive crystals of quartz and amethyst, some as tall as "
                    "pillars. They hum faintly when you touch them, resonating "
                    "with a frequency you can feel in your teeth.",
                    aliases=["crystals", "quartz", "amethyst", "pillars"]),
            Scenery("niche", "wall niche",
                    "A precisely carved niche in the cave wall, clearly artificial "
                    "among the natural formations. A crystal lens has been placed "
                    "here with great care.",
                    aliases=["wall", "alcove"]),
        ],
    )

    rooms["underground_river"] = Room(
        "underground_river", "Underground River",
        "The passage ends at the bank of a fast-flowing underground river. "
        "The water is black and cold, rushing from east to west through a "
        "channel carved over eons. The current looks treacherous. A thick "
        "stone pillar stands at the water's edge, its surface worn smooth. "
        "Across the river, you can see the passage continuing south.\n\n"
        "The way back north leads to the Fungal Grotto.",
        short_desc="The rushing underground river. A stone pillar stands at the bank. North.",
        exits={
            "north": "fungal_grotto",
            "south": "flooded_chamber",
        },
        blocked={
            "south": ("river_crossed", "The river rushes past, cold and "
                      "treacherous. You'll need to find a way to cross safely."),
        },
        scenery=[
            Scenery("river", "underground river",
                    "Black water rushes past with surprising force. The river "
                    "is about twenty feet wide. Attempting to swim it would "
                    "be extremely dangerous.",
                    aliases=["water", "current", "stream"]),
            Scenery("pillar", "stone pillar",
                    "A thick stone pillar, about waist-high, standing right at "
                    "the river's edge. It's been worn smooth by centuries of "
                    "spray. A rope tied here could serve as a lifeline across.",
                    aliases=["stone pillar", "post"]),
        ],
    )

    rooms["flooded_chamber"] = Room(
        "flooded_chamber", "Flooded Chamber",
        "This large chamber is partially submerged in dark, still water. "
        "The flood reaches mid-thigh in most places and deeper in others. "
        "Carved walls rise above the waterline, covered in more of those "
        "mysterious symbols. The architecture suggests this room was never "
        "meant to be flooded -- something has changed over the millennia.\n\n"
        "The river crossing lies to the north. A passage south is blocked "
        "by the water level -- it's completely submerged.",
        short_desc="The partially flooded chamber. Passages north; south is submerged.",
        exits={
            "north": "underground_river",
            "south": "deep_stair",
        },
        blocked={
            "south": ("chamber_drained", "The southern passage is completely "
                      "submerged. The water level would need to drop significantly "
                      "before you could pass."),
        },
        scenery=[
            Scenery("water_here", "flood water",
                    "Dark, cold water fills the chamber to mid-thigh depth. It's "
                    "still -- not flowing like the river. Something is holding "
                    "it in. If it could be drained somehow...",
                    aliases=["water", "flood", "pool"]),
            Scenery("symbols_here", "carved symbols",
                    "The symbols above the waterline match those elsewhere in the "
                    "complex -- spirals, stars, celestial imagery.",
                    aliases=["symbols", "walls", "carvings"]),
        ],
    )

    rooms["puzzle_chamber"] = Room(
        "puzzle_chamber", "Puzzle Chamber",
        "A square chamber with a floor divided into a four-by-four grid of "
        "stone tiles. Each tile is engraved with a symbol: Suns, Moons, "
        "Stars, and Waves, four of each, arranged in rows. The tiles click "
        "subtly underfoot -- they're pressure-sensitive. On the far wall, "
        "a massive stone door blocks the way south. It has no handle, no "
        "keyhole. Only the grid stands between you and whatever lies beyond.\n\n"
        "The passage north leads back to the observatory.",
        short_desc="The tile puzzle room. The great stone door blocks the south. North.",
        exits={
            "north": "observatory",
            "south": "deep_stair",
        },
        blocked={
            "south": ("floor_puzzle_solved", "The massive stone door is sealed shut. "
                      "The floor tiles must hold the key to opening it."),
        },
        scenery=[
            Scenery("tiles", "floor tiles",
                    "Sixteen stone tiles in a four-by-four grid. Each is about "
                    "two feet square and engraved with one of four symbols:\n\n"
                    "  Row 1: Sun  Moon  Star  Wave\n"
                    "  Row 2: Wave Sun   Moon  Star\n"
                    "  Row 3: Star Wave  Sun   Moon\n"
                    "  Row 4: Moon Star  Wave  Sun\n\n"
                    "They click when stepped on. You need to step on them in "
                    "the right sequence.",
                    aliases=["tile", "grid", "floor", "symbols"]),
            Scenery("stone_door", "stone door",
                    "A massive slab of stone, perfectly fitted into the wall. "
                    "No hinges, no handle. It must be opened by the floor puzzle.",
                    aliases=["door", "slab", "south door"]),
        ],
    )

    rooms["mechanism_room"] = Room(
        "mechanism_room", "The Mechanism Room",
        "A cavernous chamber dominated by a towering mechanical apparatus. "
        "Massive bronze gears, some six feet across, interlock in a complex "
        "arrangement. Three heavy levers protrude from a control panel on "
        "the wall, each labeled with a symbol: a circle (LOW), a triangle "
        "(HIGH), and a square (MIDDLE). One gear appears to be missing from "
        "the mechanism -- an empty axle waits.\n\n"
        "A channel in the floor leads south, toward what sounds like "
        "standing water. The passage north returns to the forge.",
        short_desc="The great mechanism. Three levers and a missing gear. North.",
        exits={"north": "forge"},
        scenery=[
            Scenery("mechanism", "mechanical apparatus",
                    "A vast clockwork mechanism of interlocking bronze gears. Its "
                    "purpose seems to be pumping or draining -- the channel in the "
                    "floor connects to chambers below. One gear axle is empty, "
                    "waiting for a gear about six inches in diameter.",
                    aliases=["apparatus", "gears", "clockwork", "machine", "device"]),
            Scenery("levers", "three levers",
                    "Three heavy bronze levers on the control panel:\n"
                    "  Left lever:   marked with a circle  (LOW)\n"
                    "  Middle lever: marked with a triangle (HIGH)\n"
                    "  Right lever:  marked with a square   (MIDDLE)\n\n"
                    "All three are currently in the UP position.",
                    aliases=["lever", "controls", "panel", "control panel"]),
            Scenery("axle", "empty axle",
                    "A bare axle protrudes from the mechanism. A gear of about "
                    "six inches in diameter would fit perfectly here.",
                    aliases=["empty axle", "shaft", "spindle"]),
            Scenery("channel", "floor channel",
                    "A deep channel carved into the floor, leading south. It "
                    "connects to the flooded areas below.",
                    aliases=["drain", "groove", "trough"]),
        ],
    )

    rooms["deep_stair"] = Room(
        "deep_stair", "The Deep Stair",
        "You stand at a landing where two staircases meet. One rises to "
        "the north, the other descends further into the earth. The air "
        "here is heavy and old, carrying a faint metallic tang. The walls "
        "are carved with elaborate scenes -- figures kneeling before a "
        "great light, celestial bodies in alignment, and at the center "
        "of it all, a stylized heart shape pulsing with rays.\n\n"
        "Stairs lead up to the north, a passage goes south, and a "
        "stairway descends further down.",
        short_desc="The deep landing. Stairs up (north), passage south, stairs down.",
        exits={
            "north": "puzzle_chamber",
            "south": "prison_cells",
            "down": "sanctum",
        },
        dark=True,
        scenery=[
            Scenery("scenes", "carved scenes",
                    "Elaborate carvings depict what must be the builders' history "
                    "or mythology. Robed figures kneel before a brilliant light "
                    "source. The planets align. At the center, a heart shape "
                    "radiates power. It's beautiful and unsettling.",
                    aliases=["carvings", "figures", "walls", "wall carvings"]),
        ],
    )

    rooms["prison_cells"] = Room(
        "prison_cells", "Prison Cells",
        "A grim corridor lined with small stone cells, each sealed by a "
        "heavy iron door. Most stand open and empty. But from the last "
        "cell on the right, you hear a voice -- hoarse but unmistakable.\n\n"
        "\"Elara? Is that you? Thank God! I'm in here -- the door is "
        "locked. Some kind of mechanism triggered when I entered. Please, "
        "you must get me out!\"\n\n"
        "Professor Whitmore presses his face against the small barred "
        "window in the cell door. He looks exhausted but unharmed.\n\n"
        "The passage leads north back to the Deep Stair.",
        short_desc="The prison cells. Whitmore is locked in the last cell. North.",
        exits={"north": "deep_stair"},
        dark=True,
        scenery=[
            Scenery("cells", "stone cells",
                    "Small, bare stone cells with heavy iron doors. Most are "
                    "open. The last one is locked tight.",
                    aliases=["cell", "doors", "corridor"]),
            Scenery("cell_door", "Whitmore's cell door",
                    "A heavy iron door with a barred window. The lock is a "
                    "large, crude mechanism -- it takes an iron key, or "
                    "enough force might break the rusted hinges.",
                    aliases=["locked door", "iron door", "door", "lock",
                             "hinges", "window", "bars"]),
            Scenery("whitmore_npc", "Professor Whitmore",
                    "Professor Reginald Whitmore -- your colleague, mentor, and "
                    "friend. He's disheveled and tired but his eyes are bright "
                    "with excitement despite his predicament.",
                    aliases=["whitmore", "professor", "reginald", "man"]),
        ],
    )

    rooms["sanctum"] = Room(
        "sanctum", "The Sanctum",
        "You descend into a vast, cathedral-like space. The walls soar "
        "upward into darkness. Everything here is carved from obsidian -- "
        "black, gleaming stone that reflects your lantern light like "
        "dark mirrors. At the center stands an altar of white marble, "
        "startlingly bright against the black. Five concentric rings of "
        "bronze are set into the altar's surface, each one able to rotate "
        "independently. Above the southern archway, words are carved in "
        "large letters:\n\n"
        "     ASTRA CORDIS APERITE\n\n"
        "The passage south leads to a sealed door of extraordinary "
        "craftsmanship. The stairs lead back up.",
        short_desc="The obsidian sanctum with its white altar and bronze rings. Up and south.",
        exits={
            "up": "deep_stair",
            "south": "the_heart",
        },
        blocked={
            "south": ("heart_unlocked", "The southern door is sealed. The altar "
                      "mechanism must be the key."),
        },
        dark=True,
        scenery=[
            Scenery("altar", "white altar",
                    "A perfect cube of white marble, three feet on each side. "
                    "Five concentric bronze rings are set into its top surface, "
                    "each engraved with constellation names. They can be "
                    "rotated independently. There's a small round depression "
                    "in the very center -- coin-sized.",
                    aliases=["marble altar", "cube", "marble"]),
            Scenery("rings", "bronze rings",
                    "Five rotating rings, each marked with constellation names:\n"
                    "  The Serpent, The Crown, The Flame, The River, The Eye,\n"
                    "  The Bear, The Hawk, The Ship, The Sword, The Gate\n\n"
                    "They need to be set in the correct sequence from inner "
                    "to outer ring.",
                    aliases=["ring", "concentric rings", "bronze ring"]),
            Scenery("inscription", "carved inscription",
                    "Above the southern archway, in letters six inches tall:\n\n"
                    "     ASTRA CORDIS APERITE\n\n"
                    "Your Latin is rusty, but: 'Stars, open the Heart.'",
                    aliases=["words", "text", "latin", "letters", "archway"]),
            Scenery("depression", "round depression",
                    "A small circular depression in the center of the altar, "
                    "about the size of a large coin.",
                    aliases=["slot", "hole", "indent", "center"]),
        ],
    )

    rooms["the_heart"] = Room(
        "the_heart", "The Heart",
        "You step into a perfectly spherical chamber carved from rose-red "
        "stone. The room pulses with a warm light that has no visible "
        "source -- it emanates from the stone itself, like a heartbeat "
        "made visible. In the exact center of the sphere, suspended by "
        "nothing at all, hangs a crystalline orb the size of a human "
        "head, slowly rotating. Inside the orb, points of light drift "
        "like trapped stars.\n\n"
        "This is it. The Heart of the complex. The builders' greatest "
        "secret.\n\n"
        "A passage leads north back to the Sanctum.",
        short_desc="The Heart -- the rose-red spherical chamber with its floating orb.",
        exits={"north": "sanctum"},
        scenery=[
            Scenery("orb", "crystalline orb",
                    "A sphere of perfect crystal, suspended in mid-air by forces "
                    "you cannot explain. Inside it, motes of light drift like "
                    "stars in a private universe. It is beautiful beyond words.\n\n"
                    "You sense that touching it would end your journey here -- "
                    "for better or worse.",
                    aliases=["crystal", "sphere", "crystal orb", "ball", "light",
                             "stars", "heart"]),
            Scenery("walls_heart", "rose-red walls",
                    "The walls pulse with warm light, like blood through living "
                    "tissue. This chamber is alive in some way you cannot fathom.",
                    aliases=["walls", "stone", "wall", "chamber"]),
        ],
    )

    return rooms


def build_world():
    items = create_items()
    rooms = create_rooms(items)
    return rooms, items
