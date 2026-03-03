"""
ZX Spectrum-style GUI for The Forgotten Depths.
Renders at native 256x192, scaled up 3x for the window.

Layout: a single scrolling content area (images + text inline) with a
two-line input bar pinned at the bottom. When new content overflows the
screen, a (more) prompt appears and the player presses any key to page.
"""

import pygame
import textwrap
import re
import os

from game.spectrum import (
    NATIVE_W, NATIVE_H, SCALE, WIN_W, WIN_H,
    IMAGE_H, INPUT_H, CONTENT_H, INPUT_Y,
    CHAR_W, CHAR_H, COLS, CONTENT_LINES,
    BLACK, BLUE, RED, CYAN, YELLOW, WHITE, GREEN,
    BRIGHT_BLUE, BRIGHT_RED, BRIGHT_GREEN, BRIGHT_YELLOW,
    BRIGHT_WHITE, BRIGHT_CYAN,
    BORDER_COLOR, TEXT_COLOR, INPUT_COLOR,
    ROOM_NAME_COLOR, SEPARATOR_COLOR, DIM_COLOR,
)
from game.room_art import draw_room, draw_splash
from game.engine import GameState, process_command, get_look_text

TITLE = "The Forgotten Depths"
FPS = 30
CURSOR_BLINK_MS = 500
WIN_BORDER = 24
REVEAL_DELAY_MS = 120  # ms between each line during slow reveal


def _strip_ansi(text):
    return re.sub(r'\033\[[0-9;]*m', '', text)


def _word_wrap(text, cols):
    """Re-flow text into cols-wide lines, rejoining pre-wrapped paragraphs."""
    paragraphs = []
    current = []
    for raw_line in text.split("\n"):
        stripped = raw_line.rstrip()
        if not stripped:
            if current:
                paragraphs.append(" ".join(current))
                current = []
            paragraphs.append("")
        else:
            current.append(stripped)
    if current:
        paragraphs.append(" ".join(current))

    lines = []
    for para in paragraphs:
        if not para:
            lines.append("")
        else:
            wrapped = textwrap.wrap(para, width=cols,
                                    break_long_words=True,
                                    break_on_hyphens=False)
            lines.extend(wrapped if wrapped else [""])
    return lines


# Buffer entry types
TEXT = "text"    # ("text", string, color)
IMAGE = "image"  # ("image", pygame.Surface)


