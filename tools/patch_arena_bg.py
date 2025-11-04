from pathlib import Path
import re
import shutil

ROOT = Path(__file__).resolve().parents[1]
src = ROOT / "assets" / "sprites" / "arena_bg.jpg"
dst = ROOT / "assets" / "sprites" / "arena_bg.jpg"
# Keep a copy path for optional external plate drops
alt = ROOT / "assets" / "arena_bg_japan.jpg"
if not src.exists() and alt.exists():
    shutil.copy2(alt, dst)
    print("copied arena_bg.jpg")

p = ROOT / "scenes" / "arena.tscn"
t = p.read_text(encoding="utf-8")
if "arena_bg.jpg" in t:
    print("already patched")
else:
    m = re.search(r"load_steps=(\d+)", t)
    if m:
        t = t.replace(m.group(0), f"load_steps={int(m.group(1)) + 1}", 1)
    insert_res = '[ext_resource type="Texture2D" path="res://assets/sprites/arena_bg.jpg" id="18_arenabg"]\n'
    idx = t.find("[sub_resource")
    t = t[:idx] + insert_res + "\n" + t[idx:]
    marker = '[node name="Parallax" type="Node2D" parent="."]\n'
    bg = (
        '[node name="Parallax" type="Node2D" parent="."]\n\n'
        '[node name="ArenaBG" type="Sprite2D" parent="Parallax"]\n'
        "position = Vector2(520, 200)\n"
        "scale = Vector2(1.15, 1.05)\n"
        'texture = ExtResource("18_arenabg")\n'
        "modulate = Color(0.92, 0.9, 0.95, 1)\n"
    )
    if marker in t:
        t = t.replace(marker, bg, 1)
        p.write_text(t, encoding="utf-8")
        print("arena patched")
    else:
        print("marker not found")
