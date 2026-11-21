#!/usr/bin/env python3
"""Velmara — a vintage travel poster for a place that does not exist.

Draws a 1024x1024 poster with PIL and saves it as poster.png next to this
script. Run:  python3 poster_gen.py

The entrypoint (main.py) ships the finished poster.png and copies it to
/output/entry.png, so the graded run needs no fonts and no Pillow.
"""
import math
import random

from PIL import Image, ImageDraw, ImageFilter, ImageFont

W = H = 1024
OUT = "poster.png"

# ---------------------------------------------------------------- palette
CREAM = (247, 236, 210)
CREAM_SOFT = (252, 244, 224)
INK = (22, 58, 56)          # deep teal ink for type and rules
INK_SOFT = (38, 84, 80)
TEAL_DEEP = (24, 74, 76)
TEAL_MID = (46, 110, 108)
TEAL_LIGHT = (96, 152, 148)
GOLD = (238, 183, 74)
GOLD_SOFT = (247, 205, 120)
PEACH = (244, 196, 138)
PEACH_DEEP = (232, 164, 104)
CORAL = (214, 110, 78)
GREEN = (74, 122, 88)
GREEN_DARK = (44, 86, 64)
CLOUD = (253, 246, 231)
CLOUD_SHADE = (238, 214, 178)

F_TITLE = "/usr/share/fonts/truetype/noto/NotoSerifDisplay-Black.ttf"
F_SERIF = "/usr/share/fonts/truetype/noto/NotoSerif-Bold.ttf"
F_SANS = "/usr/share/fonts/truetype/noto/NotoSans-Bold.ttf"

random.seed(20261121)


def lerp(a, b, t):
    return tuple(int(round(a[i] + (b[i] - a[i]) * t)) for i in range(3))


def vgrad(size, top, bottom):
    """Vertical gradient image."""
    w, h = size
    img = Image.new("RGB", (1, h))
    px = img.load()
    for y in range(h):
        px[0, y] = lerp(top, bottom, y / max(1, h - 1))
    return img.resize((w, h))


def draw_text_spaced(draw, xy, text, font, fill, spacing=0, anchor="mm"):
    """Draw text with manual letter spacing; returns width used."""
    x, y = xy
    widths = [draw.textlength(ch, font=font) for ch in text]
    total = sum(widths) + spacing * (len(text) - 1)
    if anchor == "mm":
        x -= total / 2
    elif anchor == "rm":
        x -= total
    for ch, wch in zip(text, widths):
        draw.text((x, y), ch, font=font, fill=fill, anchor="lm")
        x += wch + spacing
    return total


