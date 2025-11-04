from PIL import Image
import os

dst = r"e:\projects\ThemanWHo\assets"

keyed = [
    ("player_idle.jpg", "player_idle.png", 210),
    ("enemy_idle.jpg", "enemy_idle.png", 210),
    ("ally_idle.jpg", "ally_idle.png", 210),
    ("prop_bamboo.jpg", "prop_bamboo.png", 205),
    ("prop_lantern.jpg", "prop_lantern.png", 205),
    ("prop_torii.jpg", "prop_torii.png", 205),
]

for src_name, out_name, thresh in keyed:
    path = os.path.join(dst, src_name)
    img = Image.open(path).convert("RGBA")
    pixels = img.load()
    w, h = img.size
    for y in range(h):
        for x in range(w):
            r, g, b, a = pixels[x, y]
            if r >= thresh and g >= thresh and b >= thresh and abs(r - g) < 25 and abs(g - b) < 25:
                pixels[x, y] = (r, g, b, 0)
            elif r >= thresh - 20 and g >= thresh - 20 and b >= thresh - 20 and abs(r - g) < 30:
                fade = int(max(0, min(255, (thresh - min(r, g, b)) * 12)))
                pixels[x, y] = (r, g, b, fade)
    img.save(os.path.join(dst, out_name), "PNG")
    print("wrote", out_name, img.size)

for name in ["bg_shrine.jpg", "ground_path.jpg"]:
    img = Image.open(os.path.join(dst, name)).convert("RGB")
    out = name.replace(".jpg", ".png")
    img.save(os.path.join(dst, out), "PNG")
    print("wrote", out, img.size)

print("done")
