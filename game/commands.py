"""
Command handlers for The Forgotten Depths.
Each handler receives (game_state, parsed_command) and returns a string response.
"""

from game.utils import bold, dim, italic, wrap


MAX_INVENTORY = 8


# ---------------------------------------------------------------------------
#  MOVEMENT
# ---------------------------------------------------------------------------

def cmd_go(gs, cmd):
    direction = cmd.noun
    if not direction:
        return "Go where? Try a direction like NORTH, SOUTH, EAST, WEST, UP, or DOWN."

    room = gs.current_room()

    if direction not in room.exits:
        return f"You can't go {direction} from here."

    # Check blocked exits
    if direction in room.blocked:
        condition_key, message = room.blocked[direction]
        if not gs.flags.get(condition_key, False):
            return message

    dest_id = room.exits[direction]
    gs.player["room"] = dest_id
    gs.player["turns"] += 1
    _consume_oil(gs)

    return cmd_look(gs, cmd, force_long=not gs.rooms[dest_id].visited)


# ---------------------------------------------------------------------------
#  OBSERVATION
# ---------------------------------------------------------------------------

def cmd_look(gs, cmd, force_long=False):
    room = gs.current_room()

    if room.dark and not _has_light(gs):
        return ("It is pitch dark. You are likely to be eaten by a grue.\n"
                "(You need a light source to see here.)")

    room.visited = True
    gs.visit_room(room.id)

    lines = []
    lines.append("")
    lines.append(bold(f"--- {room.name} ---"))

    if force_long or cmd.verb == "look":
        lines.append(wrap(room.description))
    else:
        lines.append(wrap(room.short_desc))

    visible_items = [i for i in room.items if not i.hidden]
    if visible_items:
        lines.append("")
        for item in visible_items:
            lines.append(f"  {item.description}")

    exit_dirs = ", ".join(room.exits.keys())
    lines.append(dim(f"\n[Exits: {exit_dirs}]"))

    return "\n".join(lines)


def cmd_examine(gs, cmd):
    if not cmd.noun:
        return "Examine what?"

    room = gs.current_room()

    if room.dark and not _has_light(gs):
        return "It's too dark to see anything."

    # Check inventory first
    item = _find_in_inventory(gs, cmd.noun)
    if item:
        return item.examine

    # Check room items
    item = room.get_item(cmd.noun)
    if item:
        if item.hidden:
            _reveal_item(gs, room, item)
        return item.examine

    # Check scenery
    scenery = room.get_scenery(cmd.noun)
    if scenery:
        _check_scenery_reveals(gs, room, scenery)
        return scenery.examine

    return "You don't see that here."


# ---------------------------------------------------------------------------
#  ITEMS
# ---------------------------------------------------------------------------

def cmd_take(gs, cmd):
    if not cmd.noun:
        return "Take what?"

    room = gs.current_room()
    item = room.get_item(cmd.noun)

    if not item:
        # Maybe it's scenery
        if room.get_scenery(cmd.noun):
            return "You can't take that."
        return "You don't see that here."

    if not item.takeable:
        return "You can't take that."

    if len(gs.player["inventory"]) >= MAX_INVENTORY:
        return "You're carrying too much. Drop something first."

    if item.hidden:
        item.hidden = False

    room.items.remove(item)
    gs.player["inventory"].append(item)
    return f"Taken: {item.name}."


def cmd_drop(gs, cmd):
    if not cmd.noun:
        return "Drop what?"

    item = _find_in_inventory(gs, cmd.noun)
    if not item:
        return "You're not carrying that."

    gs.player["inventory"].remove(item)
    gs.current_room().items.append(item)
    return f"Dropped: {item.name}."


def cmd_inventory(gs, cmd):
    inv = gs.player["inventory"]
    if not inv:
        return "You are empty-handed."

    lines = ["You are carrying:"]
    for item in inv:
        lines.append(f"  {item.name}")

    oil = gs.player.get("lantern_oil", 0)
    if oil > 0:
        pct = int((oil / 80) * 100)
        lines.append(f"\n  {dim(f'[Lantern oil: ~{pct}%]')}")
    return "\n".join(lines)


# ---------------------------------------------------------------------------
#  READ
# ---------------------------------------------------------------------------