def draw_arched_text(base, text, font, fill, outline=None, outline_w=3,
                     cx=512, cy=640, radius=470, spread=0.62):
    """Draw text along an upward arc (letters rotated tangentially)."""
    layer = Image.new("RGBA", base.size, (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    widths = [d.textlength(ch, font=font) for ch in text]
    total = sum(widths)
    # angular width of the whole word
    ang_total = total / radius
    start = -math.pi / 2 - ang_total / 2
    # render the glyph on its own tile, rotate, paste centred on the arc
    pos = start
    for ch, wch in zip(text, widths):
        ang = pos + (wch / 2) / radius
        x = cx + radius * math.cos(ang)
        y = cy + radius * math.sin(ang)
        deg = math.degrees(ang) + 90
        tw, th = int(wch) + 44, font.size + 60
        tile = Image.new("RGBA", (tw, th), (0, 0, 0, 0))
        td = ImageDraw.Draw(tile)
        if outline is not None:
            td.text((tw / 2, th / 2), ch, font=font, fill=outline,
                    anchor="mm", stroke_width=outline_w, stroke_fill=outline)
        td.text((tw / 2, th / 2), ch, font=font, fill=fill, anchor="mm")
        tile = tile.rotate(deg, resample=Image.BICUBIC, expand=True)
        base.paste(tile, (int(x - tile.width / 2), int(y - tile.height / 2)),
                   tile)
        pos += wch / radius
    return base


def cloud_puff(draw, cx, cy, rx, ry, fill, shade):
    """One billowy cloud made of overlapping ellipses."""
    n = 7
    for i in range(n):
        t = i / (n - 1)
        x = cx - rx + 2 * rx * t
        r = ry * (0.55 + 0.45 * math.sin(math.pi * t))
        draw.ellipse([x - r * 1.15, cy - r, x + r * 1.15, cy + r * 0.9],
                     fill=fill)
    draw.ellipse([cx - rx, cy - ry * 0.35, cx + rx, cy + ry * 0.75],
                 fill=shade)


def cliff_poly(top, depth, tip_x=None):
    """Polygon for a floating island: flat green top, cliff sides curving
    in to a blunt tip below the centre."""
    top_y = max(p[1] for p in top)
    cx = tip_x if tip_x is not None else sum(p[0] for p in top) / len(top)
    left, right = [], []
    steps = 10
    for i in range(steps + 1):
        t = i / steps
        # ease-in: sides stay wide near the top, then sweep to the tip
        k = t ** 1.6
        y = top_y + depth * t
        left.append((top[0][0] + (cx - top[0][0]) * k, y))
        right.append((top[-1][0] + (cx - top[-1][0]) * k, y))
    # top edge left->right, right cliff down to the tip, left cliff back up
    return top + right[1:] + list(reversed(left[:-1]))


def waterfall(base, x, y0, y1, width, alpha=210):
    """A falling ribbon of water, widening and fading into mist."""
    layer = Image.new("RGBA", base.size, (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    steps = 40
    pts_l, pts_r = [], []
    for i in range(steps + 1):
        t = i / steps
        y = y0 + (y1 - y0) * t
        wob = math.sin(t * 9.0) * width * 0.08
        w = width * (0.8 + 0.5 * t)
        pts_l.append((x - w / 2 + wob, y))
        pts_r.append((x + w / 2 + wob, y))
    d.polygon(pts_l + list(reversed(pts_r)), fill=(228, 242, 236, alpha))
    for dx in (-width * 0.2, width * 0.15):
        d.line([(x + dx, y0 + 6), (x + dx * 1.2, y1 - 8)],
               fill=(255, 255, 255, int(alpha * 0.8)), width=3)
    layer = layer.filter(ImageFilter.GaussianBlur(1.6))
    base.alpha_composite(layer)


def build():
    img = Image.new("RGB", (W, H), CREAM)
    d = ImageDraw.Draw(img)

    # ---- sky: deep teal at top melting into warm peach at the horizon
    sky = vgrad((W, 700), (26, 78, 82), (246, 198, 138))
    img.paste(sky, (0, 0))

    # ---- faint sunburst rays behind the sun
    rays = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    rd = ImageDraw.Draw(rays)
    sx, sy = 822, 392
    for i in range(24):
        ang = math.radians(i * 15)
        x2 = sx + 300 * math.cos(ang)
        y2 = sy + 300 * math.sin(ang)
        rd.line([(sx, sy), (x2, y2)], fill=(250, 214, 140, 26), width=14)
    img.paste(Image.alpha_composite(img.convert("RGBA"), rays).convert("RGB"),
              (0, 0))
    d = ImageDraw.Draw(img)

    # ---- sun: halo then gold disc, low in the sky behind the right isle
    d.ellipse([sx - 128, sy - 128, sx + 128, sy + 128],
              fill=(250, 214, 140))
    d.ellipse([sx - 98, sy - 98, sx + 98, sy + 98], fill=GOLD)
    d.ellipse([sx - 98, sy - 98, sx + 98, sy + 98],
              outline=(214, 158, 52), width=3)

    # ---- right-hand island (mid distance)
    right_top = [(668, 470), (724, 452), (806, 458), (884, 478),
                 (918, 500), (676, 502)]
    d.polygon(cliff_poly(right_top, 118, tip_x=800), fill=(36, 92, 86))
    d.polygon(right_top + [(right_top[-1][0], 516), (right_top[0][0], 516)],
              fill=(58, 118, 96))
    # little white cottage on the right island
    d.rectangle([742, 424, 786, 456], fill=(252, 244, 224))
    d.polygon([(736, 424), (764, 404), (792, 424)], fill=CORAL)
    d.rectangle([758, 436, 768, 456], fill=INK)

    # ---- main island (the landmark): big, centre-left
    main_top = [(118, 520), (196, 496), (300, 488), (420, 496),
                (540, 514), (628, 540), (640, 556), (130, 556)]
    d.polygon(cliff_poly(main_top, 168, tip_x=380), fill=(26, 66, 62))
    d.polygon(main_top + [(640, 570), (118, 570)], fill=GREEN_DARK)
    d.polygon(main_top + [(640, 584), (118, 584)], fill=GREEN)
    # cliff strata, following the taper
    for t, y in ((0.35, 615), (0.65, 660)):
        k = 1 - t ** 1.6
        d.line([(130 + (380 - 130) * (1 - k), y),
                (640 - (640 - 380) * (1 - k), y)],
               fill=(16, 46, 44), width=3)

    # ---- village rooftops on the main island
    for (hx, hy, hw, hh, roof) in [
            (170, 470, 46, 30, CORAL), (228, 462, 40, 26, (224, 140, 90)),
            (286, 474, 52, 30, CORAL), (470, 468, 44, 28, (224, 140, 90)),
            (528, 476, 40, 24, CORAL)]:
        d.rectangle([hx, hy, hx + hw, hy + hh], fill=CREAM_SOFT)
        d.polygon([(hx - 4, hy), (hx + hw / 2, hy - 16),
                   (hx + hw + 4, hy)], fill=roof)
        d.rectangle([hx + hw / 2 - 4, hy + hh - 14, hx + hw / 2 + 4, hy + hh],
                    fill=INK)

    # ---- the lighthouse — the poster's one landmark
    lx = 392
    d.rectangle([lx - 16, 416, lx + 16, 492], fill=(252, 244, 224))
    d.rectangle([lx - 16, 442, lx + 16, 460], fill=CORAL)
    d.rectangle([lx - 16, 472, lx + 16, 488], fill=CORAL)
    d.rectangle([lx - 12, 400, lx + 12, 416], fill=INK)
    d.rectangle([lx - 20, 394, lx + 20, 400], fill=INK)
    # lamp glow
    glow = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    gd = ImageDraw.Draw(glow)
    gd.ellipse([lx - 34, 388, lx + 34, 428], fill=(255, 226, 150, 170))
    glow = glow.filter(ImageFilter.GaussianBlur(8))
    img.paste(Image.alpha_composite(img.convert("RGBA"), glow).convert("RGB"),
              (0, 0))
    d = ImageDraw.Draw(img)
    d.ellipse([lx - 8, 400, lx + 8, 414], fill=GOLD)
    # light beams from the lamp
    beam = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    bd = ImageDraw.Draw(beam)
    bd.polygon([(lx - 10, 406), (lx - 150, 346), (lx - 150, 376)],
               fill=(255, 240, 190, 60))
    bd.polygon([(lx + 10, 406), (lx + 170, 346), (lx + 170, 378)],
               fill=(255, 240, 190, 60))
    img.paste(Image.alpha_composite(img.convert("RGBA"), beam).convert("RGB"),
              (0, 0))
    d = ImageDraw.Draw(img)

    # ---- waterfalls off the main island into the cloud sea
    rgba = img.convert("RGBA")
    waterfall(rgba, 210, 556, 700, 16)
    waterfall(rgba, 560, 556, 690, 12)
    waterfall(rgba, 800, 502, 620, 10)
    img = rgba.convert("RGB")
    d = ImageDraw.Draw(img)

    # ---- sea of clouds (bottom): billows only, no hard top edge
    cloud_layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    cd = ImageDraw.Draw(cloud_layer)
    cd.rectangle([0, 780, W, H], fill=(*CLOUD, 255))
    for (cx, cy, rx, ry) in [
            (120, 712, 170, 42), (330, 700, 210, 48), (560, 706, 200, 46),
            (780, 700, 210, 48), (950, 712, 160, 42), (210, 758, 180, 38),
            (470, 766, 210, 40), (730, 762, 190, 38), (920, 800, 170, 36),
            (80, 830, 170, 36), (380, 850, 210, 40), (680, 860, 200, 38)]:
        cloud_puff(cd, cx, cy, rx, ry, (*CLOUD, 255), (242, 228, 200, 255))
    # faint warm shading low between the puffs
    for (cx, cy, rx, ry) in [(300, 800, 170, 20), (650, 810, 180, 20),
                              (880, 860, 140, 18), (180, 900, 150, 18)]:
        cd.ellipse([cx - rx, cy - ry, cx + rx, cy + ry],
                   fill=(*PEACH, 40))
    cloud_layer = cloud_layer.filter(ImageFilter.GaussianBlur(2))
    img.paste(Image.alpha_composite(img.convert("RGBA"),
                                    cloud_layer).convert("RGB"), (0, 0))
    d = ImageDraw.Draw(img)

    # mist where the waterfalls meet the clouds
    mist = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    md = ImageDraw.Draw(mist)
    for (cx, cy, r) in [(210, 700, 30), (560, 692, 26), (800, 622, 24)]:
        md.ellipse([cx - r, cy - r * 0.6, cx + r, cy + r * 0.6],
                   fill=(255, 255, 255, 110))
    mist = mist.filter(ImageFilter.GaussianBlur(10))
    img.paste(Image.alpha_composite(img.convert("RGBA"), mist).convert("RGB"),
              (0, 0))
    d = ImageDraw.Draw(img)

    # ---- airship, small, upper left sky
    ax, ay = 300, 300
    d.ellipse([ax - 78, ay - 26, ax + 78, ay + 26], fill=(226, 122, 88))
    d.ellipse([ax - 78, ay - 26, ax + 78, ay + 26], outline=(178, 84, 56),
              width=3)
    d.polygon([(ax - 78, ay), (ax + 78, ay), (ax + 40, ay + 14),
               (ax - 40, ay + 14)], fill=(214, 110, 78))
    d.rectangle([ax - 34, ay + 22, ax + 34, ay + 40], fill=(70, 60, 52))
    d.line([(ax - 60, ay + 26), (ax - 60, ay + 40)], fill=(70, 60, 52),
           width=3)
    d.line([(ax + 60, ay + 26), (ax + 60, ay + 40)], fill=(70, 60, 52),
           width=3)
    # tiny propellor lines
    d.line([(ax + 78, ay - 8), (ax + 92, ay - 20)], fill=INK, width=2)
    d.line([(ax + 78, ay + 8), (ax + 92, ay + 20)], fill=INK, width=2)

    # ---- birds
    for (bx, by, s) in [(520, 250, 14), (580, 215, 11), (620, 285, 9),
                        (150, 300, 10), (905, 310, 11)]:
        d.arc([bx - s, by - s // 2, bx, by + s // 2], 200, 340, fill=INK,
              width=3)
        d.arc([bx, by - s // 2, bx + s, by + s // 2], 200, 340, fill=INK,
              width=3)

    # ---- title: VELMARA, gently arched across the top in cream
    title_font = ImageFont.truetype(F_TITLE, 150)
    img = draw_arched_text(img.convert("RGBA"), "VELMARA", title_font,
                           (252, 244, 224, 255),
                           outline=(22, 58, 56, 255), outline_w=2,
                           cx=512, cy=1220, radius=1100).convert("RGB")
    d = ImageDraw.Draw(img)

    # ---- subtitle under the title arc, rules kept clear of the letters
    sub_font = ImageFont.truetype(F_SERIF, 34)
    sub_w = draw_text_spaced(d, (512, 372), "THE ISLES ABOVE THE SEA",
                             sub_font, INK, spacing=10, anchor="mm")
    half = sub_w / 2
    for (x0, x1) in [(512 - half - 120, 512 - half - 24),
                     (512 + half + 24, 512 + half + 120)]:
        d.line([(x0, 372), (x1, 372)], fill=INK, width=3)

    # ---- bottom band: cream ribbon with the tagline
    d.rectangle([36, 884, 988, 988], fill=CREAM)
    d.rectangle([36, 884, 988, 988], outline=INK, width=3)
    tag_font = ImageFont.truetype(F_SERIF, 40)
    draw_text_spaced(d, (512, 912), "WHERE THE SKY KEEPS ITS ISLANDS",
                     tag_font, INK, spacing=6, anchor="mm")
    small_font = ImageFont.truetype(F_SANS, 22)
    draw_text_spaced(d, (512, 956),
                     "TRAVEL BY AIRSHIP  ·  DEPARTURES DAILY",
                     small_font, INK_SOFT, spacing=4, anchor="mm")

    # ---- vintage border: double rule on cream paper
    d.rectangle([0, 0, W - 1, H - 1], outline=CREAM, width=36)
    d.rectangle([28, 28, W - 29, H - 29], outline=INK, width=4)
    d.rectangle([40, 40, W - 41, H - 41], outline=INK, width=2)
    # corner ornaments
    for (cx, cy) in [(40, 40), (984, 40), (40, 984), (984, 984)]:
        d.ellipse([cx - 7, cy - 7, cx + 7, cy + 7], fill=CORAL)

    # ---- gentle paper grain + vignette (print feel, keeps PNG small)
    px = img.load()
    for y in range(0, H, 2):
        for x in range(0, W, 2):
            n = random.randint(-5, 5)
            r, g, b = px[x, y]
            px[x, y] = (max(0, min(255, r + n)), max(0, min(255, g + n)),
                        max(0, min(255, b + n)))
    img.save(OUT, optimize=True)
    print("saved", OUT)


if __name__ == "__main__":
    build()