class SpectrumGUI:
    def __init__(self):
        pygame.init()
        pygame.display.set_caption(TITLE)

        self.win_w = WIN_W + WIN_BORDER * 2
        self.win_h = WIN_H + WIN_BORDER * 2
        self.screen = pygame.display.set_mode((self.win_w, self.win_h))
        self.clock = pygame.time.Clock()
        self.native = pygame.Surface((NATIVE_W, NATIVE_H))

        self.font = self._load_font()
        self.char_w, self.char_h = self._measure_font()
        self.cols = max(20, NATIVE_W // self.char_w)

        self.gs = None
        self.buffer = []       # mixed list of (TEXT, str, color) | (IMAGE, surface)
        self.view_top = 0      # index of first visible item in buffer
        self.pending = []      # items queued for line-by-line reveal
        self.more_waiting = False   # showing (more), waiting for keypress
        self.revealing = False      # line-by-line animation in progress
        self.reveal_timer = 0

        self.input_text = ""
        self.input_history = []
        self.history_idx = -1
        self.cursor_visible = True
        self.cursor_timer = 0

        self.state = "splash"  # splash | intro | playing | gameover
        self.intro_lines = []

        pygame.key.set_repeat(400, 50)

        try:
            pygame.mixer.init()
            theme_path = os.path.join(os.path.dirname(__file__),
                                      "Forgotten_Depths_Title_Theme.wav")
            if os.path.exists(theme_path):
                pygame.mixer.music.load(theme_path)
                pygame.mixer.music.play(-1)
        except Exception:
            pass

    # ------------------------------------------------------------------
    #  Font
    # ------------------------------------------------------------------

    def _load_font(self):
        font_path = os.path.join(os.path.dirname(__file__), "zxSpectrum.ttf")
        if os.path.exists(font_path):
            font = pygame.font.Font(font_path, 15)
            if font:
                return font
        for name in ["Consolas", "Courier New", "Courier"]:
            for size in range(8, 14):
                font = pygame.font.SysFont(name, size)
                if font and font.get_height() <= 10:
                    return font
        return pygame.font.Font(None, 10)

    def _measure_font(self):
        surf = self.font.render("M", False, WHITE, BLACK)
        return surf.get_width(), surf.get_height()

    def _render_text(self, text, color):
        return self.font.render(text, False, color, BLACK)

    # ------------------------------------------------------------------
    #  Content buffer helpers
    # ------------------------------------------------------------------

    def _item_height(self, item):
        if item[0] == IMAGE:
            return item[1].get_height()
        return self.char_h

    def _anchor_bottom(self):
        """Set view_top so the most recent content fills the screen
        from the bottom up, leaving no gap before the prompt."""
        budget = CONTENT_H
        for i in range(len(self.buffer) - 1, -1, -1):
            h = self._item_height(self.buffer[i])
            if h > budget:
                self.view_top = i + 1
                return
            budget -= h
        self.view_top = 0

    def _add_content(self, items):
        """Add content. If it overflows one screen, the first page appears
        instantly with (more); after a keypress the rest reveals line-by-line."""
        if not items:
            return

        total_h = sum(self._item_height(it) for it in items)

        if total_h <= CONTENT_H:
            self.buffer.extend(items)
            self._anchor_bottom()
            return

        # Overflow -- show first page, queue the rest
        budget = CONTENT_H - self.char_h  # reserve one line for (more)
        show = 0
        for it in items:
            h = self._item_height(it)
            if h > budget:
                break
            budget -= h
            show += 1

        self.buffer.extend(items[:max(1, show)])
        self.pending = list(items[max(1, show):])
        self.more_waiting = True
        self._anchor_bottom()

    # ------------------------------------------------------------------
    #  Building content from game output
    # ------------------------------------------------------------------

    def _parse_result(self, text, room_surface=None):
        """Turn engine output text (+ optional image) into buffer items."""
        items = []
        if room_surface:
            items.append((IMAGE, room_surface))

        raw_lines = text.split("\n")
        normal_accum = []

        def flush():
            if not normal_accum:
                return
            joined = "\n".join(normal_accum)
            for wl in _word_wrap(joined, self.cols):
                items.append((TEXT, wl, TEXT_COLOR))
            normal_accum.clear()

        for line in raw_lines:
            stripped = line.strip()
            if stripped.startswith("---") and stripped.endswith("---"):
                flush()
                items.append((TEXT, stripped.strip("- "), ROOM_NAME_COLOR))
            elif stripped.startswith("[Exits:"):
                flush()
                items.append((TEXT, stripped, DIM_COLOR))
            elif stripped.startswith("***"):
                flush()
                items.append((TEXT, stripped, BRIGHT_YELLOW))
            elif stripped.startswith("Rank:") or stripped.startswith("Final score:"):
                flush()
                items.append((TEXT, stripped, BRIGHT_YELLOW))
            elif stripped.startswith(">"):
                flush()
                items.append((TEXT, stripped, BRIGHT_GREEN))
            else:
                normal_accum.append(line)

        flush()
        # Word-wrap any oversized lines that slipped through
        final = []
        for item in items:
            if item[0] == TEXT and len(item[1]) > self.cols:
                for wl in _word_wrap(item[1], self.cols):
                    final.append((TEXT, wl, item[2]))
            else:
                final.append(item)
        return final

    # ------------------------------------------------------------------
    #  Main loop
    # ------------------------------------------------------------------

    def run(self):
        running = True
        while running:
            dt = self.clock.tick(FPS)
            self.cursor_timer += dt
            if self.cursor_timer >= CURSOR_BLINK_MS:
                self.cursor_visible = not self.cursor_visible
                self.cursor_timer = 0

            # Line-by-line reveal animation
            if self.revealing and self.pending:
                self.reveal_timer += dt
                if self.reveal_timer >= REVEAL_DELAY_MS:
                    self.reveal_timer -= REVEAL_DELAY_MS
                    self.buffer.append(self.pending.pop(0))
                    self._anchor_bottom()
                    if not self.pending:
                        self.revealing = False
                        self.reveal_timer = 0

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.KEYDOWN:
                    running = self._handle_key(event)

            self._draw()
            pygame.display.flip()

        pygame.quit()

    # ------------------------------------------------------------------
    #  Input handling
    # ------------------------------------------------------------------

    def _handle_key(self, event):
        if self.state == "splash":
            self._start_intro()
            return True

        if self.state == "intro":
            if event.key in (pygame.K_RETURN, pygame.K_SPACE):
                self._start_game()
            return True

        if self.state == "gameover":
            if event.key in (pygame.K_RETURN, pygame.K_SPACE, pygame.K_ESCAPE):
                return False
            return True

        # Waiting for keypress after (more) -- start line-by-line reveal
        if self.more_waiting:
            self.more_waiting = False
            self.revealing = True
            self.reveal_timer = 0
            return True

        # During reveal, any key skips the animation
        if self.revealing:
            self.buffer.extend(self.pending)
            self.pending.clear()
            self.revealing = False
            self.reveal_timer = 0
            self._anchor_bottom()
            return True

        if event.key == pygame.K_RETURN:
            self._submit_command()
        elif event.key == pygame.K_BACKSPACE:
            self.input_text = self.input_text[:-1]
        elif event.key == pygame.K_UP:
            self._history_prev()
        elif event.key == pygame.K_DOWN:
            self._history_next()
        elif event.key == pygame.K_ESCAPE:
            return False
        elif event.unicode and event.unicode.isprintable():
            self.input_text += event.unicode

        return True

    def _history_prev(self):
        if not self.input_history:
            return
        if self.history_idx == -1:
            self._saved_input = self.input_text
            self.history_idx = len(self.input_history) - 1
        elif self.history_idx > 0:
            self.history_idx -= 1
        self.input_text = self.input_history[self.history_idx]

    def _history_next(self):
        if self.history_idx == -1:
            return
        if self.history_idx < len(self.input_history) - 1:
            self.history_idx += 1
            self.input_text = self.input_history[self.history_idx]
        else:
            self.history_idx = -1
            self.input_text = getattr(self, '_saved_input', '')

    def _submit_command(self):
        raw = self.input_text.strip()
        self.input_text = ""
        self.history_idx = -1
        if not raw:
            return

        self.input_history.append(raw)

        if raw.lower() in ("quit", "exit", "q"):
            items = [(TEXT, f"> {raw}", BRIGHT_GREEN),
                     (TEXT, "Farewell, Dr. Voss.", BRIGHT_YELLOW)]
            self._add_content(items)
            self.state = "gameover"
            return

        result, room_changed = process_command(self.gs, raw)
        room_surface = None
        if room_changed:
            room_surface = draw_room(self.gs.player["room"])

        echo = [(TEXT, f"> {raw}", BRIGHT_GREEN)]
        body = self._parse_result(_strip_ansi(result or ""), room_surface)
        self._add_content(echo + body)

        if self.gs.flags.get("game_won"):
            self.state = "gameover"

    # ------------------------------------------------------------------
    #  Game state transitions
    # ------------------------------------------------------------------

    def _start_intro(self):
        self.state = "intro"
        try:
            pygame.mixer.music.fadeout(1000)
        except Exception:
            pass
        self.intro_lines = [
            ("The year is 1923.", BRIGHT_YELLOW),
            ("", WHITE),
            ("You are Dr. Elara Voss,", TEXT_COLOR),
            ("archaeologist. You stand in", TEXT_COLOR),
            ("the ruins of a monastery in", TEXT_COLOR),
            ("the Scottish Highlands.", TEXT_COLOR),
            ("", WHITE),
            ("Below you lies a complex", TEXT_COLOR),
            ("older than civilisation.", TEXT_COLOR),
            ("", WHITE),
            ("Your partner, Prof. Whitmore,", TEXT_COLOR),
            ("entered yesterday.", TEXT_COLOR),
            ("He has not returned.", BRIGHT_RED),
            ("", WHITE),
            ("HELP=cmds  HINT=stuck", DIM_COLOR),
            ("", WHITE),
            ("Press ENTER to begin...", BRIGHT_GREEN),
        ]

    def _start_game(self):
        self.state = "playing"
        self.gs = GameState()
        self.buffer = []

        room_surface = draw_room(self.gs.player["room"])
        look_text = _strip_ansi(get_look_text(self.gs))
        items = self._parse_result(look_text, room_surface)
        self._add_content(items)

    # ------------------------------------------------------------------
    #  Drawing
    # ------------------------------------------------------------------

    def _draw(self):
        self.screen.fill(BORDER_COLOR)
        self.native.fill(BLACK)

        if self.state == "splash":
            self._draw_splash()
        elif self.state == "intro":
            self._draw_intro()
        else:
            self._draw_content()
            self._draw_separator()
            self._draw_input()

        scaled = pygame.transform.scale(self.native, (WIN_W, WIN_H))
        self.screen.blit(scaled, (WIN_BORDER, WIN_BORDER))

    def _draw_splash(self):
        if not hasattr(self, '_splash_img'):
            splash_path = os.path.join(os.path.dirname(__file__), "splash.png")
            try:
                raw = pygame.image.load(splash_path).convert()
                self._splash_img = pygame.transform.scale(raw, (NATIVE_W, NATIVE_H))
            except Exception:
                self._splash_img = None

        if self._splash_img:
            self.native.blit(self._splash_img, (0, 0))
        else:
            draw_splash(self.native)

        prompt = self._render_text("Press any key to start", BRIGHT_GREEN)
        px = (NATIVE_W - prompt.get_width()) // 2
        py = NATIVE_H - self.char_h - 4
        self.native.blit(prompt, (px, py))

    def _draw_intro(self):
        y = 2
        for text, color in self.intro_lines:
            if y + self.char_h > NATIVE_H:
                break
            if text:
                surf = self._render_text(text, color)
                self.native.blit(surf, (0, y))
            y += self.char_h + 1

    def _draw_content(self):
        # Calculate total height of visible items to anchor at bottom
        total_h = 0
        for i in range(self.view_top, len(self.buffer)):
            total_h += self._item_height(self.buffer[i])

        # Start y so the last item sits flush against the input bar
        y = CONTENT_H - total_h
        if y < 0:
            y = 0

        idx = self.view_top
        while idx < len(self.buffer):
            item = self.buffer[idx]
            h = self._item_height(item)
            if y + h > CONTENT_H:
                break

            if item[0] == IMAGE:
                self.native.blit(item[1], (0, y))
            elif item[1]:
                surf = self._render_text(item[1], item[2])
                self.native.blit(surf, (0, y))

            y += h
            idx += 1

    def _draw_separator(self):
        pygame.draw.line(self.native, SEPARATOR_COLOR,
                         (0, INPUT_Y), (NATIVE_W, INPUT_Y), 1)

    def _draw_input(self):
        if self.more_waiting:
            more = self._render_text("[more]", BRIGHT_GREEN)
            self.native.blit(more, (0, INPUT_Y + 1))
            return

        if self.revealing:
            return

        prompt = "> "
        display_text = prompt + self.input_text
        cursor_char = "_" if self.cursor_visible else " "
        if self.state == "playing":
            display_text += cursor_char

        lines = _word_wrap(display_text, self.cols)
        max_lines = max(1, INPUT_H // self.char_h)
        y = INPUT_Y + 1
        for line in lines[-max_lines:]:
            if line:
                surf = self._render_text(line, INPUT_COLOR)
                self.native.blit(surf, (0, y))
            y += self.char_h

        if self.state == "gameover":
            msg = self._render_text("Press ENTER to exit.", BRIGHT_YELLOW)
            self.native.blit(msg, (0, INPUT_Y + 1))


def run_gui():
    gui = SpectrumGUI()
    gui.run()