def cmd_read(gs, cmd):
    if not cmd.noun:
        return "Read what?"

    item = _find_in_inventory(gs, cmd.noun)
    if not item:
        item = gs.current_room().get_item(cmd.noun)

    if not item:
        return "You don't see that here."

    if item.read_text:
        return item.read_text
    return f"There's nothing written on the {item.name}."


# ---------------------------------------------------------------------------
#  USE / INTERACT
# ---------------------------------------------------------------------------

def cmd_use(gs, cmd):
    if not cmd.noun:
        return "Use what?"

    item = _find_in_inventory(gs, cmd.noun)
    if not item:
        return "You're not carrying that."

    target = cmd.obj
    room = gs.current_room()

    # --- OIL FLASK on LANTERN ---
    if item.id == "oil_flask" and (not target or _noun_matches(target, "lantern")):
        return _use_oil(gs)

    # --- ROPE at UNDERGROUND RIVER ---
    if item.id == "rope":
        return _use_rope(gs, room)

    # --- CRYSTAL LENS on ORRERY ---
    if item.id == "crystal_lens":
        return _use_lens(gs, room)

    # --- BRONZE GEAR on MECHANISM ---
    if item.id == "bronze_gear":
        return _use_gear(gs, room)

    # --- IRON KEY on CELL DOOR ---
    if item.id == "iron_key":
        return _use_iron_key(gs, room)

    # --- CHISEL on CELL DOOR ---
    if item.id == "chisel":
        return _use_chisel(gs, room)

    # --- ANCIENT COIN on ALTAR ---
    if item.id == "ancient_coin":
        return _use_coin(gs, room)

    # --- STAR CHART on RINGS ---
    if item.id == "star_chart":
        return _use_star_chart(gs, room)

    if target:
        return f"Using the {item.name} on that doesn't seem to accomplish anything."
    return f"You're not sure how to use the {item.name} here."


def cmd_open(gs, cmd):
    if not cmd.noun:
        return "Open what?"

    room = gs.current_room()

    # Open desk drawer in scriptorium
    if room.id == "scriptorium" and cmd.noun in ("desk", "drawer", "desk drawer"):
        key = gs.items["iron_key"]
        if key.hidden:
            key.hidden = False
            return ("You pull the drawer fully open. Inside, resting on a bed "
                    "of ancient dust, is a heavy iron key.")
        return "The drawer is already open."

    # Open workbench drawer in forge
    if room.id == "forge" and cmd.noun in ("workbench", "drawer", "drawers", "bench"):
        gear = gs.items["bronze_gear"]
        if gear.hidden:
            gear.hidden = False
            return ("You wrench the drawer open with a grinding protest. Inside "
                    "lies a bronze gear, about six inches across, perfectly preserved.")
        return "The drawer is already open."

    # Open toolbox in scriptorium
    if room.id == "scriptorium" and cmd.noun in ("toolbox", "box", "tools"):
        chisel = gs.items["chisel"]
        if chisel.hidden:
            chisel.hidden = False
            return ("You open the toolbox. Most of the tools inside have rusted "
                    "to nothing, but a sturdy chisel remains in excellent condition.")
        return "The toolbox is already open."

    return "You can't open that."


def cmd_pull(gs, cmd):
    if not cmd.noun:
        return "Pull what?"
    room = gs.current_room()

    if room.id == "mechanism_room" and cmd.noun in ("lever", "levers"):
        return ("There are three levers. Try PULL LEFT LEVER, PULL MIDDLE LEVER, "
                "or PULL RIGHT LEVER. (Or examine them for details.)")

    if room.id == "mechanism_room":
        return _pull_lever(gs, cmd.noun)

    return "You can't pull that."


def cmd_push(gs, cmd):
    if not cmd.noun:
        return "Push what?"
    return "Pushing that doesn't accomplish anything."


def cmd_turn(gs, cmd):
    if not cmd.noun:
        return "Turn what?"

    room = gs.current_room()

    # Turn crank on orrery
    if room.id == "observatory" and cmd.noun in ("crank", "orrery", "rings"):
        return _turn_orrery(gs)

    return "You can't turn that."


def cmd_tie(gs, cmd):
    if not cmd.noun:
        return "Tie what?"

    item = _find_in_inventory(gs, cmd.noun)
    if item and item.id == "rope":
        return _use_rope(gs, gs.current_room())

    return "You can't tie that."


