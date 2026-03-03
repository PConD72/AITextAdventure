"""
Game engine for The Forgotten Depths.
Manages game state, the main loop, save/load, and command dispatch.
"""

import json
import os

from game.world import build_world
from game.parser import parse
from game.commands import COMMANDS
from game.utils import (
    print_wrapped, bold, dim, get_input, clear_screen, print_slow
)


SAVE_FILE = "forgotten_depths_save.json"


class GameState:
    def __init__(self):
        self.rooms, self.items = build_world()
        self.player = {
            "room": "monastery_ruins",
            "inventory": [],
            "turns": 0,
            "lantern_oil": 80,
        }
        self.flags = {}
        self.score_items = {}
        self.visited_rooms = set()
        self.pending_message = None

        # Give starting items
        self.player["inventory"].append(self.items["lantern"])
        self.player["inventory"].append(self.items["journal"])

    def current_room(self):
        return self.rooms[self.player["room"]]

    def visit_room(self, room_id):
        if room_id not in self.visited_rooms:
            self.visited_rooms.add(room_id)

    def add_score(self, key, points):
        if key not in self.score_items:
            self.score_items[key] = points

    def to_save_dict(self):
        """Serialize game state to a JSON-compatible dict."""
        inv_ids = [item.id for item in self.player["inventory"]]

        room_items = {}
        for rid, room in self.rooms.items():
            room_items[rid] = {
                "item_ids": [i.id for i in room.items],
                "visited": room.visited,
            }

        item_states = {}
        for iid, item in self.items.items():
            item_states[iid] = {"hidden": item.hidden}

        return {
            "player_room": self.player["room"],
            "inventory_ids": inv_ids,
            "turns": self.player["turns"],
            "lantern_oil": self.player["lantern_oil"],
            "flags": self.flags,
            "score_items": self.score_items,
            "visited_rooms": list(self.visited_rooms),
            "room_data": room_items,
            "item_states": item_states,
        }

    def load_save_dict(self, data):
        """Restore game state from a save dict."""
        self.player["room"] = data["player_room"]
        self.player["turns"] = data["turns"]
        self.player["lantern_oil"] = data["lantern_oil"]
        self.flags = data["flags"]
        self.score_items = data["score_items"]
        self.visited_rooms = set(data["visited_rooms"])

        # Restore item hidden states
        for iid, state in data.get("item_states", {}).items():
            if iid in self.items:
                self.items[iid].hidden = state["hidden"]

        # Restore inventory
        self.player["inventory"] = []
        for iid in data["inventory_ids"]:
            if iid in self.items:
                self.player["inventory"].append(self.items[iid])

        # Restore room items
        for rid, rdata in data.get("room_data", {}).items():
            if rid in self.rooms:
                room = self.rooms[rid]
                room.visited = rdata["visited"]
                room.items = []
                for iid in rdata["item_ids"]:
                    if iid in self.items:
                        item = self.items[iid]
                        if item not in self.player["inventory"]:
                            room.items.append(item)


def save_game(gs):
    try:
        data = gs.to_save_dict()
        with open(SAVE_FILE, "w") as f:
            json.dump(data, f, indent=2)
        return "Game saved."
    except Exception as e:
        return f"Save failed: {e}"


def load_game(gs):
    if not os.path.exists(SAVE_FILE):
        return None, "No save file found."
    try:
        with open(SAVE_FILE, "r") as f:
            data = json.load(f)
        gs.load_save_dict(data)
        return gs, "Game restored."
    except Exception as e:
        return None, f"Load failed: {e}"


def process_command(gs, raw_input):
    """Process a single command string. Returns (response_text, room_changed).
    Used by both CLI and GUI frontends."""
    from game.commands import cmd_look, COMMANDS

    raw = raw_input.strip()
    if not raw:
        return ("", False)

    cmd = parse(raw)

    if not cmd.verb:
        return ("I don't understand that. Type HELP for a list of commands.", False)

    if cmd.verb == "save":
        return (save_game(gs), False)

    if cmd.verb == "load":
        new_gs, msg = load_game(gs)
        if new_gs:
            gs.load_save_dict(new_gs.to_save_dict() if hasattr(new_gs, "to_save_dict")
                              else {})
            look_result = get_look_text(gs)
            return (msg + "\n" + look_result, True)
        return (msg, False)

    old_room = gs.player["room"]

    handler = COMMANDS.get(cmd.verb)
    if handler:
        result = handler(gs, cmd) or ""
    else:
        result = "I don't know how to do that. Type HELP for a list of commands."

    room_changed = gs.player["room"] != old_room

    # Append any pending messages
    if gs.pending_message:
        result = result + "\n\n" + gs.pending_message
        gs.pending_message = None

    return (result, room_changed)


def get_look_text(gs):
    """Get the look description for the current room."""
    from game.commands import cmd_look
    dummy = type("Cmd", (), {"verb": "look", "noun": None})()
    return cmd_look(gs, dummy, force_long=True)


def run_game(gs):
    """Main game loop (CLI version)."""
    from game.commands import _calc_score

    result = get_look_text(gs)
    print_wrapped(result)

    while True:
        if gs.flags.get("game_won"):
            break

        print()
        raw = get_input()

        if not raw:
            continue

        cmd = parse(raw)

        if cmd.verb == "quit":
            print_wrapped("Are you sure you want to quit? (yes/no)")
            try:
                confirm = get_input().lower()
            except (EOFError, KeyboardInterrupt):
                confirm = "yes"
            if confirm in ("yes", "y", "quit"):
                score = _calc_score(gs)
                print_wrapped(f"\nFinal score: {score} out of 100.")
                print_wrapped("Thanks for playing The Forgotten Depths!")
                break
            print_wrapped("Okay, continuing.")
            continue

        result, _ = process_command(gs, raw)
        if result:
            print_wrapped(result)
