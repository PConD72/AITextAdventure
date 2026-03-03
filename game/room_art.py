"""
Procedural room illustrations in ZX Spectrum style.
Each room gets a drawing function that renders onto a pygame Surface
at native ZX Spectrum resolution (256 wide x IMAGE_H tall).
"""

import pygame
import math
from game.spectrum import (
    BLACK, BLUE, RED, MAGENTA, GREEN, CYAN, YELLOW, WHITE,
    BRIGHT_BLUE, BRIGHT_RED, BRIGHT_MAGENTA, BRIGHT_GREEN,
    BRIGHT_CYAN, BRIGHT_YELLOW, BRIGHT_WHITE,
    NATIVE_W, IMAGE_H,
)

ART_W = NATIVE_W  # 256
ART_H = IMAGE_H   # 80


def create_art_surface():
    return pygame.Surface((ART_W, ART_H))


def draw_room(room_id):
    surf = create_art_surface()
    surf.fill(BLACK)
    fn = ROOM_ART.get(room_id, _draw_default)
    fn(surf)
    return surf


# ---------------------------------------------------------------------------
#  Helper drawing routines
# ---------------------------------------------------------------------------

def _ground(surf, color, y_start):
    pygame.draw.rect(surf, color, (0, y_start, ART_W, ART_H - y_start))


def _stars(surf, count=20, region_h=None):
    import random
    rng = random.Random(42)
    rh = region_h or int(ART_H * 0.5)
    for _ in range(count):
        x = rng.randint(0, ART_W - 1)
        y = rng.randint(0, rh)
        c = rng.choice([WHITE, BRIGHT_WHITE, YELLOW])
        surf.set_at((x, y), c)


def _mountain_range(surf, color, peaks, base_y):
    pts = [(0, base_y)]
    for px, py in peaks:
        pts.append((px, py))
    pts.append((ART_W, base_y))
    pts.append((ART_W, ART_H))
    pts.append((0, ART_H))
    pygame.draw.polygon(surf, color, pts)