def cmd_insert(gs, cmd):
    if not cmd.noun:
        return "Insert what?"

    item = _find_in_inventory(gs, cmd.noun)
    if not item:
        return "You're not carrying that."

    return cmd_use(gs, cmd)


def cmd_place(gs, cmd):
    return cmd_use(gs, cmd)


def cmd_set(gs, cmd):
    return cmd_use(gs, cmd)


def cmd_climb(gs, cmd):
    return "There's nothing here that warrants climbing."


# ---------------------------------------------------------------------------
#  STEP (for the floor puzzle)
# ---------------------------------------------------------------------------

def cmd_step(gs, cmd):
    noun = cmd.noun or ""
    # Handle "step on sun" -> strip "on"
    if noun.startswith("on "):
        noun = noun[3:]
    if cmd.prep == "on" and cmd.obj:
        noun = cmd.obj

    if not noun:
        return "Step where?"

    room = gs.current_room()
    if room.id != "puzzle_chamber":
        return "There's nothing special to step on here."

    return _step_on_tile(gs, noun)


# ---------------------------------------------------------------------------
#  TALK
# ---------------------------------------------------------------------------

def cmd_talk(gs, cmd):
    room = gs.current_room()

    if room.id == "prison_cells" and not gs.flags.get("whitmore_freed"):
        return (
            "Whitmore speaks urgently through the bars:\n\n"
            "\"Elara, listen -- this place is beyond anything we imagined. "
            "The builders weren't just astronomers, they were... something "
            "more. I found a chamber below -- The Heart, they call it. It's "
            "the center of everything.\n\n"
            "But I triggered a trap and ended up in here. The door needs "
            "an iron key -- I saw one in the scriptorium upstairs, in the "
            "desk drawer. Or if you have a chisel, the hinges are rusted "
            "enough to break.\n\n"
            "Please hurry. And bring my notebook when you free me -- my "
            "notes on The Heart are critical.\""
        )

    if room.id == "prison_cells" and gs.flags.get("whitmore_freed"):
        return (
            "Whitmore nods thoughtfully. \"You have everything you need, "
            "I think. The Sanctum is below us. The altar there is the "
            "final lock. Remember: the coin, the constellations, and "
            "the invocation. Good luck, Elara.\""
        )

    return "There's no one here to talk to."


# ---------------------------------------------------------------------------
#  SAY (for the invocation)
# ---------------------------------------------------------------------------

def cmd_say(gs, cmd):
    if not cmd.noun:
        return "Say what?"

    room = gs.current_room()

    if room.id == "sanctum":
        phrase = cmd.noun.strip().lower()
        if "astra" in phrase and "cordis" in phrase and "aperite" in phrase:
            return _speak_invocation(gs)
        return "Your words echo through the obsidian chamber, but nothing happens."

    if room.id == "the_heart":
        return "Your voice is swallowed by the pulsing light. The orb drifts silently."

    return f"You say \"{cmd.noun}\" aloud. Nothing happens."


# ---------------------------------------------------------------------------
#  SENSORY
# ---------------------------------------------------------------------------

def cmd_listen(gs, cmd):
    room = gs.current_room()
    responses = {
        "hall_of_echoes": "Three tones dominate the eerie hum: LOW, HIGH, MIDDLE -- repeating in that order.",
        "underground_river": "The roar of the river echoes off the stone walls.",
        "fungal_grotto": "A faint popping and hissing as the fungi release spores.",
        "the_heart": "A deep, rhythmic thrum -- like a heartbeat -- fills the chamber.",
        "monastery_ruins": "Wind howls through the ruins. Far below, silence.",
    }
    return responses.get(room.id, "You listen carefully but hear nothing unusual.")


def cmd_smell(gs, cmd):
    room = gs.current_room()
    responses = {
        "fungal_grotto": "Sweet decay and damp earth. Not unpleasant, but heavy.",
        "forge": "Hot metal and ancient stone. The heat carries a faint sulfurous tang.",
        "the_heart": "Ozone and something floral you can't identify.",
    }
    return responses.get(room.id, "Nothing remarkable.")


def cmd_touch(gs, cmd):
    if not cmd.noun:
        return "Touch what?"

    room = gs.current_room()
    if room.id == "the_heart" and cmd.noun in ("orb", "crystal", "sphere", "ball", "heart"):
        return _touch_orb(gs)

    return "You touch it. It feels about how you'd expect."


