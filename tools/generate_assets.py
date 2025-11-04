"""Japanese ink-pixel art for The Man Who — clearer parry & deathblow poses."""
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

OUT = (24, 20, 28, 255)
SKIN = (240, 205, 180, 255)
SKIN_S = (210, 160, 140, 255)
HAIR = (28, 24, 32, 255)
HAIR_H = (55, 48, 60, 255)
KIMONO = (245, 238, 225, 255)
KIMONO_S = (210, 195, 175, 255)
SASH = (180, 42, 48, 255)
SASH_S = (120, 28, 36, 255)
STEEL = (235, 240, 248, 255)
STEEL_S = (140, 155, 175, 255)
BOOT = (55, 45, 48, 255)
EN_ROBE = (55, 58, 72, 255)
EN_ROBE_S = (38, 40, 52, 255)
EN_MASK = (30, 28, 36, 255)
EN_EYE = (220, 70, 55, 255)
BAMBOO = (78, 130, 70, 255)
BAMBOO_S = (48, 90, 50, 255)
LEAF = (90, 150, 80, 255)
TORII = (170, 48, 42, 255)
TORII_S = (120, 32, 30, 255)
LANTERN = (240, 170, 80, 255)
GROUND = (78, 64, 55, 255)
GROUND_H = (110, 90, 75, 255)
SKY_TOP = (28, 32, 48, 255)
SKY_BOT = (70, 58, 72, 255)
MOON = (245, 235, 210, 255)
SPARK = (255, 245, 180, 255)
BLOOD = (160, 35, 40, 255)
TRANS = (0, 0, 0, 0)

FW, FH = 24, 24
UPSCALE = 4


def blank(w=FW, h=FH):
    return Image.new("RGBA", (w, h), TRANS)


def put(img, x, y, c):
    if 0 <= x < img.width and 0 <= y < img.height:
        img.putpixel((int(x), int(y)), c)


def rect(img, x0, y0, x1, y1, c):
    for y in range(y0, y1 + 1):
        for x in range(x0, x1 + 1):
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
    print("wrote", path, out.size)


def body_base(im, by, legs, kimono=KIMONO, kimono_s=KIMONO_S, hair=HAIR, mask=False):
    lx, ly, rx, ry = legs
    rect(im, lx, ly, lx + 2, 22, BOOT)
    rect(im, rx, ry, rx + 2, 22, BOOT)
    rect(im, 9, by + 8, 14, by + 16, kimono)
    rect(im, 10, by + 10, 13, by + 16, kimono_s)
    rect(im, 9, by + 12, 14, by + 14, SASH)
    rect(im, 10, by + 13, 13, by + 14, SASH_S)
    # head
    rect(im, 10, by + 2, 13, by + 7, SKIN)
    rect(im, 10, by + 5, 13, by + 7, SKIN_S)
    if mask:
        rect(im, 9, by + 1, 14, by + 6, EN_MASK)
        put(im, 11, by + 3, EN_EYE)
        put(im, 13, by + 3, EN_EYE)
        put(im, 9, by, EN_MASK)
        put(im, 14, by, EN_MASK)
    else:
        # topknot
        rect(im, 9, by, 14, by + 3, hair)
        rect(im, 11, by - 2, 12, by, hair)
        put(im, 11, by + 4, OUT)
        put(im, 13, by + 4, OUT)


