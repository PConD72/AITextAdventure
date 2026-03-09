"""
The Mechanical Spider -- an ancient robotic automaton that roams the depths.
It wanders autonomously between rooms and occasionally interacts with the
player or the environment.
"""

import random

SPIDER_ROOMS = [
    "stone_stairway", "antechamber", "hall_of_echoes", "flooded_passage",
    "crystal_cavern", "obsidian_bridge", "library_of_whispers",
    "fungal_garden", "clockwork_chamber", "forge", "mirror_gallery",
    "tomb_of_the_builder", "underground_river", "abyss_ledge",
    "pillar_room", "sanctum_approach", "the_sanctum",
]

PROTECTED_ITEMS = {"lantern", "journal"}

SPEECH = [
    "Kzzrt vreem shala nok!",
    "Tik-tik-tik... meeva sol braan.",
    "Chrrrk! Zan oru metalik vren.",
    "Whrrr click-click... noom ferrata.",
    "Bzzt! Kaal voss im dratha kel.",
    "Tch-tch-tch... primus architecta.",
    "Skreee! Ven oth makina zur!",
    "Click-whirr... solam eternis gratk.",
    "Znn znn... ferrus vita kol.",
    "Bzzzt klik! Om sharra ven tek.",
]

REPAIRS = [
    "extends a tiny welding arm and sparks fly as it repairs a crack in the wall",
    "produces a miniature wrench and tightens a loose bolt in the floor",
    "spins silk-like metallic thread to patch a crumbling section of stonework",
    "polishes a section of the wall with a whirring buffing attachment",
    "welds two broken pieces of ancient pipe back together",
    "carefully realigns a crooked stone tile with delicate pincers",
]

TUNES = [
    "a tinny, haunting melody that echoes off the walls",
    "a rapid series of clicks that almost sounds like a waltz",
    "a low, resonant hum that vibrates through the floor",
    "a cheerful but discordant jingle from deep inside its chassis",
    "what sounds like a music-box rendition of a very ancient song",
    "an eerie sequence of tones that makes the hairs on your neck stand up",
]


class SpiderRobot:
    def __init__(self):
        self.room = "antechamber"
        self.inventory = []
        self.cooldown = 4       # ticks before first action
        self.give_cooldown = 0  # when >0, prioritise giving item back

    def tick(self, gs):
        """Advance one tick.  Returns a message string if the player can
        see or hear the result, otherwise None."""
        if gs.flags.get("game_won"):
            return None

        if self.cooldown > 0:
            self.cooldown -= 1
            return None

        player_room = gs.player["room"]
        in_player_room = (self.room == player_room)

        # If carrying a stolen item and near the player, give it back soon
        if self.inventory and in_player_room:
            self.give_cooldown += 1
            if self.give_cooldown >= 2:
                self.give_cooldown = 0
                self._set_cooldown()
                return self._give_item(gs)

        roll = random.random()

        if roll < 0.45:
            msg = self._try_move(gs, player_room)
        elif in_player_room:
            msg = self._do_action(gs)
        else:
            msg = self._try_move(gs, player_room)

        self._set_cooldown()
        return msg

    def _set_cooldown(self):
        self.cooldown = random.randint(2, 5)

    # ------------------------------------------------------------------
    #  Movement
    # ------------------------------------------------------------------

    def _try_move(self, gs, player_room):
        if self.room not in gs.rooms:
            return None

        current = gs.rooms[self.room]
        exits = list(current.exits.items())
        if not exits:
            return None

        direction, dest_id = random.choice(exits)
        if dest_id == "monastery_ruins":
            return None

        was_visible = (self.room == player_room)
        old_room = self.room
        self.room = dest_id
        now_visible = (self.room == player_room)

        if was_visible:
            return (
                "The mechanical spider clicks its legs and "
                f"scuttles away to the {direction}."
            )

        if now_visible:
            came_from = self._reverse_dir(gs, old_room)
            if came_from:
                return (
                    "A small mechanical spider scuttles into "
                    f"the room from the {came_from}."
                )
            return "A small mechanical spider scuttles into the room."

        return None

    def _reverse_dir(self, gs, from_room_id):
        """Find the direction name in the current room that leads back to from_room_id."""
        if self.room not in gs.rooms:
            return None
        for d, r in gs.rooms[self.room].exits.items():
            if r == from_room_id:
                return d
        return None

    # ------------------------------------------------------------------
    #  Actions (player is in the same room)
    # ------------------------------------------------------------------

    def _do_action(self, gs):
        choices = ["speak", "speak", "music", "repair", "repair"]

        player_inv = gs.player["inventory"]
        stealable = [i for i in player_inv if i.id not in PROTECTED_ITEMS]
        if stealable and not self.inventory:
            choices.append("take")

        if self.inventory:
            choices.append("give")
            choices.append("give")

        action = random.choice(choices)

        if action == "speak":
            phrase = random.choice(SPEECH)
            return f'The mechanical spider clicks and whirs: "{phrase}"'

        if action == "music":
            tune = random.choice(TUNES)
            return f"The mechanical spider emits {tune}."

        if action == "repair":
            desc = random.choice(REPAIRS)
            return f"The mechanical spider {desc}."

        if action == "take":
            return self._take_item(gs, stealable)

        if action == "give":
            return self._give_item(gs)

        return None

    def _take_item(self, gs, stealable):
        item = random.choice(stealable)
        gs.player["inventory"].remove(item)
        self.inventory.append(item)
        self.give_cooldown = 0
        return (
            f"The mechanical spider snatches the {item.name} from "
            "your hands with surprising speed!"
        )

    def _give_item(self, gs):
        if not self.inventory:
            return None
        item = self.inventory.pop(0)
        gs.player["inventory"].append(item)
        self.give_cooldown = 0
        return (
            f"The mechanical spider carefully places the "
            f"{item.name} at your feet."
        )

    # ------------------------------------------------------------------
    #  Serialisation
    # ------------------------------------------------------------------

    def to_dict(self):
        return {
            "room": self.room,
            "inventory_ids": [i.id for i in self.inventory],
            "cooldown": self.cooldown,
            "give_cooldown": self.give_cooldown,
        }

    def load_dict(self, data, items_lookup):
        self.room = data.get("room", "antechamber")
        self.cooldown = data.get("cooldown", 2)
        self.give_cooldown = data.get("give_cooldown", 0)
        self.inventory = []
        for iid in data.get("inventory_ids", []):
            if iid in items_lookup:
                self.inventory.append(items_lookup[iid])