def cmd_swim(gs, cmd):
    room = gs.current_room()
    if room.id == "underground_river":
        return _try_swim(gs)
    if room.id == "flooded_chamber":
        return "The water is cold and chest-deep in places. You wade through it."
    return "There's nothing to swim in here."


def cmd_jump(gs, cmd):
    return "You jump on the spot. Nothing useful happens."


def cmd_enter(gs, cmd):
    return "You'll need to be more specific about where you want to go."


def cmd_eat(gs, cmd):
    return "That doesn't seem edible."


def cmd_drink(gs, cmd):
    room = gs.current_room()
    if room.id in ("underground_river", "flooded_chamber"):
        return "The water doesn't look remotely safe to drink."
    return "There's nothing drinkable here."


def cmd_taste(gs, cmd):
    return "Better not."


def cmd_wait(gs, cmd):
    gs.player["turns"] += 1
    _consume_oil(gs)
    return "Time passes."


# ---------------------------------------------------------------------------
#  META
# ---------------------------------------------------------------------------

def cmd_help(gs, cmd):
    return (
        f"{bold('THE FORGOTTEN DEPTHS -- Command Reference')}\n\n"
        "  LOOK / L             -- Describe your surroundings\n"
        "  EXAMINE [thing] / X  -- Look closely at something\n"
        "  TAKE [item]          -- Pick up an item\n"
        "  DROP [item]          -- Put down an item\n"
        "  INVENTORY / I        -- List what you're carrying\n"
        "  USE [item]           -- Use an item\n"
        "  USE [item] ON [thing]-- Use an item on something\n"
        "  OPEN [thing]         -- Open a container or door\n"
        "  READ [item]          -- Read text on an item\n"
        "  PUSH / PULL [thing]  -- Interact with mechanisms\n"
        "  TURN [thing]         -- Rotate or turn something\n"
        "  TALK                 -- Speak with someone nearby\n"
        "  SAY [words]          -- Say something aloud\n"
        "  LISTEN               -- Listen to your surroundings\n"
        "  TIE [item]           -- Tie an item to something\n"
        "  STEP ON [tile]       -- Step on a specific tile\n"
        f"  N / S / E / W        -- Move {dim('(or NORTH, SOUTH, etc.)')}\n"
        f"  UP / DOWN            -- Move vertically\n"
        "  SCORE                -- Check your score\n"
        "  HINT                 -- Get a contextual hint\n"
        "  SAVE / LOAD          -- Save or restore your game\n"
        "  QUIT                 -- Exit the game"
    )


def cmd_hint(gs, cmd):
    return _get_hint(gs)


def cmd_score(gs, cmd):
    score = _calc_score(gs)
    return f"Your score is {bold(str(score))} out of a possible 100 points."


# ---------------------------------------------------------------------------
#  PUZZLE IMPLEMENTATIONS
# ---------------------------------------------------------------------------

def _use_oil(gs):
    flask = _find_in_inventory(gs, "oil_flask")
    lantern = _find_in_inventory(gs, "lantern")
    if not flask:
        return "You don't have the oil flask."
    if not lantern:
        return "You don't have the lantern."
    if gs.flags.get("oil_used"):
        return "The flask is empty."

    gs.player["lantern_oil"] = 80
    gs.flags["oil_used"] = True
    return ("You carefully unscrew the flask and pour the oil into the lantern's "
            "reservoir. The flame brightens and steadies. The gauge reads full.")


def _use_rope(gs, room):
    if room.id != "underground_river":
        return "There's nothing useful to tie the rope to here."

    if gs.flags.get("river_crossed"):
        return "The rope is already tied securely to the pillar."

    rope = _find_in_inventory(gs, "rope")
    if not rope:
        return "You don't have a rope."

    gs.player["inventory"].remove(rope)
    gs.flags["river_crossed"] = True
    gs.add_score("river_crossed", 10)
    return ("You tie one end of the rope firmly around the stone pillar, then "
            "use it as a lifeline to cross the rushing river. The current "
            "pulls at your legs but the rope holds. You reach the far bank "
            "safely. The rope remains tied for future crossings.\n\n"
            "The south passage is now accessible.")


