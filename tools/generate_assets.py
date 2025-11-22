"""Idle Slayer × Celeste pixel art for The Man Who — custom-drawn chibi sword hero."""
from __future__ import annotations

import math
import random
import struct
import wave
from pathlib import Path

from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
SPR = ROOT / "assets" / "sprites"
ARENA = SPR / "arena"
SFX = ROOT / "assets" / "sfx"

# Limited Celeste-like palette
OUT = (28, 22, 32, 255)
SKIN = (255, 214, 186, 255)
SKIN_S = (230, 170, 140, 255)
HAIR = (42, 32, 48, 255)
HAIR_H = (72, 55, 78, 255)
TUNIC = (248, 242, 232, 255)
TUNIC_S = (210, 198, 180, 255)
SASH = (196, 48, 58, 255)
SASH_S = (140, 28, 38, 255)
STEEL = (240, 245, 252, 255)
STEEL_S = (150, 165, 185, 255)
BOOT = (58, 42, 48, 255)
CHEEK = (255, 150, 140, 255)
EN_ROBE = (52, 56, 78, 255)
EN_ROBE_S = (34, 36, 52, 255)
EN_MASK = (24, 22, 30, 255)
EN_EYE = (255, 72, 58, 255)
BAMBOO = (72, 128, 68, 255)
BAMBOO_S = (44, 88, 48, 255)
LEAF = (98, 158, 78, 255)
TORII = (188, 48, 42, 255)
TORII_S = (128, 28, 28, 255)
LANTERN = (255, 180, 78, 255)
GROUND = (86, 68, 54, 255)
GROUND_H = (120, 96, 72, 255)
SKY_TOP = (22, 26, 48, 255)
SKY_BOT = (68, 52, 72, 255)
MOON = (255, 244, 210, 255)
SPARK = (255, 248, 170, 255)
BLOOD = (176, 36, 42, 255)
FOG = (190, 195, 210, 255)
TRANS = (0, 0, 0, 0)

# Finer Idle Slayer detail (less blocky squares), side-view, nearest upscale
FW, FH = 64, 64
UPSCALE = 2  # display frame = 128×128


def blank(w=FW, h=FH):
    return Image.new("RGBA", (w, h), TRANS)


def put(img, x, y, c):
    if 0 <= x < img.width and 0 <= y < img.height:
        img.putpixel((int(x), int(y)), c)


def rect(img, x0, y0, x1, y1, c):
    for y in range(y0, y1 + 1):
        for x in range(x0, x1 + 1):
            put(img, x, y, c)


def disc(img, cx, cy, r, c):
    r2 = r * r
    for y in range(cy - r, cy + r + 1):
        for x in range(cx - r, cx + r + 1):
            if (x - cx) * (x - cx) + (y - cy) * (y - cy) <= r2:
                put(img, x, y, c)


def ellipse(img, cx, cy, rx, ry, c):
    for y in range(cy - ry, cy + ry + 1):
        for x in range(cx - rx, cx + rx + 1):
            if rx == 0 or ry == 0:
                continue
            if ((x - cx) / rx) ** 2 + ((y - cy) / ry) ** 2 <= 1.0:
                put(img, x, y, c)


def outline(img, color=OUT):
    base = img.copy()
    w, h = img.size
    for y in range(h):
        for x in range(w):
            if base.getpixel((x, y))[3] < 8:
                for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                    nx, ny = x + dx, y + dy
                    if 0 <= nx < w and 0 <= ny < h and base.getpixel((nx, ny))[3] > 8:
                        put(img, x, y, color)
                        break


def sheet(frames, path: Path):
    s = Image.new("RGBA", (FW * len(frames), FH), TRANS)
    for i, f in enumerate(frames):
        s.paste(f, (i * FW, 0), f)
    out = s.resize((s.width * UPSCALE, s.height * UPSCALE), Image.NEAREST)
    path.parent.mkdir(parents=True, exist_ok=True)
    out.save(path)
    print("wrote", path, out.size, "frames=", len(frames))


