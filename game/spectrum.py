"""
ZX Spectrum color palette, font helpers, and display constants.
All layout is defined at native 256x192, then scaled up for display.
"""

# ZX Spectrum standard colors (normal brightness)
BLACK = (0, 0, 0)
BLUE = (0, 0, 205)
RED = (205, 0, 0)
MAGENTA = (205, 0, 205)
GREEN = (0, 205, 0)
CYAN = (0, 205, 205)
YELLOW = (205, 205, 0)
WHITE = (205, 205, 205)

# ZX Spectrum bright colors
BRIGHT_BLACK = (0, 0, 0)
BRIGHT_BLUE = (0, 0, 255)
BRIGHT_RED = (255, 0, 0)
BRIGHT_MAGENTA = (255, 0, 255)
BRIGHT_GREEN = (0, 255, 0)
BRIGHT_CYAN = (0, 255, 255)
BRIGHT_YELLOW = (255, 255, 0)
BRIGHT_WHITE = (255, 255, 255)

# Native ZX Spectrum resolution
NATIVE_W = 256
NATIVE_H = 192

# Scale factor for the actual window
SCALE = 3
WIN_W = NATIVE_W * SCALE  # 768
WIN_H = NATIVE_H * SCALE  # 576

# Room art height (inline in content stream)
IMAGE_H = 80

# Input area at bottom of screen
INPUT_H = 20

# Content area fills the rest
CONTENT_H = NATIVE_H - INPUT_H  # 172
INPUT_Y = CONTENT_H

# Font: ZX Spectrum ROM font at size 15 gives 8px wide, 10px tall glyphs
CHAR_W = 8
CHAR_H = 10
COLS = NATIVE_W // CHAR_W          # 32
CONTENT_LINES = CONTENT_H // CHAR_H  # 17

# Kept for back-compat with imports but now equal to native dims
INNER_W = NATIVE_W
INNER_H = NATIVE_H
INNER_X = 0
BORDER = 0
FONT_SIZE = 8  # will be overridden by gui to find best match

# UI colors
BORDER_COLOR = BLUE
TEXT_BG = BLACK
IMAGE_BG = BLACK
TEXT_COLOR = WHITE
INPUT_COLOR = BRIGHT_GREEN
ROOM_NAME_COLOR = BRIGHT_YELLOW
PROMPT_COLOR = BRIGHT_GREEN
SEPARATOR_COLOR = CYAN
DIM_COLOR = (100, 100, 100)