def _try_swim(gs):
    if gs.flags.get("river_crossed"):
        return "You use the rope to cross safely. No need to swim."

    gs.player["turns"] += 1
    _consume_oil(gs)
    gs.player["room"] = "fungal_grotto"
    return ("You plunge into the icy water. The current immediately seizes you, "
            "dragging you downstream. You struggle, swallowing water, and are "
            "eventually spat out in the Fungal Grotto, coughing and shivering.\n\n"
            "You need a rope or something to cross safely.")


def _use_lens(gs, room):
    if room.id != "observatory":
        return "You hold up the crystal lens, but there's nothing useful to do with it here."

    if gs.flags.get("lens_placed"):
        return "The lens is already in the orrery."

    lens = _find_in_inventory(gs, "crystal_lens")
    if not lens:
        return "You don't have the crystal lens."

    gs.player["inventory"].remove(lens)
    gs.flags["lens_placed"] = True
    return ("You slot the crystal lens into the empty socket on the orrery. It "
            "fits with a satisfying click. Light from your lantern refracts "
            "through it, casting rainbow patterns on the dome above.\n\n"
            "The orrery seems ready to be operated. Try turning the crank.")


def _turn_orrery(gs):
    if not gs.flags.get("lens_placed"):
        return ("You turn the crank but the orrery barely moves. Something "
                "is missing -- that empty socket looks important.")

    if gs.flags.get("orrery_solved"):
        return "The orrery is already set. The star chart has been revealed."

    gs.flags["orrery_solved"] = True
    gs.add_score("orrery_solved", 15)

    # Place star chart in the room
    room = gs.current_room()
    room.items.append(gs.items["star_chart"])

    return ("You turn the crank and the orrery comes alive. The brass rings spin, "
            "the planetary spheres glide along their orbits. Light refracts "
            "through the crystal lens, projecting a brilliant star map onto the "
            "domed ceiling.\n\n"
            "You remember Whitmore's diagram: Mercury, Venus, Earth, Mars, "
            "Jupiter -- innermost to outermost. You adjust each ring to match.\n\n"
            "With a deep CLUNK, the orrery locks into position. A hidden "
            "compartment opens in the pedestal, revealing a star chart etched "
            "on thin metal.")


def _use_gear(gs, room):
    if room.id != "mechanism_room":
        return "You turn the gear in your hands, but there's nothing to fit it into here."

    if gs.flags.get("gear_placed"):
        return "The gear is already in place."

    gear = _find_in_inventory(gs, "bronze_gear")
    if not gear:
        return "You don't have the bronze gear."

    gs.player["inventory"].remove(gear)
    gs.flags["gear_placed"] = True
    return ("You slide the bronze gear onto the empty axle. It meshes perfectly "
            "with the surrounding gears. The mechanism is now complete.\n\n"
            "The three levers await. Pull them in the right order to activate it.")


def _pull_lever(gs, noun):
    if not gs.flags.get("gear_placed"):
        return "The mechanism is incomplete. It's missing a gear."

    if gs.flags.get("mechanism_solved"):
        return "The mechanism is already running. You can hear water draining below."

    lever_map = {
        "left": "low", "left lever": "low", "circle": "low", "low": "low",
        "middle": "high", "middle lever": "high", "triangle": "high", "high": "high",
        "right": "middle", "right lever": "middle", "square": "middle",
    }

    lever = lever_map.get(noun.lower())
    if not lever:
        return "Which lever? LEFT (circle), MIDDLE (triangle), or RIGHT (square)?"

    sequence = gs.flags.get("lever_sequence", [])
    expected = ["low", "high", "middle"]

    sequence.append(lever)
    gs.flags["lever_sequence"] = sequence

    if sequence == expected[:len(sequence)]:
        if len(sequence) == 3:
            gs.flags["mechanism_solved"] = True
            gs.flags["chamber_drained"] = True
            gs.flags["lever_sequence"] = []
            gs.add_score("mechanism_solved", 15)
            return ("You pull the final lever. The mechanism groans to life -- "
                    "gears turn, chains rattle, and you hear a deep gurgling "
                    "sound from below as water rushes through hidden channels.\n\n"
                    "The flooded chamber is draining! A new path should be "
                    "accessible now.")
        pulled_name = {0: "first", 1: "second"}
        return f"CLUNK. The {pulled_name.get(len(sequence)-1, 'next')} lever locks into position."
    else:
        gs.flags["lever_sequence"] = []
        return ("CLANG! The levers spring back to their starting positions. "
                "Wrong sequence. The pipes in the Hall of Echoes might hold "
                "a clue to the correct order.")