def draw_player(pose: str, fr: int = 0) -> Image.Image:
    im = blank()
    if pose == "dead":
        rect(im, 3, 16, 19, 19, KIMONO)
        rect(im, 4, 17, 18, 18, KIMONO_S)
        rect(im, 5, 14, 10, 17, SKIN)
        rect(im, 5, 13, 10, 14, HAIR)
        rect(im, 11, 16, 15, 18, SASH)
        rect(im, 16, 16, 21, 17, STEEL)
        outline(im)
        return im

    bob = -1 if pose == "idle" and fr == 1 else 0
    by = 4 + bob
    if pose == "run":
        legs = [(7, 18, 13, 17), (8, 17, 12, 18), (7, 18, 13, 17), (8, 18, 12, 18)][fr % 4]
    else:
        legs = (8, 18, 12, 18)

    body_base(im, by, legs)

    if pose in ("idle", "run"):
        rect(im, 7, by + 9, 8, by + 14, SKIN)
        rect(im, 15, by + 9, 16, by + 14, SKIN)
        # sheathed katana
        rect(im, 15, by + 6, 16, by + 17, STEEL_S)
        put(im, 15, by + 5, SASH)
    elif pose == "swing":
        if fr == 0:
            rect(im, 5, by + 5, 8, by + 10, SKIN)
            rect(im, 2, by + 2, 6, by + 5, STEEL)
            rect(im, 15, by + 10, 16, by + 15, SKIN)
        elif fr == 1:
            rect(im, 4, by + 6, 8, by + 11, SKIN)
            rect(im, 1, by + 5, 5, by + 7, STEEL)
            put(im, 0, by + 5, STEEL_S)
        elif fr == 2:
            rect(im, 14, by + 7, 18, by + 11, SKIN)
            rect(im, 17, by + 5, 22, by + 8, STEEL)
            put(im, 21, by + 4, SPARK)
            rect(im, 7, by + 10, 8, by + 15, SKIN)
        else:
            rect(im, 14, by + 10, 17, by + 15, SKIN)
            rect(im, 16, by + 13, 21, by + 15, STEEL)
            rect(im, 7, by + 10, 8, by + 15, SKIN)
    elif pose == "parry":
        # 5 frames: ready -> raise -> clash -> hold -> settle
        rect(im, 7, by + 10, 8, by + 15, SKIN)
        if fr == 0:
            rect(im, 14, by + 6, 17, by + 12, SKIN)
            rect(im, 16, by + 3, 17, by + 14, STEEL)
        elif fr == 1:
            rect(im, 13, by + 3, 17, by + 10, SKIN)
            rect(im, 16, by, 18, by + 13, STEEL)
            put(im, 17, by - 1, STEEL_S)
        elif fr == 2:
            # clash — blade forward + big spark ring
            rect(im, 13, by + 4, 18, by + 10, SKIN)
            rect(im, 17, by + 1, 19, by + 14, STEEL)
            for p in ((20, by + 2), (21, by + 4), (20, by + 6), (22, by + 5), (19, by + 3), (21, by + 7)):
                put(im, p[0], p[1], SPARK)
            put(im, 20, by + 4, MOON)
        elif fr == 3:
            rect(im, 13, by + 4, 17, by + 11, SKIN)
            rect(im, 16, by + 1, 18, by + 14, STEEL)
            put(im, 19, by + 3, SPARK)
            put(im, 20, by + 5, SPARK)
        else:
            rect(im, 14, by + 7, 17, by + 13, SKIN)
            rect(im, 16, by + 4, 17, by + 15, STEEL)
    elif pose == "deathblow":
        # 5 frames: approach, raise overhead, decisive cut, follow, sheathe
        if fr == 0:
            rect(im, 5, by + 6, 8, by + 12, SKIN)
            rect(im, 2, by + 4, 6, by + 7, STEEL)
            rect(im, 15, by + 10, 16, by + 15, SKIN)
        elif fr == 1:
            rect(im, 6, by + 2, 9, by + 8, SKIN)
            rect(im, 7, by - 2, 9, by + 4, STEEL)
            put(im, 8, by - 3, STEEL_S)
            rect(im, 15, by + 10, 16, by + 15, SKIN)
        elif fr == 2:
            # horizontal kill cut
            rect(im, 13, by + 6, 19, by + 11, SKIN)
            rect(im, 17, by + 5, 23, by + 8, STEEL)
            for x in range(14, 23):
                put(im, x, by + 6, SPARK if x % 2 == 0 else MOON)
            put(im, 20, by + 4, BLOOD)
            put(im, 21, by + 7, BLOOD)
            rect(im, 7, by + 10, 8, by + 15, SKIN)
        elif fr == 3:
            rect(im, 14, by + 9, 18, by + 14, SKIN)
            rect(im, 16, by + 12, 22, by + 14, STEEL)
            put(im, 18, by + 10, BLOOD)
            rect(im, 7, by + 10, 8, by + 15, SKIN)
        else:
            rect(im, 7, by + 9, 8, by + 14, SKIN)
            rect(im, 15, by + 9, 16, by + 14, SKIN)
            rect(im, 15, by + 6, 16, by + 17, STEEL_S)
            put(im, 15, by + 5, SASH)
    elif pose == "hurt":
        rect(im, 6, by + 11, 8, by + 15, SKIN)
        rect(im, 15, by + 7, 17, by + 12, SKIN)
        put(im, 11, by + 4, BLOOD)

    outline(im)
    return im


def make_player():
    frames = (
        [draw_player("idle", 0), draw_player("idle", 1)]
        + [draw_player("run", i) for i in range(4)]
        + [draw_player("swing", i) for i in range(4)]
        + [draw_player("parry", i) for i in range(5)]
        + [draw_player("hurt", 0)]
        + [draw_player("deathblow", i) for i in range(5)]
        + [draw_player("dead", 0)]
    )
    # 2+4+4+5+1+5+1 = 22 frames
    sheet(frames, SPR / "player_sheet.png")