def save_up(img: Image.Image, path: Path, sx=UPSCALE, sy=None):
    sy = sx if sy is None else sy
    path.parent.mkdir(parents=True, exist_ok=True)
    img.resize((img.width * sx, img.height * sy), Image.NEAREST).save(path)
    print("wrote", path)


# --- Idle Slayer side-view slayer @64px (finer curves, less square blocks) ---

HAT = (232, 198, 120, 255)
HAT_S = (190, 150, 80, 255)
HAT_L = (248, 220, 150, 255)
PANTS = (48, 44, 58, 255)
PANTS_S = (32, 28, 40, 255)
SLEEVE = (236, 228, 214, 255)


def draw_blade(im, x0, y0, x1, y1, tip_spark=False, thick=1):
    steps = max(abs(x1 - x0), abs(y1 - y0), 1)
    for i in range(steps + 1):
        t = i / steps
        x = int(round(x0 + (x1 - x0) * t))
        y = int(round(y0 + (y1 - y0) * t))
        half = max(0, thick // 2)
        rect(im, x - half, y - half, x + half, y + half, STEEL if i % 3 else STEEL_S)
        if thick >= 2:
            put(im, x, y - half - 1, STEEL)
    if tip_spark:
        put(im, x1, y1, SPARK)
        put(im, x1 + 1, y1 - 1, MOON)
        put(im, x1 + 2, y1, SPARK)
        put(im, x1 + 1, y1 + 1, SPARK)


def sword_on_back(im, ox, oy):
    draw_blade(im, ox - 1, oy + 2, ox + 6, oy + 28, thick=2)
    rect(im, ox - 3, oy, ox + 1, oy + 5, SASH)
    rect(im, ox - 2, oy + 1, ox, oy + 4, SASH_S)
    put(im, ox - 1, oy - 1, STEEL)


def side_head(im, hx, hy, mask=False, hurt=False):
    """Rounded Idle Slayer head with finer face/hat detail."""
    ellipse(im, hx, hy + 1, 10, 11, SKIN)
    ellipse(im, hx, hy + 4, 9, 7, SKIN_S)
    put(im, hx + 5, hy + 2, CHEEK)
    if mask:
        ellipse(im, hx, hy, 11, 10, EN_MASK)
        put(im, hx + 3, hy - 1, EN_EYE)
        put(im, hx + 6, hy - 1, EN_EYE)
        put(im, hx + 4, hy + 1, EN_EYE)
        rect(im, hx - 2, hy - 14, hx + 3, hy - 8, EN_MASK)
        put(im, hx, hy - 15, EN_ROBE_S)
    else:
        # layered hair (strands, not one block)
        ellipse(im, hx - 1, hy - 4, 11, 8, HAIR)
        rect(im, hx - 10, hy - 6, hx + 9, hy + 1, HAIR)
        for dx in (-8, -5, -2, 1, 4, 7):
            put(im, hx + dx, hy - 9, HAIR_H)
        rect(im, hx - 1, hy - 16, hx + 2, hy - 8, HAIR)
        put(im, hx, hy - 17, HAIR_H)
        put(im, hx + 1, hy - 15, HAIR_H)
        # conical kasa with rim highlight
        ellipse(im, hx, hy - 8, 14, 4, HAT)
        rect(im, hx - 14, hy - 8, hx + 13, hy - 5, HAT)
        rect(im, hx - 12, hy - 9, hx + 11, hy - 7, HAT_S)
        rect(im, hx - 5, hy - 13, hx + 5, hy - 8, HAT)
        rect(im, hx - 3, hy - 14, hx + 3, hy - 12, HAT_L)
        put(im, hx - 10, hy - 6, HAT_L)
        # eye + brow + smile
        put(im, hx + 4, hy, OUT)
        put(im, hx + 5, hy, OUT)
        put(im, hx + 6, hy, OUT)
        put(im, hx + 4, hy - 2, HAIR)
        put(im, hx + 3, hy + 3, OUT)
        put(im, hx + 4, hy + 3, OUT)
        if hurt:
            put(im, hx + 2, hy + 1, BLOOD)
            put(im, hx + 7, hy - 1, BLOOD)


def side_torso(im, tx, ty, robe=TUNIC, robe_s=TUNIC_S, sash=SASH):
    # tapered torso (not a flat square)
    rect(im, tx + 1, ty, tx + 14, ty + 16, robe)
    rect(im, tx, ty + 2, tx + 15, ty + 15, robe)
    rect(im, tx + 2, ty + 3, tx + 13, ty + 15, robe_s)
    # collar fold
    rect(im, tx + 3, ty + 1, tx + 8, ty + 3, SLEEVE if robe == TUNIC else robe_s)
    rect(im, tx, ty + 8, tx + 15, ty + 12, sash)
    rect(im, tx + 1, ty + 9, tx + 14, ty + 11, SASH_S)
    put(im, tx + 7, ty + 10, SPARK if robe == TUNIC else sash)


def side_legs(im, bx, by, pose: str, fr: int, pants=PANTS):
    """Feet plant near y≈56."""
    if pose == "run":
        cycle = [
            ((bx - 3, by + 2), (bx + 10, by - 2)),
            ((bx - 1, by - 3), (bx + 9, by + 2)),
            ((bx + 2, by + 1), (bx + 7, by - 3)),
            ((bx - 2, by + 2), (bx + 11, by)),
            ((bx + 1, by - 2), (bx + 8, by + 2)),
            ((bx - 3, by), (bx + 10, by + 1)),
        ][fr % 6]
        (lx, ly), (rx, ry) = cycle
    elif pose == "jump":
        (lx, ly), (rx, ry) = (bx + 1, by - 4), (bx + 8, by - 3)
    elif pose == "fall":
        (lx, ly), (rx, ry) = (bx - 2, by + 1), (bx + 10, by + 2)
    elif pose == "dead":
        return
    else:
        bob = [0, -1, 0, 1][fr % 4] if pose == "idle" else 0
        (lx, ly), (rx, ry) = (bx, by + bob), (bx + 9, by + bob)

    # tapered calves
    rect(im, lx, ly, lx + 5, ly + 10, pants)
    rect(im, lx + 1, ly + 1, lx + 4, ly + 9, PANTS_S if pants == PANTS else pants)
    rect(im, rx, ry, rx + 5, ry + 10, pants)
    rect(im, rx + 1, ry + 1, rx + 4, ry + 9, PANTS_S if pants == PANTS else pants)
    rect(im, lx - 1, ly + 8, lx + 6, ly + 11, BOOT)
    rect(im, rx - 1, ry + 8, rx + 6, ry + 11, BOOT)
    put(im, lx + 5, ly + 10, HAT_S)
    put(im, rx + 5, ry + 10, HAT_S)


def _arm(im, x0, y0, x1, y1, skin=SKIN):
    """Short tapered arm segment."""
    shade = SKIN_S if skin == SKIN else skin
    steps = max(abs(x1 - x0), abs(y1 - y0), 1)
    for i in range(steps + 1):
        t = i / steps
        x = int(round(x0 + (x1 - x0) * t))
        y = int(round(y0 + (y1 - y0) * t))
        put(im, x, y, skin)
        put(im, x, y + 1, shade)
        put(im, x + 1, y, shade)


def draw_player(pose: str, fr: int = 0) -> Image.Image:
    im = blank()
    if pose == "dead":
        rect(im, 10, 44, 50, 54, TUNIC)
        rect(im, 12, 46, 48, 52, TUNIC_S)
        ellipse(im, 18, 40, 9, 8, SKIN)
        rect(im, 10, 30, 28, 40, HAIR)
        ellipse(im, 20, 28, 12, 4, HAT)
        draw_blade(im, 36, 48, 56, 50, thick=2)
        outline(im)
        return im

    bob = [0, -2, 0, -1][fr % 4] if pose == "idle" else 0
    lean = 0
    if pose == "run":
        bob = [0, -3, -1, -3, 0, -2][fr % 6]
        lean = 3
    elif pose == "jump":
        bob = -5
    elif pose == "fall":
        bob = -1
    elif pose == "hurt":
        bob = 2
        lean = -3

    hx = 28 + lean
    hy = 18 + bob
    tx = 20 + lean
    ty = 28 + bob
    bx = 22 + lean
    by = 46 + bob

    side_legs(im, bx, by, pose, fr)
    side_torso(im, tx, ty)
    side_head(im, hx, hy, hurt=(pose == "hurt"))

    if pose in ("idle", "run"):
        _arm(im, tx - 1, ty + 3, tx - 3, ty + 12)
        if pose == "run":
            ay = ty + (1 if fr % 2 == 0 else 8)
            _arm(im, tx + 12, ty + 3, tx + 18, ay)
            if fr % 2 == 0:
                put(im, tx + 19, ay - 1, SPARK)
        else:
            _arm(im, tx + 12, ty + 3, tx + 16, ty + 12)
        sword_on_back(im, tx - 2, ty - 4)
    elif pose == "jump":
        _arm(im, tx - 1, ty + 1, tx - 4, ty - 4)
        _arm(im, tx + 12, ty + 1, tx + 18, ty - 3)
        sword_on_back(im, tx - 2, ty - 4)
        put(im, bx - 5, by + 8, SPARK)
    elif pose == "fall":
        _arm(im, tx - 2, ty + 2, tx - 5, ty + 10)
        _arm(im, tx + 13, ty + 2, tx + 19, ty + 10)
        sword_on_back(im, tx - 2, ty - 4)
    elif pose == "swing":
        if fr == 0:
            _arm(im, tx + 2, ty + 2, tx - 4, ty - 6)
            draw_blade(im, tx - 6, ty - 12, tx - 1, ty + 1, thick=2)
            _arm(im, tx + 12, ty + 4, tx + 15, ty + 12)
        elif fr == 1:
            _arm(im, tx + 6, ty, tx + 8, ty - 10)
            draw_blade(im, tx + 7, ty - 22, tx + 10, ty - 6, tip_spark=True, thick=2)
            _arm(im, tx - 1, ty + 4, tx + 1, ty + 12)
        elif fr == 2:
            _arm(im, tx + 12, ty + 2, tx + 22, ty + 4)
            draw_blade(im, tx + 18, ty + 2, tx + 40, ty + 5, tip_spark=True, thick=2)
            for x in range(tx + 10, tx + 36):
                put(im, x, ty + 3 + (x % 2), SPARK if x % 2 == 0 else MOON)
            _arm(im, tx - 1, ty + 4, tx + 1, ty + 12)
        else:
            _arm(im, tx + 12, ty + 6, tx + 20, ty + 12)
            draw_blade(im, tx + 18, ty + 12, tx + 36, ty + 16, thick=2)
            _arm(im, tx - 1, ty + 4, tx + 1, ty + 12)
    elif pose == "parry":
        _arm(im, tx - 1, ty + 3, tx + 1, ty + 12)
        if fr <= 1:
            _arm(im, tx + 12, ty + 1, tx + 18, ty - 4)
            draw_blade(im, tx + 16, ty - 14, tx + 20, ty + 12, tip_spark=(fr == 1), thick=2)
        elif fr == 2:
            _arm(im, tx + 12, ty + 1, tx + 20, ty + 4)
            draw_blade(im, tx + 18, ty - 8, tx + 28, ty + 12, tip_spark=True, thick=2)
            for p in ((tx + 30, ty), (tx + 32, ty + 3), (tx + 31, ty + 7), (tx + 34, ty + 2)):
                put(im, p[0], p[1], SPARK)
            put(im, tx + 30, ty + 2, MOON)
        else:
            _arm(im, tx + 12, ty + 2, tx + 18, ty + 6)
            draw_blade(im, tx + 16, ty - 6, tx + 20, ty + 14, thick=2)
    elif pose == "deathblow":
        if fr == 0:
            _arm(im, tx + 2, ty + 2, tx - 6, ty - 2)
            draw_blade(im, tx - 10, ty - 6, tx - 2, ty + 2, thick=2)
        elif fr == 1:
            _arm(im, tx + 6, ty, tx + 8, ty - 12)
            draw_blade(im, tx + 7, ty - 24, tx + 10, ty - 8, tip_spark=True, thick=2)
        elif fr == 2:
            _arm(im, tx + 12, ty + 2, tx + 24, ty + 4)
            draw_blade(im, tx + 20, ty + 2, tx + 44, ty + 4, tip_spark=True, thick=2)
            for x in range(tx + 8, tx + 40):
                put(im, x, ty + 3, SPARK if x % 2 == 0 else MOON)
            put(im, tx + 36, ty + 1, BLOOD)
        elif fr == 3:
            _arm(im, tx + 12, ty + 5, tx + 22, ty + 10)
            draw_blade(im, tx + 18, ty + 12, tx + 38, ty + 14, thick=2)
            put(im, tx + 30, ty + 10, BLOOD)
        else:
            _arm(im, tx - 1, ty + 3, tx + 1, ty + 12)
            _arm(im, tx + 12, ty + 3, tx + 16, ty + 12)
            sword_on_back(im, tx - 2, ty - 4)
    elif pose == "hurt":
        _arm(im, tx - 2, ty + 6, tx - 4, ty + 14)
        _arm(im, tx + 13, ty + 1, tx + 18, ty - 2)
        sword_on_back(im, tx - 2, ty - 4)

    outline(im)
    return im


def make_player():
    frames = (
        [draw_player("idle", i) for i in range(4)]
        + [draw_player("run", i) for i in range(6)]
        + [draw_player("jump", i) for i in range(2)]
        + [draw_player("fall", i) for i in range(2)]
        + [draw_player("swing", i) for i in range(4)]
        + [draw_player("parry", i) for i in range(5)]
        + [draw_player("hurt", 0)]
        + [draw_player("deathblow", i) for i in range(5)]
        + [draw_player("dead", 0)]
    )
    sheet(frames, SPR / "player_sheet.png")


def draw_enemy(pose: str, fr: int = 0) -> Image.Image:
    im = blank()
    if pose == "dead":
        rect(im, 8, 46, 52, 56, EN_ROBE)
        rect(im, 10, 48, 50, 54, EN_ROBE_S)
        ellipse(im, 18, 42, 10, 9, EN_MASK)
        put(im, 20, 40, EN_EYE)
        put(im, 32, 50, BLOOD)
        put(im, 38, 52, BLOOD)
        outline(im)
        return im

    bob = 2 if pose == "broken" else ([0, -1][fr % 2] if pose in ("idle", "walk") else 0)
    lean = 2 if pose == "walk" else 0
    hx, hy = 28 + lean, 18 + bob
    tx, ty = 20 + lean, 28 + bob
    bx, by = 22 + lean, 46 + bob

    side_legs(im, bx, by, "walk" if pose == "walk" else "idle", fr, PANTS_S)
    side_torso(im, tx, ty, EN_ROBE, EN_ROBE_S, SASH_S)
    side_head(im, hx, hy, mask=True)

    if pose in ("idle", "walk", "broken"):
        _arm(im, tx - 1, ty + 3, tx - 3, ty + 12, EN_ROBE_S)
        _arm(im, tx + 12, ty + 3, tx + 16, ty + 12, EN_ROBE_S)
        sword_on_back(im, tx - 2, ty - 4)
        if pose == "broken":
            put(im, hx + 3, hy, SPARK)
            put(im, hx + 6, hy + 2, BLOOD)
    elif pose == "telegraph":
        _arm(im, tx + 2, ty + 1, tx - 6, ty - 8, EN_ROBE_S)
        draw_blade(im, tx - 10, ty - 16, tx - 2, ty - 2, tip_spark=(fr == 1), thick=2)
        _arm(im, tx + 12, ty + 4, tx + 15, ty + 12, EN_ROBE_S)
        if fr == 1:
            put(im, tx - 8, ty - 18, EN_EYE)
    elif pose == "strike":
        if fr < 2:
            _arm(im, tx + 12, ty + 2, tx + 22, ty + 4, EN_ROBE_S)
            draw_blade(im, tx + 18, ty + 2, tx + 42, ty + 5, tip_spark=True, thick=2)
        else:
            _arm(im, tx + 12, ty + 6, tx + 20, ty + 12, EN_ROBE_S)
            draw_blade(im, tx + 18, ty + 12, tx + 36, ty + 15, thick=2)
        _arm(im, tx - 1, ty + 4, tx + 1, ty + 12, EN_ROBE_S)

    outline(im)
    return im


def make_enemy():
    frames = (
        [draw_enemy("idle", 0), draw_enemy("idle", 1)]
        + [draw_enemy("walk", 0), draw_enemy("walk", 1)]
        + [draw_enemy("telegraph", 0), draw_enemy("telegraph", 1)]
        + [draw_enemy("strike", 0), draw_enemy("strike", 1), draw_enemy("strike", 2)]
        + [draw_enemy("broken", 0), draw_enemy("dead", 0)]
    )
    sheet(frames, SPR / "enemy_sheet.png")


def make_ally():
    im = blank(48, 64)
    hx, hy = 24, 18
    rect(im, 16, 48, 21, 58, BOOT)
    rect(im, 26, 48, 31, 58, BOOT)
    rect(im, 16, 30, 32, 50, SASH)
    rect(im, 17, 32, 31, 48, SASH_S)
    ellipse(im, hx, hy, 9, 10, SKIN)
    ellipse(im, hx - 1, hy - 4, 10, 7, HAIR)
    put(im, hx + 3, hy, OUT)
    put(im, hx + 4, hy + 2, OUT)
    put(im, hx + 2, hy + 1, CHEEK)
    outline(im)
    save_up(im, SPR / "ally.png")


def make_arena_bg():
    """Full-bleed pixel night shrine BG (replaces soft JPG for demo)."""
    w, h = 320, 180
    bg = blank(w, h)
    for y in range(h):
        t = y / (h - 1)
        c = tuple(int(SKY_TOP[i] * (1 - t) + SKY_BOT[i] * t) for i in range(3)) + (255,)
        for x in range(w):
            put(bg, x, y, c)
    random.seed(7)
    for _ in range(55):
        put(bg, random.randint(0, w - 1), random.randint(0, 70), (255, 245, 220, random.randint(140, 220)))
    # moon
    disc(bg, 268, 36, 14, MOON)
    disc(bg, 262, 32, 10, (255, 250, 230, 255))
    # distant hills
    for x in range(w):
        peak = 95 + int(10 * math.sin(x / 28.0)) + int(6 * math.sin(x / 11.0))
        for y in range(peak, 130):
            put(bg, x, y, (36, 40, 58, 255) if y > peak + 3 else (48, 52, 70, 255))
    # path strip
    rect(bg, 0, 128, w - 1, h - 1, GROUND)
    rect(bg, 0, 128, w - 1, 136, GROUND_H)
    for x in range(0, w, 8):
        put(bg, x + 2, 127, LEAF)
    # soft mist band
    for y in range(110, 128):
        for x in range(w):
            a = int(40 + 35 * abs(math.sin(x / 18.0 + y / 8.0)))
            put(bg, x, y, (FOG[0], FOG[1], FOG[2], a))
    # distant torii silhouette
    rect(bg, 140, 78, 146, 128, TORII_S)
    rect(bg, 200, 78, 206, 128, TORII_S)
    rect(bg, 130, 74, 216, 82, TORII)
    rect(bg, 134, 70, 212, 74, TORII_S)
    save_up(bg, SPR / "arena_bg.png", 4)  # 1280×720


def make_arena_props():
    ARENA.mkdir(parents=True, exist_ok=True)

    b = blank(16, 44)
    rect(b, 7, 2, 9, 43, BAMBOO)
    rect(b, 8, 2, 8, 43, BAMBOO_S)
    for y in (10, 18, 26, 34):
        rect(b, 5, y, 11, y, BAMBOO_S)
    for lx, ly in ((10, 12), (2, 20), (11, 28), (1, 34)):
        rect(b, lx, ly, lx + 4, ly + 2, LEAF)
    outline(b)
    save_up(b, ARENA / "bamboo.png")

    p = blank(14, 52)
    rect(p, 4, 2, 9, 51, TORII)
    rect(p, 5, 2, 8, 51, TORII_S)
    outline(p)
    save_up(p, ARENA / "torii_post.png")

    beam = blank(84, 14)
    rect(beam, 2, 5, 81, 10, TORII)
    rect(beam, 2, 6, 81, 8, TORII_S)
    rect(beam, 0, 2, 83, 5, TORII)
    rect(beam, 8, 1, 76, 2, SASH)
    outline(beam)
    save_up(beam, ARENA / "torii_beam.png")

    g = blank(48, 22)
    rect(g, 0, 6, 47, 21, GROUND)
    rect(g, 0, 6, 47, 10, GROUND_H)
    for x in range(0, 48, 6):
        put(g, x + 1, 5, LEAF)
        put(g, x + 3, 4, BAMBOO)
    save_up(g, ARENA / "ground.png")

    rf = blank(36, 26)
    rect(rf, 0, 0, 35, 25, (48, 40, 38, 255))
    for y in range(0, 26, 3):
        for x in range(0, 36, 4):
            put(rf, x, y, (38, 32, 30, 255))
    save_up(rf, ARENA / "rock_face.png")

    lan = blank(14, 18)
    rect(lan, 6, 0, 7, 3, OUT)
    rect(lan, 3, 3, 10, 12, LANTERN)
    rect(lan, 4, 5, 9, 10, SPARK)
    rect(lan, 4, 12, 9, 14, BOOT)
    outline(lan)
    save_up(lan, ARENA / "lantern.png")

    mist = blank(56, 20)
    for y in range(20):
        for x in range(56):
            a = int(28 + 36 * abs(math.sin(x / 7.0 + y / 4.0)))
            put(mist, x, y, (200, 205, 215, a))
    save_up(mist, ARENA / "mist.png")

    sky = blank(80, 56)
    for y in range(56):
        t = y / 55
        c = tuple(int(SKY_TOP[i] * (1 - t) + SKY_BOT[i] * t) for i in range(3)) + (255,)
        for x in range(80):
            put(sky, x, y, c)
    random.seed(4)
    for _ in range(28):
        put(sky, random.randint(0, 79), random.randint(0, 24), (255, 245, 220, 200))
    disc(sky, 58, 14, 7, MOON)
    save_up(sky, ARENA / "sky.png")

    cloud = blank(48, 14)
    for cx, cy, r in ((12, 7, 6), (24, 6, 7), (36, 8, 5)):
        for y in range(14):
            for x in range(48):
                if (x - cx) ** 2 + (y - cy) ** 2 * 2 <= r * r:
                    put(cloud, x, y, (180, 175, 190, 170))
    save_up(cloud, ARENA / "cloud.png")

    mt = blank(96, 32)
    for x in range(96):
        peak = 14 + int(8 * math.sin(x / 14.0)) + int(4 * math.sin(x / 6.0))
        for y in range(peak, 32):
            put(mt, x, y, (40, 44, 58, 255) if y > peak + 2 else (55, 60, 74, 255))
    save_up(mt, ARENA / "mountain.png")

    wind = blank(56, 28)
    random.seed(1)
    for _ in range(14):
        y = random.randint(2, 24)
        x0 = random.randint(0, 36)
        for x in range(x0, x0 + random.randint(6, 12)):
            put(wind, x, y, (255, 255, 255, 95))
    save_up(wind, ARENA / "wind.png")

    # keep pine/pillar/ridge/gem as simple matching props if scene refs them
    pine = blank(20, 40)
    for i, (w0, y0) in enumerate(((14, 8), (12, 16), (10, 24))):
        rect(pine, 10 - w0 // 2, y0, 10 + w0 // 2, y0 + 7, BAMBOO_S if i else BAMBOO)
    rect(pine, 9, 30, 11, 39, BOOT)
    outline(pine)
    save_up(pine, ARENA / "pine.png")

    pillar = blank(18, 48)
    rect(pillar, 4, 2, 13, 47, (70, 62, 58, 255))
    rect(pillar, 5, 2, 12, 47, (55, 48, 45, 255))
    outline(pillar)
    save_up(pillar, ARENA / "pillar.png")

    ridge = blank(64, 16)
    for x in range(64):
        y0 = 6 + int(3 * math.sin(x / 8.0))
        for y in range(y0, 16):
            put(ridge, x, y, GROUND if y > y0 + 2 else GROUND_H)
    save_up(ridge, ARENA / "ridge.png")

    gem = blank(10, 10)
    disc(gem, 5, 5, 3, (120, 200, 220, 255))
    put(gem, 5, 5, SPARK)
    outline(gem)
    save_up(gem, ARENA / "gem.png")

    sp = blank(14, 14)
    for p in [(7, 1), (7, 7), (7, 12), (1, 7), (12, 7), (3, 3), (11, 3), (3, 11), (11, 11)]:
        put(sp, p[0], p[1], SPARK)
    put(sp, 7, 7, MOON)
    outline(sp)
    save_up(sp, SPR / "parry_spark.png")

    make_arena_bg()
    print("wrote japanese arena props")


def write_wav(path, samples, rate=22050):
    path.parent.mkdir(parents=True, exist_ok=True)
    with wave.open(str(path), "w") as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(rate)
        w.writeframes(b"".join(struct.pack("<h", max(-32767, min(32767, int(s * 32767)))) for s in samples))


def tone(freq, dur, rate=22050, vol=0.4):
    n = int(rate * dur)
    return [math.sin(2 * math.pi * freq * (i / rate)) * vol * (1 - i / n) for i in range(n)]


def noise(dur, rate=22050, vol=0.3):
    n = int(rate * dur)
    return [(random.random() * 2 - 1) * vol * (1 - i / n) for i in range(n)]


def mix(*tracks):
    length = max(len(t) for t in tracks)
    out = [0.0] * length
    for t in tracks:
        for i, v in enumerate(t):
            out[i] += v
    return [max(-1.0, min(1.0, v)) for v in out]


def make_sfx():
    write_wav(SFX / "swing.wav", mix(noise(0.1, vol=0.2), tone(190, 0.08, vol=0.12)))
    write_wav(SFX / "parry.wav", mix(tone(1600, 0.06, vol=0.35), tone(2400, 0.04, vol=0.2), noise(0.03, vol=0.12)))
    write_wav(SFX / "hit.wav", mix(tone(90, 0.1, vol=0.35), noise(0.06, vol=0.2)))
    write_wav(SFX / "deathblow.wav", mix(tone(60, 0.28, vol=0.5), tone(200, 0.15, vol=0.25), noise(0.2, vol=0.28)))
    write_wav(SFX / "jump.wav", mix(tone(280, 0.06, vol=0.15)))
    write_wav(SFX / "telegraph.wav", mix(tone(140, 0.16, vol=0.15)))
    write_wav(SFX / "ally_death.wav", mix(tone(55, 0.25, vol=0.35), noise(0.2, vol=0.25)))


def make_title_bg():
    """Pixel title plate matching arena night palette."""
    w, h = 320, 180
    bg = blank(w, h)
    for y in range(h):
        t = y / (h - 1)
        c = tuple(int(SKY_TOP[i] * (1 - t) + SKY_BOT[i] * t) for i in range(3)) + (255,)
        for x in range(w):
            put(bg, x, y, c)
    random.seed(11)
    for _ in range(40):
        put(bg, random.randint(0, w - 1), random.randint(0, 60), (255, 245, 220, 180))
    disc(bg, 60, 40, 12, MOON)
    for x in range(w):
        peak = 100 + int(8 * math.sin(x / 20.0))
        for y in range(peak, h):
            put(bg, x, y, (36, 40, 58, 255))
    # silhouetted hero stance
    hero = draw_player("idle", 0)
    bg.paste(hero, (148, 110), hero)
    save_up(bg, SPR / "title_bg.png", 4)


def main():
    SPR.mkdir(parents=True, exist_ok=True)
    make_player()
    make_enemy()
    make_ally()
    make_arena_props()
    make_title_bg()
    make_sfx()
    print("done frame=", FW * UPSCALE)


if __name__ == "__main__":
    main()