def _step_on_tile(gs, noun):
    if gs.flags.get("floor_puzzle_solved"):
        return "The tiles are locked in place. The stone door stands open."

    tile_map = {"sun": 0, "moon": 1, "star": 2, "stars": 2, "wave": 3, "waves": 3}
    tile = tile_map.get(noun.lower())

    if tile is None:
        return "The tiles show four symbols: SUN, MOON, STAR, and WAVE."

    sequence = gs.flags.get("tile_sequence", [])
    expected = [0, 1, 2, 3]  # sun, moon, star, wave

    sequence.append(tile)
    gs.flags["tile_sequence"] = sequence

    tile_names = ["Sun", "Moon", "Star", "Wave"]
    stepped = tile_names[tile]

    if sequence == expected[:len(sequence)]:
        if len(sequence) == 4:
            gs.flags["floor_puzzle_solved"] = True
            gs.flags["tile_sequence"] = []
            gs.add_score("floor_puzzle_solved", 15)
            return (f"You step on the {stepped} tile. CLICK.\n\n"
                    "All four tiles illuminate in sequence: Sun, Moon, Star, Wave. "
                    "A deep rumble shakes the room, and the massive stone door "
                    "grinds slowly open, revealing stairs descending into darkness.")
        return f"You step on the {stepped} tile. CLICK. It stays depressed. Promising."
    else:
        gs.flags["tile_sequence"] = []
        return (f"You step on the {stepped} tile. For a moment nothing happens... "
                "then all the tiles pop up with a resounding CLACK. Wrong sequence. "
                "The stone tablet from the archive might tell you the right order.")


def _use_iron_key(gs, room):
    if room.id != "prison_cells":
        return "There's no lock here that fits this key."

    if gs.flags.get("whitmore_freed"):
        return "Whitmore is already free."

    return _free_whitmore(gs, "key")


def _use_chisel(gs, room):
    if room.id != "prison_cells":
        return "There's nothing to chisel here."

    if gs.flags.get("whitmore_freed"):
        return "Whitmore is already free."

    return _free_whitmore(gs, "chisel")


def _free_whitmore(gs, method):
    gs.flags["whitmore_freed"] = True
    gs.add_score("whitmore_freed", 15)

    notebook = gs.items["whitmore_notebook"]
    gs.player["inventory"].append(notebook)

    if method == "key":
        text = ("You insert the iron key into the lock. It turns with a heavy "
                "CLUNK, and the cell door swings open.")
    else:
        text = ("You work the chisel under the rusted hinges and lever hard. "
                "With a screech of protesting metal, the hinges snap and the "
                "door falls outward with a crash.")

    text += ("\n\nProfessor Whitmore stumbles out, gripping your arm.\n\n"
             "\"Elara! Magnificent work. Here -- take my notebook. Everything "
             "I've learned about The Heart is in there. The answer is below "
             "us, in the Sanctum. The altar, the rings, the invocation. "
             "It's all connected.\"\n\n"
             "He presses his notebook into your hands.\n\n"
             "  " + italic("(Whitmore's notebook added to inventory)"))

    return text


def _use_coin(gs, room):
    if room.id != "sanctum":
        return "You turn the ancient coin in your fingers. It feels important."

    if gs.flags.get("coin_placed"):
        return "The coin is already in the altar."

    coin = _find_in_inventory(gs, "ancient_coin")
    if not coin:
        return "You don't have the coin."

    gs.player["inventory"].remove(coin)
    gs.flags["coin_placed"] = True
    return ("You press the ancient coin into the depression at the center of "
            "the altar. It fits exactly. The coin sinks slightly and locks "
            "in place with a click. The bronze rings hum faintly.")