def draw_enemy(pose: str, fr: int = 0) -> Image.Image:
    im = blank()
    if pose == "dead":
        # dramatic fallen + blood
        rect(im, 2, 16, 20, 19, EN_ROBE)
        rect(im, 3, 17, 19, 18, EN_ROBE_S)
        rect(im, 4, 14, 10, 17, EN_MASK)
        put(im, 6, 15, EN_EYE)
        put(im, 12, 17, BLOOD)
        put(im, 14, 16, BLOOD)
        put(im, 15, 18, BLOOD)
        outline(im)
        return im

    bob = 2 if pose == "broken" else (0 if fr % 2 == 0 else -1)
    by = 4 + bob
    if pose == "walk":
        legs = [(7, 18, 13, 17), (8, 17, 12, 18)][fr % 2]
    else:
        legs = (8, 18, 12, 18)

    body_base(im, by, legs, EN_ROBE, EN_ROBE_S, HAIR, mask=True)

    if pose in ("idle", "walk"):
        rect(im, 7, by + 9, 8, by + 14, EN_ROBE_S)
        rect(im, 15, by + 9, 16, by + 14, EN_ROBE_S)
        rect(im, 15, by + 6, 16, by + 17, STEEL_S)
    elif pose == "telegraph":
        rect(im, 4, by + 3, 8, by + 9, EN_ROBE_S)
        rect(im, 1, by, 6, by + 4, STEEL)
        if fr == 1:
            put(im, 2, by - 1, EN_EYE)
            put(im, 0, by + 1, SPARK)
        rect(im, 15, by + 10, 16, by + 15, EN_ROBE_S)
    elif pose == "strike":
        if fr < 2:
            rect(im, 14, by + 6, 19, by + 11, EN_ROBE_S)
            rect(im, 18, by + 4, 23, by + 8, STEEL)
        else:
            rect(im, 14, by + 10, 18, by + 15, EN_ROBE_S)
            rect(im, 17, by + 12, 22, by + 15, STEEL)
        rect(im, 7, by + 10, 8, by + 15, EN_ROBE_S)
    elif pose == "broken":
        rect(im, 6, by + 12, 8, by + 16, EN_ROBE_S)
        rect(im, 15, by + 12, 17, by + 16, EN_ROBE_S)
        put(im, 11, by + 3, SPARK)
        put(im, 13, by + 4, SPARK)
        # cracked mask
        put(im, 12, by + 2, BLOOD)

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
    im = blank(20, 24)
    rect(im, 7, 18, 8, 22, BOOT)
    rect(im, 11, 18, 12, 22, BOOT)
    rect(im, 6, 10, 13, 19, SASH)
    rect(im, 7, 12, 12, 18, SASH_S)
    rect(im, 7, 4, 12, 10, SKIN)
    rect(im, 6, 2, 13, 5, HAIR)
    put(im, 9, 6, OUT)
    put(im, 11, 6, OUT)
    outline(im)
    im.resize((20 * UPSCALE, 24 * UPSCALE), Image.NEAREST).save(SPR / "ally.png")


