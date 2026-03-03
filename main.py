#!/usr/bin/env python3
"""
THE FORGOTTEN DEPTHS
A Text Adventure in the Style of the Infocom Classics
With a ZX Spectrum-inspired graphical interface

(c) 2026 -- An Interactive Fiction

Usage:
    python main.py          Launch with graphical interface (default)
    python main.py --cli    Launch in terminal/text-only mode
"""

import sys


def run_cli():
    from game.utils import clear_screen, print_slow, bold, dim, press_enter, print_wrapped
    from game.engine import GameState, run_game

    TITLE_ART = r"""
    ___________________________________________________________
   /                                                           \
  |   _____ _            _____                     _   _        |
  |  |_   _| |__   ___  |  ___|__  _ __ __ _  ___ | |_| |_ ___ |
  |    | | | '_ \ / _ \ | |_ / _ \| '__/ _` |/ _ \| __| __/ _ \|
  |    | | | | | |  __/ |  _| (_) | | | (_| | (_) | |_| ||  __/|
  |    |_| |_| |_|\___| |_|  \___/|_|  \__, |\___/ \__|\__\___||
  |                                     |___/                   |
  |          ____             _   _                             |
  |         |  _ \  ___ _ __ | |_| |__  ___                    |
  |         | | | |/ _ \ '_ \| __| '_ \/ __|                   |
  |         | |_| |  __/ |_) | |_| | | \__ \                   |
  |         |____/ \___| .__/ \__|_| |_|___/                   |
  |                    |_|                                      |
  |                                                             |
  |           An Interactive Fiction                             |
  |           Inspired by the Infocom Classics                  |
   \___________________________________________________________/
"""

    INTRO_TEXT = """\
The year is 1923.

You are Dr. Elara Voss, archaeologist, standing in the ruins of a
Benedictine monastery high in the Scottish Highlands. Below your feet,
beneath centuries of stone and silence, lies something that should not
exist: an underground complex older than any known civilization.

Your expedition partner, Professor Reginald Whitmore, descended into
the complex yesterday morning. He has not returned.

The entrance yawns before you -- a dark spiral stairway cut into the
bedrock. Whitmore's bootprints are still fresh in the dust.

You grip your brass lantern, check the oil, and begin your descent.
"""

    clear_screen()
    print(bold(TITLE_ART))
    print()
    print(dim("  Type HELP at any time for a list of commands."))
    print(dim("  Type HINT if you get stuck."))
    print()
    press_enter()
    clear_screen()

    print_slow("The year is 1923.\n", delay=0.03)
    print()
    print_wrapped(INTRO_TEXT)
    print()
    press_enter()
    clear_screen()

    gs = GameState()
    run_game(gs)


def run_gui():
    from game.gui import run_gui as _run_gui
    _run_gui()


def main():
    if "--cli" in sys.argv:
        run_cli()
    else:
        run_gui()


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nFarewell, Dr. Voss. The depths will wait.")
        sys.exit(0)