def _use_star_chart(gs, room):
    if room.id != "sanctum":
        return "You study the star chart. The five constellations seem significant."

    if gs.flags.get("rings_set"):
        return "The rings are already set to the correct positions."

    if not gs.flags.get("coin_placed"):
        return "The altar doesn't respond. Something is missing from its center."

    gs.flags["rings_set"] = True
    return ("Consulting the star chart, you rotate each ring to align with the "
            "correct constellation:\n\n"
            "  Inner ring:  The Serpent\n"
            "  Second ring: The Crown\n"
            "  Third ring:  The Flame\n"
            "  Fourth ring: The River\n"
            "  Outer ring:  The Eye\n\n"
            "Each ring clicks into position with a resonant tone. The altar "
            "pulses with a warm light. One final step remains -- the invocation.")


def _speak_invocation(gs):
    if not gs.flags.get("coin_placed"):
        return "The words echo impressively, but nothing happens. The altar seems inert."

    if not gs.flags.get("rings_set"):
        return ("The words resonate through the chamber. The rings vibrate but "
                "don't respond. They need to be set correctly first.")

    if gs.flags.get("heart_unlocked"):
        return "The way to The Heart is already open."

    gs.flags["heart_unlocked"] = True
    gs.add_score("sanctum_solved", 15)
    return ("You speak the words aloud: " + italic("\"ASTRA CORDIS APERITE.\"") + "\n\n"
            "Your voice reverberates through the obsidian chamber, growing "
            "louder with each echo rather than fading. The altar blazes with "
            "white light. The five rings spin in perfect synchronization, "
            "and the sealed door to the south splits open with a sound like "
            "a great sigh.\n\n"
            "Warm, rose-red light spills from the passage beyond.\n\n"
            "The way to The Heart is open.")


def _touch_orb(gs):
    gs.flags["game_won"] = True
    gs.add_score("touched_orb", 15)
    score = _calc_score(gs)

    return (
        "You reach out and touch the orb.\n\n"
        "Light blazes through you. For an instant you see everything: the "
        "builders, tall and strange, working in these halls millennia ago. "
        "They came from somewhere far away -- not another country, but another "
        "place entirely, beyond the stars. They built this complex as a "
        "waypoint, a lighthouse in the void between worlds. The Heart was "
        "their beacon, calling out across the cosmos.\n\n"
        "And now it calls to you.\n\n"
        "The orb pulses once, twice, and then the light gently fades. The "
        "chamber rumbles. Ancient mechanisms awaken throughout the complex. "
        "A stairway opens in the wall -- a new passage, spiraling upward "
        "toward daylight.\n\n"
        "You ascend. Whitmore is waiting at the top, blinking in the grey "
        "Highland light.\n\n"
        "\"Did you see it?\" he asks quietly. \"Did you see them?\"\n\n"
        "You nod. There are no words sufficient.\n\n"
        "Together, you walk out of the monastery ruins and into the mist, "
        "carrying a secret that will change the world.\n\n"
        + bold("*** THE END ***") + "\n\n"
        + f"Final score: {bold(str(score))} out of 100.\n"
        + _score_rank(score)
    )


# ---------------------------------------------------------------------------
#  HINTS
# ---------------------------------------------------------------------------

def _get_hint(gs):
    room = gs.current_room()

    if room.id == "monastery_ruins":
        return "The stairway leads down into the complex. Go DOWN to begin your exploration."

    if room.id == "underground_river" and not gs.flags.get("river_crossed"):
        return "You need a rope to cross safely. There was one in the antechamber."

    if room.id == "observatory" and not gs.flags.get("lens_placed"):
        return "The orrery is missing a lens. A crystal one might be found in a nearby cavern."

    if room.id == "observatory" and not gs.flags.get("orrery_solved"):
        return "Your field journal has notes about planetary positions. Turn the crank."

    if room.id == "mechanism_room" and not gs.flags.get("gear_placed"):
        return "The mechanism needs a gear. Check the forge workbench."

    if room.id == "mechanism_room" and not gs.flags.get("mechanism_solved"):
        return "The levers must be pulled in a specific order. Listen in the Hall of Echoes."

    if room.id == "puzzle_chamber" and not gs.flags.get("floor_puzzle_solved"):
        return "Step on the tiles in the right order. The stone tablet in the archive has the answer."

    if room.id == "prison_cells" and not gs.flags.get("whitmore_freed"):
        return "The cell needs an iron key (scriptorium desk) or a chisel to break the hinges."

    if room.id == "sanctum" and not gs.flags.get("coin_placed"):
        return "The altar has a coin-sized depression. An ancient coin might fit."

    if room.id == "sanctum" and not gs.flags.get("rings_set"):
        return "Set the rings using the constellation sequence from the star chart."

    if room.id == "sanctum" and not gs.flags.get("heart_unlocked"):
        return "Speak the invocation. The words are carved above the archway."

    if room.id == "the_heart":
        return "Touch the orb to complete your journey."

    if not gs.flags.get("river_crossed") and not gs.flags.get("floor_puzzle_solved"):
        return "Explore the upper chambers. There are puzzles to solve and items to find."

    if not gs.flags.get("whitmore_freed"):
        return "You need to find and free Professor Whitmore."

    if not gs.flags.get("heart_unlocked"):
        return "The Sanctum holds the final lock. You need a coin, a star chart, and the invocation."

    return "Explore carefully. Examine everything."