def make_arena_props():
    ARENA.mkdir(parents=True, exist_ok=True)

    # bamboo
    b = blank(14, 40)
    rect(b, 6, 2, 8, 39, BAMBOO)
    rect(b, 7, 2, 7, 39, BAMBOO_S)
    for y in (8, 16, 24, 32):
        rect(b, 5, y, 9, y, BAMBOO_S)
    for lx, ly in ((9, 10), (2, 18), (10, 26), (1, 30)):
        rect(b, lx, ly, lx + 3, ly + 1, LEAF)
    outline(b)
    b.resize((14 * UPSCALE, 40 * UPSCALE), Image.NEAREST).save(ARENA / "bamboo.png")

    # torii post
    p = blank(12, 48)
    rect(p, 3, 2, 8, 47, TORII)
    rect(p, 4, 2, 7, 47, TORII_S)
    outline(p)
    p.resize((12 * UPSCALE, 48 * UPSCALE), Image.NEAREST).save(ARENA / "torii_post.png")

    # torii beam
    beam = blank(80, 12)
    rect(beam, 2, 4, 77, 8, TORII)
    rect(beam, 2, 5, 77, 6, TORII_S)
    rect(beam, 0, 2, 79, 4, TORII)
    rect(beam, 6, 1, 73, 2, SASH)
    outline(beam)
    beam.resize((80 * UPSCALE, 12 * UPSCALE), Image.NEAREST).save(ARENA / "torii_beam.png")

    # ground
    g = blank(40, 20)
    rect(g, 0, 6, 39, 19, GROUND)
    rect(g, 0, 6, 39, 9, GROUND_H)
    for x in range(0, 40, 5):
        put(g, x + 1, 5, LEAF)
        put(g, x + 2, 4, BAMBOO)
    g.resize((40 * UPSCALE, 20 * UPSCALE), Image.NEAREST).save(ARENA / "ground.png")

    # rock face reuse as dark earth under
    rf = blank(32, 24)
    rect(rf, 0, 0, 31, 23, (48, 40, 38, 255))
    for y in range(0, 24, 3):
        for x in range(0, 32, 4):
            put(rf, x, y, (38, 32, 30, 255))
    rf.resize((32 * UPSCALE, 24 * UPSCALE), Image.NEAREST).save(ARENA / "rock_face.png")

    # lantern
    lan = blank(12, 16)
    rect(lan, 5, 0, 6, 2, OUT)
    rect(lan, 2, 2, 9, 11, LANTERN)
    rect(lan, 3, 4, 8, 9, SPARK)
    rect(lan, 3, 11, 8, 13, BOOT)
    outline(lan)
    lan.resize((12 * UPSCALE, 12 * UPSCALE), Image.NEAREST).save(ARENA / "lantern.png")

    # mist
    mist = blank(48, 18)
    for y in range(18):
        for x in range(48):
            a = int(25 + 30 * abs(math.sin(x / 6.0 + y / 4.0)))
            put(mist, x, y, (200, 205, 215, a))
    mist.resize((48 * UPSCALE, 18 * UPSCALE), Image.NEAREST).save(ARENA / "mist.png")

    # ink night sky + moon
    sky = blank(64, 48)
    for y in range(48):
        t = y / 47
        c = tuple(int(SKY_TOP[i] * (1 - t) + SKY_BOT[i] * t) for i in range(3)) + (255,)
        for x in range(64):
            put(sky, x, y, c)
    random.seed(4)
    for _ in range(20):
        put(sky, random.randint(0, 63), random.randint(0, 20), (255, 245, 220, 200))
    # moon
    for y in range(6, 14):
        for x in range(48, 56):
            if (x - 52) ** 2 + (y - 10) ** 2 <= 16:
                put(sky, x, y, MOON)
    sky.resize((64 * UPSCALE, 48 * UPSCALE), Image.NEAREST).save(ARENA / "sky.png")

    # soft cloud / fog bank
    cloud = blank(40, 12)
    for cx, cy, r in ((10, 6, 5), (20, 5, 6), (30, 7, 4)):
        for y in range(12):
            for x in range(40):
                if (x - cx) ** 2 + (y - cy) ** 2 * 2 <= r * r:
                    put(cloud, x, y, (180, 175, 190, 160))
    cloud.resize((40 * UPSCALE, 12 * UPSCALE), Image.NEAREST).save(ARENA / "cloud.png")

    # distant hills instead of celeste mountain
    mt = blank(80, 28)
    for x in range(80):
        peak = 16 + int(6 * math.sin(x / 11.0)) + int(3 * math.sin(x / 5.0))
        for y in range(peak, 28):
            put(mt, x, y, (40, 44, 52, 255) if y > peak + 2 else (55, 60, 70, 255))
    mt.resize((80 * UPSCALE, 28 * UPSCALE), Image.NEAREST).save(ARENA / "mountain.png")

    # subtle wind (less busy)
    wind = blank(48, 24)
    random.seed(1)
    for _ in range(12):
        y = random.randint(2, 20)
        x0 = random.randint(0, 30)
        for x in range(x0, x0 + random.randint(5, 10)):
            put(wind, x, y, (255, 255, 255, 90))
    wind.resize((48 * UPSCALE, 24 * UPSCALE), Image.NEAREST).save(ARENA / "wind.png")

    # parry spark bigger
    sp = blank(12, 12)
    for p in [(6, 1), (6, 6), (6, 10), (1, 6), (10, 6), (3, 3), (9, 3), (3, 9), (9, 9), (4, 6), (8, 6)]:
        put(sp, p[0], p[1], SPARK)
    put(sp, 6, 6, MOON)
    outline(sp)
    sp.resize((12 * UPSCALE, 12 * UPSCALE), Image.NEAREST).save(SPR / "parry_spark.png")
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


def main():
    SPR.mkdir(parents=True, exist_ok=True)
    make_player()
    make_enemy()
    make_ally()
    make_arena_props()
    make_sfx()
    print("done frame=", FW * UPSCALE)


if __name__ == "__main__":
    main()