def _stone_wall(surf, x, y, w, h, color=WHITE, mortar=BLACK):
    pygame.draw.rect(surf, color, (x, y, w, h))
    row_h = max(3, h // 5)
    for ry in range(y, y + h, row_h):
        pygame.draw.line(surf, mortar, (x, ry), (x + w, ry), 1)
        offset = (ry // row_h) % 2 * (w // 4)
        for rx in range(x + offset, x + w, w // 3):
            pygame.draw.line(surf, mortar, (rx, ry), (rx, ry + row_h), 1)


def _arch(surf, cx, y_top, width, height, color=WHITE, thickness=1):
    rect = pygame.Rect(cx - width // 2, y_top, width, height * 2)
    pygame.draw.arc(surf, color, rect, 0, math.pi, thickness)
    pygame.draw.line(surf, color, (cx - width // 2, y_top + height),
                     (cx - width // 2, y_top + height + height // 3), thickness)
    pygame.draw.line(surf, color, (cx + width // 2, y_top + height),
                     (cx + width // 2, y_top + height + height // 3), thickness)


def _pillar(surf, x, y1, y2, width=3, color=WHITE):
    pygame.draw.rect(surf, color, (x - width // 2, y1, width, y2 - y1))
    pygame.draw.rect(surf, color, (x - width // 2 - 1, y1, width + 2, 2))
    pygame.draw.rect(surf, color, (x - width // 2 - 1, y2 - 2, width + 2, 2))


def _torch(surf, x, y, color=BRIGHT_YELLOW):
    pygame.draw.rect(surf, (139, 90, 43), (x, y, 1, 5))
    pygame.draw.circle(surf, color, (x, y - 1), 2)
    surf.set_at((x, y - 2), BRIGHT_RED)


def _water(surf, y, h, color=BLUE):
    for wy in range(y, y + h, 2):
        wave_color = BRIGHT_BLUE if (wy // 2) % 2 == 0 else BLUE
        pygame.draw.line(surf, wave_color, (0, wy), (ART_W, wy), 1)


def _mushroom(surf, x, y, cap_w, cap_h, stem_h, cap_color, stem_color=WHITE):
    pygame.draw.rect(surf, stem_color, (x - 1, y - stem_h, 2, stem_h))
    pygame.draw.ellipse(surf, cap_color,
                        (x - cap_w // 2, y - stem_h - cap_h, cap_w, cap_h))


def _gear(surf, cx, cy, r, color=YELLOW, teeth=6):
    pygame.draw.circle(surf, color, (cx, cy), r, 1)
    pygame.draw.circle(surf, color, (cx, cy), max(1, r // 3), 1)
    for i in range(teeth):
        angle = 2 * math.pi * i / teeth
        x1 = cx + int((r - 1) * math.cos(angle))
        y1 = cy + int((r - 1) * math.sin(angle))
        x2 = cx + int((r + 2) * math.cos(angle))
        y2 = cy + int((r + 2) * math.sin(angle))
        pygame.draw.line(surf, color, (x1, y1), (x2, y2), 1)


def _spiral(surf, x, y, color, size):
    for step in range(0, 360 * 2, 20):
        a = math.radians(step)
        r = size * step / (360 * 2)
        px = int(x + r * math.cos(a))
        py = int(y + r * math.sin(a))
        if 0 <= px < ART_W and 0 <= py < ART_H:
            surf.set_at((px, py), color)


def _heart_shape(surf, cx, cy, scale, color):
    pts = []
    for a in range(0, 360, 10):
        t = math.radians(a)
        x = 16 * math.sin(t) ** 3
        y = -(13 * math.cos(t) - 5 * math.cos(2 * t) - 2 * math.cos(3 * t) - math.cos(4 * t))
        pts.append((cx + int(x * scale), cy + int(y * scale)))
    if len(pts) > 2:
        pygame.draw.polygon(surf, color, pts)


def _star_shape(surf, x, y, size, color):
    pts = []
    for i in range(10):
        a = math.radians(i * 36 - 90)
        r = size if i % 2 == 0 else size // 2
        pts.append((x + int(r * math.cos(a)), y + int(r * math.sin(a))))
    if len(pts) > 2:
        pygame.draw.polygon(surf, color, pts)


# ---------------------------------------------------------------------------
#  Individual room illustrations (all at 256 x 80)
# ---------------------------------------------------------------------------

def _draw_monastery_ruins(surf):
    # Sky
    pygame.draw.rect(surf, BLUE, (0, 0, ART_W, 35))
    _stars(surf, 10, 30)
    # Mountains
    _mountain_range(surf, (40, 40, 60),
                    [(30, 22), (70, 10), (110, 18), (160, 8),
                     (200, 16), (230, 12), (250, 20)], 35)
    # Ground
    _ground(surf, (60, 50, 40), 52)
    # Ruined walls
    _stone_wall(surf, 20, 24, 30, 28, (150, 150, 140))
    _stone_wall(surf, ART_W - 50, 20, 30, 32, (150, 150, 140))
    # Jagged wall tops
    pygame.draw.polygon(surf, (150, 150, 140),
                        [(20, 24), (28, 18), (40, 20), (50, 24)])
    pygame.draw.polygon(surf, (150, 150, 140),
                        [(ART_W - 50, 20), (ART_W - 40, 14), (ART_W - 28, 17), (ART_W - 20, 20)])
    # Dark entrance
    cx = ART_W // 2
    pygame.draw.ellipse(surf, BLACK, (cx - 18, 55, 36, 14))
    pygame.draw.ellipse(surf, (100, 100, 90), (cx - 19, 54, 38, 16), 1)
    for i in range(3):
        sw = 28 - i * 6
        pygame.draw.rect(surf, (max(30, 60 - i * 15),) * 3,
                         (cx - sw // 2, 59 + i * 3, sw, 3))
    # Moon
    pygame.draw.circle(surf, BRIGHT_YELLOW, (ART_W - 30, 14), 6)
    pygame.draw.circle(surf, BLUE, (ART_W - 27, 12), 5)


def _draw_stone_stairway(surf):
    surf.fill((20, 15, 10))
    cx = ART_W // 2
    # Curved wall
    pygame.draw.ellipse(surf, (80, 70, 60), (cx - 50, 2, 100, ART_H + 20), 1)
    # Steps
    for i in range(9):
        y = 8 + i * 8
        w = 44 - i * 2
        shade = max(30, 80 - i * 6)
        pygame.draw.rect(surf, (shade, shade - 5, shade - 10), (cx - w // 2, y, w, 4))
    # Spirals on walls
    for sx, sy in [(cx - 36, 18), (cx + 30, 35), (cx - 32, 55)]:
        _spiral(surf, sx, sy, CYAN, 5)
    # Light from above
    pygame.draw.polygon(surf, (30, 30, 50),
                        [(cx - 10, 0), (cx + 10, 0), (cx + 20, 15), (cx - 20, 15)])


def _draw_antechamber(surf):
    surf.fill((25, 20, 15))
    # Vaulted ceiling
    pygame.draw.arc(surf, (120, 110, 100),
                    pygame.Rect(10, -25, ART_W - 20, 60), 0, math.pi, 1)
    # Floor
    _ground(surf, (60, 55, 45), 60)
    # Pillars
    for px in [45, 105, 155, 210]:
        _pillar(surf, px, 16, 60, 3, (140, 130, 120))
    # Three doorways
    _arch(surf, 60, 28, 24, 16, CYAN, 1)
    _arch(surf, ART_W // 2, 28, 24, 16, GREEN, 1)
    _arch(surf, ART_W - 60, 28, 24, 16, CYAN, 1)
    # Rope on hook
    hx = 185
    pygame.draw.circle(surf, (150, 140, 130), (hx, 32), 2, 1)
    for i in range(4):
        pygame.draw.line(surf, YELLOW, (hx, 34 + i * 3),
                         (hx + 2 * (1 if i % 2 else -1), 37 + i * 3), 1)
    # Torch
    _torch(surf, 22, 30)


def _draw_hall_of_echoes(surf):
    surf.fill((15, 10, 20))
    vx, vy = ART_W // 2, ART_H // 3
    # Perspective corridor
    pygame.draw.polygon(surf, (50, 45, 55),
                        [(0, ART_H), (ART_W, ART_H), (vx + 28, vy + 20), (vx - 28, vy + 20)])
    pygame.draw.polygon(surf, (40, 35, 50),
                        [(0, 0), (ART_W, 0), (vx + 28, vy - 20), (vx - 28, vy - 20)])
    pygame.draw.polygon(surf, (35, 30, 40),
                        [(0, 0), (vx - 28, vy - 20), (vx - 28, vy + 20), (0, ART_H)])
    pygame.draw.polygon(surf, (30, 25, 35),
                        [(ART_W, 0), (vx + 28, vy - 20), (vx + 28, vy + 20), (ART_W, ART_H)])
    # Bronze pipes on walls
    pipe_c = (180, 140, 50)
    for i in range(6):
        t = i / 6.0
        lx = int(t * (vx - 28)) + 3
        ly_t = int(t * (vy - 20)) + 6
        ly_b = int(ART_H - t * (ART_H - vy - 20)) - 6
        pygame.draw.line(surf, pipe_c, (lx, ly_t), (lx, ly_b), 1)
        rx = int(ART_W - t * (ART_W - vx - 28)) - 3
        pygame.draw.line(surf, pipe_c, (rx, ly_t), (rx, ly_b), 1)
    # Sound arcs
    for r in range(6, 24, 6):
        pygame.draw.arc(surf, CYAN, pygame.Rect(vx - r, vy - r // 2, r * 2, r),
                        0, math.pi, 1)


def _draw_scriptorium(surf):
    surf.fill((25, 20, 15))
    _ground(surf, (55, 50, 40), 56)
    # Back wall
    pygame.draw.rect(surf, (70, 65, 55), (0, 8, ART_W, 30))
    # Shelves with tablets
    for sy in [12, 24, 36]:
        pygame.draw.rect(surf, (100, 90, 70), (6, sy, ART_W - 12, 2))
        for tx in range(10, ART_W - 10, 9):
            pygame.draw.rect(surf, (140, 130, 110), (tx, sy - 8, 5, 8))
    # Desk
    dy = 44
    pygame.draw.rect(surf, (90, 60, 30), (ART_W // 2 - 28, dy, 56, 12))
    pygame.draw.rect(surf, (70, 45, 20), (ART_W // 2 - 26, dy + 12, 52, 6))
    # Drawer
    pygame.draw.rect(surf, YELLOW, (ART_W // 2 - 10, dy + 3, 20, 5), 1)
    # Toolbox
    pygame.draw.rect(surf, (100, 70, 30), (ART_W - 36, 46, 18, 10))
    pygame.draw.rect(surf, YELLOW, (ART_W - 36, 46, 18, 10), 1)


def _draw_fungal_grotto(surf):
    surf.fill((5, 15, 10))
    # Cave ceiling
    pygame.draw.polygon(surf, (30, 25, 20),
                        [(0, 10), (40, 4), (100, 8), (160, 2), (220, 7), (ART_W, 5),
                         (ART_W, 0), (0, 0)])
    _ground(surf, (20, 30, 15), 62)
    # Glowing mushrooms
    glow1, glow2 = BRIGHT_GREEN, BRIGHT_CYAN
    _mushroom(surf, 40, 62, 18, 7, 22, glow1)
    _mushroom(surf, 100, 62, 24, 9, 28, glow2)
    _mushroom(surf, 170, 62, 16, 6, 18, glow1)
    _mushroom(surf, 210, 62, 20, 8, 24, glow2)
    # Small ones
    for mx in [28, 75, 140, 195, 240]:
        _mushroom(surf, mx, 64, 8, 4, 8, CYAN)
    # Glow halos
    for mx, my, r in [(40, 33, 10), (100, 25, 14), (210, 30, 11)]:
        pygame.draw.circle(surf, (0, 40, 30), (mx, my), r)
    # Pool with coin
    pygame.draw.ellipse(surf, (10, 30, 40), (ART_W // 2 - 22, 66, 44, 10))
    surf.set_at((ART_W // 2 + 4, 70), BRIGHT_YELLOW)


def _draw_observatory(surf):
    surf.fill(BLACK)
    # Dome with stars
    pygame.draw.arc(surf, (40, 40, 60),
                    pygame.Rect(6, -30, ART_W - 12, 80), 0, math.pi, 1)
    _stars(surf, 40, 40)
    _ground(surf, (40, 35, 30), 58)
    # Orrery
    cx, cy = ART_W // 2, 42
    # Pedestal
    pygame.draw.polygon(surf, (120, 110, 90),
                        [(cx - 10, cy + 10), (cx + 10, cy + 10),
                         (cx + 14, 58), (cx - 14, 58)])
    # Rings
    for r in [20, 16, 12, 8, 4]:
        pygame.draw.circle(surf, YELLOW, (cx, cy), r, 1)
    # Planets
    for angle, r, c in [(30, 20, BRIGHT_RED), (120, 16, BRIGHT_CYAN),
                         (200, 12, BRIGHT_GREEN), (300, 8, BRIGHT_YELLOW)]:
        a = math.radians(angle)
        pygame.draw.circle(surf, c, (cx + int(r * math.cos(a)), cy + int(r * math.sin(a))), 2)
    pygame.draw.circle(surf, BRIGHT_YELLOW, (cx, cy), 2)


def _draw_archive(surf):
    surf.fill((20, 15, 10))
    _ground(surf, (50, 45, 35), 62)
    # Shelves of cylinders
    for row in range(4):
        y = 6 + row * 13
        pygame.draw.rect(surf, (90, 80, 60), (6, y + 9, ART_W - 12, 2))
        for cx in range(10, ART_W - 10, 6):
            pygame.draw.rect(surf, (140, 130, 100), (cx, y, 4, 9))
    # Pedestal with tablet
    px = ART_W // 2
    pygame.draw.polygon(surf, (60, 55, 45),
                        [(px - 8, 50), (px + 8, 50), (px + 10, 62), (px - 10, 62)])
    pygame.draw.rect(surf, (160, 150, 120), (px - 6, 46, 12, 4))


def _draw_forge(surf):
    surf.fill((30, 15, 5))
    _ground(surf, (60, 40, 25), 58)
    # Forge basin
    fx = 70
    pygame.draw.rect(surf, (80, 60, 40), (fx - 16, 30, 32, 18))
    # Heat glow
    for r in range(10, 3, -2):
        c = (min(255, 150 + (10 - r) * 12), max(0, 40 - r * 3), 0)
        pygame.draw.circle(surf, c, (fx, 34), r)
    # Anvil
    ax = 140
    pygame.draw.polygon(surf, (140, 140, 150),
                        [(ax - 8, 44), (ax + 8, 44), (ax + 6, 52), (ax - 6, 52)])
    pygame.draw.rect(surf, (130, 130, 140), (ax - 2, 52, 5, 8))
    # Workbench
    wx = 195
    pygame.draw.rect(surf, (90, 60, 30), (wx, 36, 48, 12))
    pygame.draw.rect(surf, (80, 50, 25), (wx + 2, 48, 8, 10))
    pygame.draw.rect(surf, (80, 50, 25), (wx + 38, 48, 8, 10))
    # Tool rack
    for tx in range(16, 50, 7):
        pygame.draw.line(surf, (120, 110, 100), (tx, 14), (tx, 30), 1)


def _draw_crystal_cavern(surf):
    surf.fill((10, 5, 20))
    # Cave ceiling
    pygame.draw.polygon(surf, (20, 15, 30),
                        [(0, 16), (30, 6), (80, 12), (150, 4), (220, 10), (ART_W, 7),
                         (ART_W, 0), (0, 0)])
    _ground(surf, (25, 20, 35), 64)
    # Crystal formations
    crystals = [
        (35, 64, 10, 36, BRIGHT_MAGENTA),
        (85, 64, 14, 44, BRIGHT_CYAN),
        (145, 64, 8, 30, BRIGHT_MAGENTA),
        (195, 64, 12, 38, BRIGHT_CYAN),
        (60, 64, 6, 22, (200, 150, 255)),
        (230, 64, 8, 28, (200, 150, 255)),
    ]
    for cx, base, w, h, color in crystals:
        pts = [(cx - w // 4, base), (cx - w // 6, base - h),
               (cx, base - h - 4), (cx + w // 6, base - h),
               (cx + w // 4, base)]
        pygame.draw.polygon(surf, color, pts)
        pygame.draw.polygon(surf, BRIGHT_WHITE, pts, 1)
    # Niche with lens
    nx, ny = ART_W // 2 + 10, 36
    pygame.draw.rect(surf, (50, 40, 60), (nx - 5, ny - 4, 10, 8))
    pygame.draw.circle(surf, BRIGHT_WHITE, (nx, ny), 3)
    pygame.draw.circle(surf, BRIGHT_CYAN, (nx, ny), 2)


def _draw_underground_river(surf):
    surf.fill((10, 10, 15))
    # Cave ceiling
    pygame.draw.polygon(surf, (25, 20, 20),
                        [(0, 12), (60, 6), (130, 10), (200, 4), (ART_W, 8),
                         (ART_W, 0), (0, 0)])
    # Near bank
    river_y = 34
    pygame.draw.polygon(surf, (60, 50, 40),
                        [(0, river_y), (ART_W, river_y),
                         (ART_W, river_y - 5), (180, river_y - 7),
                         (70, river_y - 4), (0, river_y - 6)])
    # Far bank
    far_y = river_y + 20
    _ground(surf, (55, 45, 35), far_y)
    # River
    for wy in range(river_y, far_y, 2):
        c = BRIGHT_BLUE if (wy // 2) % 2 == 0 else BLUE
        pygame.draw.line(surf, c, (0, wy), (ART_W, wy), 1)
    # White caps
    import random
    rng = random.Random(99)
    for _ in range(8):
        wx = rng.randint(0, ART_W)
        wy = rng.randint(river_y + 2, far_y - 2)
        pygame.draw.line(surf, BRIGHT_WHITE, (wx, wy), (wx + rng.randint(2, 6), wy), 1)
    # Stone pillar
    px = ART_W // 2
    pygame.draw.rect(surf, (140, 130, 110), (px - 3, river_y - 12, 6, 12))
    pygame.draw.rect(surf, (160, 150, 130), (px - 4, river_y - 14, 8, 3))


def _draw_flooded_chamber(surf):
    surf.fill((10, 15, 25))
    # Walls
    _stone_wall(surf, 0, 8, 14, 30, (80, 75, 65), (50, 45, 35))
    _stone_wall(surf, ART_W - 14, 8, 14, 30, (80, 75, 65), (50, 45, 35))
    # Ceiling
    pygame.draw.rect(surf, (40, 35, 30), (0, 0, ART_W, 8))
    # Water
    water_y = 38
    for wy in range(water_y, ART_H, 2):
        depth = (wy - water_y) / max(1, ART_H - water_y)
        r = int(10 + 20 * (1 - depth))
        g = int(30 + 30 * (1 - depth))
        b = int(60 + 50 * (1 - depth))
        pygame.draw.line(surf, (r, g, b), (0, wy), (ART_W, wy), 1)
    # Ripples
    for rx in range(20, ART_W - 20, 30):
        pygame.draw.arc(surf, (80, 120, 160),
                        pygame.Rect(rx - 8, water_y - 1, 16, 4), 0, math.pi, 1)
    # Spirals on walls
    for sx in range(25, ART_W - 25, 40):
        _spiral(surf, sx, water_y - 10, CYAN, 4)


def _draw_puzzle_chamber(surf):
    surf.fill((25, 20, 20))
    floor_y = 32
    # Floor with grid
    pygame.draw.polygon(surf, (50, 45, 40),
                        [(30, ART_H), (ART_W - 30, ART_H),
                         (ART_W // 2 + 28, floor_y), (ART_W // 2 - 28, floor_y)])
    # Grid lines
    for i in range(5):
        t = i / 4.0
        lx = int(30 + t * (ART_W // 2 - 28 - 30))
        rx = int(ART_W - 30 - t * (ART_W - 30 - ART_W // 2 - 28))
        ly = int(ART_H - t * (ART_H - floor_y))
        pygame.draw.line(surf, (80, 75, 70), (lx, ly), (rx, ly), 1)
    for i in range(5):
        t = i / 4.0
        bx = int(30 + t * (ART_W - 60))
        tx = int(ART_W // 2 - 28 + t * 56)
        pygame.draw.line(surf, (80, 75, 70), (bx, ART_H), (tx, floor_y), 1)
    # Symbols on tiles
    sy = 52
    # Sun
    pygame.draw.circle(surf, BRIGHT_YELLOW, (ART_W // 2 - 12, sy), 3)
    # Moon
    pygame.draw.circle(surf, WHITE, (ART_W // 2 + 8, sy), 3)
    pygame.draw.circle(surf, (50, 45, 40), (ART_W // 2 + 10, sy - 1), 2)
    # Star
    _star_shape(surf, ART_W // 2 - 12, sy + 14, 3, BRIGHT_WHITE)
    # Wave
    pygame.draw.arc(surf, BRIGHT_CYAN,
                    pygame.Rect(ART_W // 2 + 4, sy + 10, 10, 6), 0, math.pi, 1)
    # Stone door
    pygame.draw.rect(surf, (100, 95, 85), (ART_W // 2 - 20, 6, 40, floor_y - 6))
    pygame.draw.rect(surf, (130, 125, 115), (ART_W // 2 - 20, 6, 40, floor_y - 6), 1)


def _draw_mechanism_room(surf):
    surf.fill((20, 15, 15))
    _ground(surf, (45, 40, 35), 62)
    # Gears
    _gear(surf, 60, 32, 20, YELLOW, 8)
    _gear(surf, 108, 26, 14, (180, 140, 50), 6)
    _gear(surf, 86, 52, 12, YELLOW, 6)
    _gear(surf, 142, 46, 16, (180, 140, 50), 7)
    _gear(surf, 48, 58, 8, YELLOW, 5)
    # Control panel
    px = 195
    py = 22
    pygame.draw.rect(surf, (80, 75, 70), (px, py, 50, 28))
    pygame.draw.rect(surf, (100, 95, 85), (px, py, 50, 28), 1)
    # Levers
    for i, lc in enumerate([BRIGHT_RED, BRIGHT_GREEN, BRIGHT_CYAN]):
        lx = px + 10 + i * 15
        pygame.draw.rect(surf, (60, 55, 50), (lx - 1, py + 6, 2, 16))
        pygame.draw.circle(surf, lc, (lx, py + 6), 2)
    # Channel
    pygame.draw.rect(surf, (20, 20, 25), (ART_W // 2 - 4, 66, 8, ART_H - 66))


def _draw_deep_stair(surf):
    surf.fill((15, 10, 10))
    _ground(surf, (50, 40, 35), 48)
    # Stairs up
    for i in range(5):
        y = 48 - i * 6
        shade = 50 + i * 6
        pygame.draw.rect(surf, (shade, shade - 5, shade - 10), (16, y, 70, 4))
    # Stairs down
    for i in range(5):
        y = 50 + i * 6
        shade = max(20, 50 - i * 6)
        pygame.draw.rect(surf, (shade, shade - 5, shade - 10), (ART_W - 86, y, 70, 4))
    # Wall carvings - kneeling figures
    for fx in range(70, 190, 22):
        pygame.draw.circle(surf, CYAN, (fx, 12), 2, 1)
        pygame.draw.line(surf, CYAN, (fx, 14), (fx, 22), 1)
        pygame.draw.line(surf, CYAN, (fx, 22), (fx - 2, 28), 1)
    # Light
    pygame.draw.circle(surf, BRIGHT_YELLOW, (ART_W // 2, 10), 5)
    for a in range(0, 360, 45):
        rad = math.radians(a)
        pygame.draw.line(surf, YELLOW,
                         (ART_W // 2 + int(6 * math.cos(rad)), 10 + int(6 * math.sin(rad))),
                         (ART_W // 2 + int(9 * math.cos(rad)), 10 + int(9 * math.sin(rad))), 1)
    # Heart
    _heart_shape(surf, ART_W // 2, 32, 0.25, BRIGHT_RED)


def _draw_prison_cells(surf):
    surf.fill((15, 12, 10))
    _ground(surf, (40, 35, 30), 58)
    # Cell doors
    for i, (dx, is_open) in enumerate([(20, True), (60, True), (100, True),
                                        (140, True), (180, True), (216, False)]):
        dy, dh, dw = 18, 40, 18
        dc = (100, 80, 60) if is_open else (120, 90, 70)
        pygame.draw.rect(surf, dc, (dx, dy, dw, dh))
        pygame.draw.rect(surf, (80, 65, 45), (dx, dy, dw, dh), 1)
        if not is_open:
            # Barred window
            wy = dy + 5
            pygame.draw.rect(surf, (30, 25, 20), (dx + 4, wy, 10, 7))
            for bx in range(dx + 5, dx + 14, 3):
                pygame.draw.line(surf, (140, 130, 110), (bx, wy), (bx, wy + 7), 1)
            # Face
            pygame.draw.circle(surf, (200, 180, 160), (dx + 9, wy + 3), 2)
            pygame.draw.rect(surf, BLACK, (dx + 14, dy + dh // 2, 2, 2))
    # Ceiling
    pygame.draw.rect(surf, (30, 25, 20), (0, 0, ART_W, 14))


def _draw_sanctum(surf):
    surf.fill(BLACK)
    # Obsidian walls - subtle vertical bands
    for x in range(0, ART_W, 14):
        shade = 12 + (x % 28) // 2
        pygame.draw.rect(surf, (shade, shade, shade + 3), (x, 0, 14, ART_H))
    _ground(surf, (10, 10, 15), 58)
    # White altar
    cx, ay = ART_W // 2, 40
    pygame.draw.polygon(surf, BRIGHT_WHITE,
                        [(cx - 14, ay), (cx + 14, ay), (cx + 18, 58), (cx - 18, 58)])
    pygame.draw.polygon(surf, WHITE,
                        [(cx - 14, ay), (cx + 14, ay), (cx + 18, 58), (cx - 18, 58)], 1)
    # Concentric rings
    for r in range(2, 14, 3):
        pygame.draw.circle(surf, YELLOW, (cx, ay - 2), r, 1)
    # Depression
    pygame.draw.circle(surf, (80, 80, 60), (cx, ay - 2), 2)
    # Arch with inscription
    _arch(surf, ART_W // 2, 4, 36, 16, YELLOW, 1)
    # Floating stars
    import random
    rng = random.Random(77)
    for _ in range(12):
        sx = rng.randint(10, ART_W - 10)
        sy = rng.randint(4, 32)
        surf.set_at((sx, sy), BRIGHT_YELLOW)


def _draw_the_heart(surf):
    surf.fill(BLACK)
    cx, cy = ART_W // 2, ART_H // 2
    # Rose-red glow
    for r in range(min(ART_W // 2, ART_H // 2), 6, -2):
        intensity = max(0, min(255, int(60 * (1 - r / (ART_H // 2)))))
        pygame.draw.circle(surf, (intensity + 30, intensity // 5, intensity // 5), (cx, cy), r)
    # Chamber outline
    pygame.draw.ellipse(surf, (180, 60, 60),
                        (cx - 100, cy - 36, 200, 72), 1)
    # Orb
    pygame.draw.circle(surf, BRIGHT_WHITE, (cx, cy), 8)
    pygame.draw.circle(surf, BRIGHT_CYAN, (cx, cy), 7)
    pygame.draw.circle(surf, BRIGHT_WHITE, (cx, cy), 5)
    # Stars inside
    import random
    rng = random.Random(123)
    for _ in range(8):
        a = rng.uniform(0, 2 * math.pi)
        d = rng.uniform(0, 4)
        surf.set_at((cx + int(d * math.cos(a)), cy + int(d * math.sin(a))), BRIGHT_YELLOW)
    # Rays
    for a in range(0, 360, 24):
        rad = math.radians(a)
        x1 = cx + int(10 * math.cos(rad))
        y1 = cy + int(10 * math.sin(rad))
        x2 = cx + int(18 * math.cos(rad))
        y2 = cy + int(18 * math.sin(rad))
        pygame.draw.line(surf, (200, 80, 80), (x1, y1), (x2, y2), 1)


def _draw_default(surf):
    surf.fill((15, 10, 10))
    _ground(surf, (40, 35, 30), 56)
    _stone_wall(surf, 0, 8, ART_W, 30, (70, 65, 55), (40, 35, 30))
    _torch(surf, ART_W // 2, 24)


# ---------------------------------------------------------------------------
#  Splash screen (fallback if splash.png not found)
# ---------------------------------------------------------------------------

def draw_splash(surf):
    """Draw a fallback splash screen at native resolution."""
    surf.fill(BLACK)
    w, h = surf.get_size()
    _mountain_range(surf, (30, 30, 50),
                    [(30, int(h * 0.15)), (70, int(h * 0.05)), (120, int(h * 0.12)),
                     (170, int(h * 0.03)), (210, int(h * 0.1)), (w - 20, int(h * 0.14))],
                    int(h * 0.4))
    _stars(surf, 30, int(h * 0.35))
    cx = w // 2
    pygame.draw.polygon(surf, (20, 20, 30),
                        [(cx - 30, int(h * 0.4)), (cx, int(h * 0.2)),
                         (cx + 30, int(h * 0.4)),
                         (cx + 24, int(h * 0.8)), (cx - 24, int(h * 0.8))])
    _ground(surf, (40, 35, 25), int(h * 0.4))
    pygame.draw.circle(surf, BRIGHT_YELLOW, (cx - 14, int(h * 0.44)), 2)
    return surf


# ---------------------------------------------------------------------------
#  Room art dispatch table
# ---------------------------------------------------------------------------

ROOM_ART = {
    "monastery_ruins": _draw_monastery_ruins,
    "stone_stairway": _draw_stone_stairway,
    "antechamber": _draw_antechamber,
    "hall_of_echoes": _draw_hall_of_echoes,
    "scriptorium": _draw_scriptorium,
    "fungal_grotto": _draw_fungal_grotto,
    "observatory": _draw_observatory,
    "archive": _draw_archive,
    "forge": _draw_forge,
    "crystal_cavern": _draw_crystal_cavern,
    "underground_river": _draw_underground_river,
    "flooded_chamber": _draw_flooded_chamber,
    "puzzle_chamber": _draw_puzzle_chamber,
    "mechanism_room": _draw_mechanism_room,
    "deep_stair": _draw_deep_stair,
    "prison_cells": _draw_prison_cells,
    "sanctum": _draw_sanctum,
    "the_heart": _draw_the_heart,
}