# ---------------------------------------------------------------------------
#  SCORING
# ---------------------------------------------------------------------------

def _calc_score(gs):
    return sum(gs.score_items.values())


def _score_rank(score):
    if score >= 100:
        return "Rank: Master Archaeologist"
    if score >= 75:
        return "Rank: Senior Researcher"
    if score >= 50:
        return "Rank: Field Archaeologist"
    if score >= 25:
        return "Rank: Graduate Student"
    return "Rank: Amateur Explorer"


# ---------------------------------------------------------------------------
#  HELPERS
# ---------------------------------------------------------------------------

def _has_light(gs):
    lantern = _find_in_inventory(gs, "lantern")
    if lantern and gs.player.get("lantern_oil", 0) > 0:
        return True
    room = gs.current_room()
    return room.id == "fungal_grotto"


def _consume_oil(gs):
    if gs.player.get("lantern_oil", 0) > 0:
        gs.player["lantern_oil"] -= 1
        if gs.player["lantern_oil"] == 20:
            gs.pending_message = "Your lantern flickers. The oil is getting low."
        elif gs.player["lantern_oil"] == 10:
            gs.pending_message = "Your lantern sputters. It won't last much longer."
        elif gs.player["lantern_oil"] <= 0:
            gs.player["lantern_oil"] = 0
            gs.pending_message = ("Your lantern gutters and goes out. Darkness swallows you.\n"
                                  "Find oil quickly, or stay in lit areas.")


def _find_in_inventory(gs, noun):
    for item in gs.player["inventory"]:
        if item.matches(noun):
            return item
    return None


def _noun_matches(text, name):
    text = text.lower()
    return text == name or text in name.split()


def _reveal_item(gs, room, item):
    item.hidden = False


def _check_scenery_reveals(gs, room, scenery):
    """Examining certain scenery reveals hidden items."""
    if room.id == "scriptorium":
        if scenery.id in ("desk", "drawer"):
            key = gs.items.get("iron_key")
            if key and key.hidden:
                key.hidden = False
        elif scenery.id == "toolbox":
            chisel = gs.items.get("chisel")
            if chisel and chisel.hidden:
                chisel.hidden = False

    if room.id == "forge":
        if scenery.id == "workbench":
            gear = gs.items.get("bronze_gear")
            if gear and gear.hidden:
                gear.hidden = False


# Command dispatch table
COMMANDS = {
    "go": cmd_go,
    "look": cmd_look,
    "examine": cmd_examine,
    "take": cmd_take,
    "drop": cmd_drop,
    "inventory": cmd_inventory,
    "use": cmd_use,
    "open": cmd_open,
    "read": cmd_read,
    "push": cmd_push,
    "pull": cmd_pull,
    "turn": cmd_turn,
    "tie": cmd_tie,
    "insert": cmd_insert,
    "place": cmd_place,
    "set": cmd_set,
    "climb": cmd_climb,
    "step": cmd_step,
    "talk": cmd_talk,
    "say": cmd_say,
    "listen": cmd_listen,
    "smell": cmd_smell,
    "touch": cmd_touch,
    "swim": cmd_swim,
    "jump": cmd_jump,
    "enter": cmd_enter,
    "eat": cmd_eat,
    "drink": cmd_drink,
    "taste": cmd_taste,
    "wait": cmd_wait,
    "help": cmd_help,
    "hint": cmd_hint,
    "score": cmd_score,
    "light": lambda gs, cmd: _use_oil(gs) if _find_in_inventory(gs, "lantern") else "Light what?",
    "fill": lambda gs, cmd: _use_oil(gs),
}
