"""Build Japanese katana character sheets from pose images (+ title bg)."""
from __future__ import annotations

from pathlib import Path

from PIL import Image, ImageEnhance

ROOT = Path(__file__).resolve().parents[1]
SPR = ROOT / "assets" / "sprites"
ASSETS = ROOT / "assets"
FW = FH = 128


def transparent(im: Image.Image, thresh: int = 248) -> Image.Image:
    im = im.convert("RGBA")
    px = im.load()
    for y in range(im.height):
        for x in range(im.width):
            r, g, b, a = px[x, y]
            # near-white studio bg
            if r >= thresh and g >= thresh and b >= thresh:
                px[x, y] = (255, 255, 255, 0)
            # light gray corners
            elif r > 230 and g > 230 and b > 230 and a > 0:
                px[x, y] = (r, g, b, 0)
    return im


def fit(im: Image.Image, tw=FW, th=FH) -> Image.Image:
    im = transparent(im)
    bbox = im.getbbox()
    if bbox:
        im = im.crop(bbox)
    scale = min((tw - 10) / im.width, (th - 10) / im.height)
    nw, nh = max(1, int(im.width * scale)), max(1, int(im.height * scale))
    im = im.resize((nw, nh), Image.LANCZOS)
    canvas = Image.new("RGBA", (tw, th), (0, 0, 0, 0))
    canvas.paste(im, ((tw - nw) // 2, th - nh - 2), im)
    return canvas


def nudge(im: Image.Image, dx: int = 0, dy: int = 0) -> Image.Image:
    canvas = Image.new("RGBA", im.size, (0, 0, 0, 0))
    canvas.paste(im, (dx, dy), im)
    return canvas


def recolor_enemy(im: Image.Image) -> Image.Image:
    im = im.convert("RGBA")
    px = im.load()
    for y in range(im.height):
        for x in range(im.width):
            r, g, b, a = px[x, y]
            if a < 8:
                continue
            # push cloth toward ash / keep blade pale
            if b > r + 15 and b > g:  # bluish kimono
                px[x, y] = (min(255, int(r * 0.4 + 30)), min(255, int(g * 0.4 + 35)), min(255, int(b * 0.55 + 55)), a)
            elif r > 150 and g < 100:
                px[x, y] = (210, 55, 45, a)
    return im


def load_pose(name: str) -> Image.Image:
    path = ASSETS / name
    return fit(Image.open(path))


def sheet(frames: list[Image.Image], path: Path):
    out = Image.new("RGBA", (FW * len(frames), FH), (0, 0, 0, 0))
    for i, f in enumerate(frames):
        out.paste(f, (i * FW, 0), f)
    path.parent.mkdir(parents=True, exist_ok=True)
    out.save(path)
    print("wrote", path, "frames", len(frames))


def main():
    idle = load_pose("pose_idle.jpg")
    slash = load_pose("pose_slash.jpg")
    parry = load_pose("pose_parry.jpg")
    db = load_pose("pose_deathblow.jpg")
    enemy_base = load_pose("pose_enemy.jpg")

    # Subtle variants for animation readability
    idle_b = nudge(idle, 0, -2)
    run1 = nudge(idle, 2, -1)
    run2 = nudge(idle, -1, 1)
    run3 = nudge(idle, 3, 0)
    run4 = nudge(idle, -2, 1)

    swing0 = nudge(db, -2, 0)          # windup high
    swing1 = db
    swing2 = slash                     # cut
    swing3 = nudge(slash, 2, 1)        # follow

    parry0 = nudge(parry, -1, 0)
    parry1 = parry
    parry2 = nudge(parry, 1, -1)
    parry3 = nudge(parry, 0, 1)
    parry4 = idle

    hurt = ImageEnhance.Color(slash.convert("RGBA")).enhance(0.7)
    hurt = ImageEnhance.Brightness(hurt).enhance(0.85)

    dead = slash.rotate(-90, expand=True, fillcolor=(0, 0, 0, 0))
    dead = fit(dead)

    player = [
        idle, idle_b,
        run1, run2, run3, run4,
        swing0, swing1, swing2, swing3,
        parry0, parry1, parry2, parry3, parry4,
        hurt,
        swing0, db, slash, swing3, idle,
        dead,
    ]
    sheet(player, SPR / "player_sheet.png")

    # Enemy sheet: 11 frames matching enemy.gd mapping
    e_idle = enemy_base
    e_walk = nudge(enemy_base, 2, 0)
    e_tele = nudge(enemy_base, -1, -2)
    e_strike = recolor_enemy(slash.copy()) if False else fit(Image.open(ASSETS / "pose_enemy.jpg"))
    # Build strike from enemy pose + player slash silhouette tint
    e_slash = recolor_enemy(slash.copy())
    e_broken = ImageEnhance.Brightness(enemy_base).enhance(0.75)
    e_dead = fit(enemy_base.rotate(-90, expand=True, fillcolor=(0, 0, 0, 0)))

    enemy = [
        e_idle, nudge(e_idle, 0, -1),
        e_walk, nudge(e_walk, -2, 1),
        e_tele, nudge(e_tele, 0, -2),
        e_slash, nudge(e_slash, 2, 0), nudge(e_slash, 3, 1),
        e_broken,
        e_dead,
    ]
    sheet(enemy, SPR / "enemy_sheet.png")

    ally = ImageEnhance.Brightness(idle).enhance(1.08)
    ally.save(SPR / "ally.png")

    title = ASSETS / "title_bg_japan.jpg"
    if title.exists():
        Image.open(title).convert("RGB").resize((1280, 720), Image.LANCZOS).save(SPR / "title_bg.jpg", quality=90)
        print("wrote title_bg.jpg")

    print("FRAME size", FW)


if __name__ == "__main__":
    main()
