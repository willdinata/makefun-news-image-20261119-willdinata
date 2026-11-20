"""
The Morning Atlas — Newspaper Front Page Renderer (Thursday 19 November 2026)
Renders stories.py data into entry.png using Pillow.
"""

import os
import math
from PIL import Image, ImageDraw, ImageFont
import stories

# Canvas and layout dimensions
WIDTH, HEIGHT = 1024, 1024

# Font paths
SERIF_BOLD = "/usr/share/fonts/truetype/liberation/LiberationSerif-Bold.ttf"
SERIF_ITALIC = "/usr/share/fonts/truetype/liberation/LiberationSerif-Italic.ttf"
SANS_BOLD = "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf"
SANS_REG = "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf"
DEJA_BOLD = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
DEJA_REG = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"

def get_font(path, size):
    try:
        return ImageFont.truetype(path, size)
    except Exception:
        return ImageFont.load_default()

def wrap(text, font, max_width):
    """Wrap text into lines fitting max_width using font.getlength or getbbox."""
    words = text.split()
    if not words:
        return [""]
    lines = []
    current_line = []
    for word in words:
        test_line = " ".join(current_line + [word])
        try:
            w = font.getlength(test_line)
        except AttributeError:
            bbox = font.getbbox(test_line)
            w = bbox[2] - bbox[0]
        if w <= max_width or not current_line:
            current_line.append(word)
        else:
            lines.append(" ".join(current_line))
            current_line = [word]
    if current_line:
        lines.append(" ".join(current_line))
    return lines

def wrap_with_ellipsis(text, font, max_width, max_lines=3):
    """Wrap text to max_width and max_lines, ending the last line with '…' if truncated."""
    words = text.split()
    if not words:
        return [""]
    lines = []
    current_line = []
    
    for word in words:
        if len(lines) == max_lines - 1:
            test_line = " ".join(current_line + [word]) + "…"
            try:
                w = font.getlength(test_line)
            except AttributeError:
                bbox = font.getbbox(test_line)
                w = bbox[2] - bbox[0]
            if w <= max_width or not current_line:
                current_line.append(word)
            else:
                lines.append(" ".join(current_line) + "…")
                current_line = []
                break
        else:
            test_line = " ".join(current_line + [word])
            try:
                w = font.getlength(test_line)
            except AttributeError:
                bbox = font.getbbox(test_line)
                w = bbox[2] - bbox[0]
            if w <= max_width or not current_line:
                current_line.append(word)
            else:
                lines.append(" ".join(current_line))
                current_line = [word]
    if current_line and len(lines) < max_lines:
        lines.append(" ".join(current_line))
    elif current_line and len(lines) == max_lines - 1:
        lines.append(" ".join(current_line) + "…")
    return lines[:max_lines]

def fit_text(text, font_path, size, max_width, max_lines=2):
    """Finds the largest font size (down from size) that fits text within max_lines."""
    s = size
    while s >= 8:
        font = get_font(font_path, s)
        lines = wrap(text, font, max_width)
        if len(lines) <= max_lines:
            return font, lines
        s -= 1
    return get_font(font_path, 8), wrap(text, get_font(font_path, 8), max_width)

def draw_icon(draw, name, box, colour):
    """Draws a 24x24 white geometric pictogram inside box (x, y, w, h)."""
    bx, by, bw, bh = box
    cx, cy = bx + bw / 2, by + bh / 2
    stroke = 2
    c = (255, 255, 255)

    if name == "flag":
        # Pole + triangular flag
        px = bx + 6
        draw.line([(px, by + 3), (px, by + 21)], fill=c, width=stroke)
        draw.polygon([(px, by + 4), (bx + 18, by + 9), (px, by + 14)], fill=c)
    elif name == "scales":
        # Post, beam, two hanging triangle pans
        draw.line([(cx, by + 4), (cx, by + 20)], fill=c, width=stroke)
        draw.line([(bx + 5, by + 7), (bx + 19, by + 7)], fill=c, width=stroke)
        # left pan
        draw.polygon([(bx + 5, by + 7), (bx + 2, by + 14), (bx + 8, by + 14)], fill=c)
        # right pan
        draw.polygon([(bx + 19, by + 7), (bx + 16, by + 14), (bx + 22, by + 14)], fill=c)
    elif name == "chart":
        # Axis + 3 rising bars + arrow
        ax, ay = bx + 4, by + 20
        draw.line([(ax, by + 4), (ax, ay)], fill=c, width=stroke)
        draw.line([(ax, ay), (bx + 20, ay)], fill=c, width=stroke)
        # bars
        draw.rectangle([ax + 3, by + 14, ax + 6, ay], fill=c)
        draw.rectangle([ax + 8, by + 10, ax + 11, ay], fill=c)
        draw.rectangle([ax + 13, by + 6, ax + 16, ay], fill=c)
    elif name == "flame":
        # Teardrop / flame polygon
        draw.polygon([(cx, by + 3), (bx + 19, by + 14), (cx, by + 21), (bx + 5, by + 14)], fill=c)
    elif name == "tower":
        # Tall rectangle, battlements, window dots
        tx, ty, tw, th = bx + 6, by + 3, 12, 18
        draw.rectangle([tx, ty + 3, tx + tw, ty + th], outline=c, width=stroke)
        draw.line([(tx, ty + 3), (tx + tw, ty + 3)], fill=c, width=stroke)
        draw.point([(tx + 4, ty + 7), (tx + 8, ty + 7), (tx + 4, ty + 12), (tx + 8, ty + 12)], fill=c)
    elif name == "coin":
        draw.ellipse([bx + 4, by + 4, bx + 20, by + 20], outline=c, width=stroke)
        draw.ellipse([bx + 9, by + 9, bx + 15, by + 15], outline=c, width=stroke)
    elif name == "pin":
        draw.ellipse([bx + 6, by + 3, bx + 18, by + 15], outline=c, width=stroke)
        draw.line([(cx, by + 15), (cx, by + 21)], fill=c, width=stroke)
    elif name == "leaf":
        draw.ellipse([bx + 5, by + 4, bx + 19, by + 20], fill=c)
        draw.line([(cx, by + 15), (cx, by + 21)], fill=colour, width=stroke) # stalk in region colour or bg
    elif name == "burst":
        # 8-ray star
        for i in range(8):
            angle = i * math.pi / 4
            x2 = cx + math.cos(angle) * 9
            y2 = cy + math.sin(angle) * 9
            draw.line([(cx, cy), (x2, y2)], fill=c, width=stroke)
    elif name == "cross":
        draw.rectangle([cx - 2, by + 5, cx + 2, by + 19], fill=c)
        draw.rectangle([bx + 5, cy - 2, bx + 19, cy + 2], fill=c)
    elif name == "cyclone":
        # Three spiral arcs / curved lines approximation
        for r in [4, 8, 12]:
            draw.arc([cx - r, cy - r, cx + r, cy + r], start=0, end=200, fill=c, width=stroke)
    elif name == "rocket":
        draw.polygon([(cx, by + 3), (bx + 15, by + 14), (bx + 13, by + 20), (cx, by + 17), (bx + 11, by + 20), (bx + 9, by + 14)], fill=c)
        draw.ellipse([cx - 2, by + 9, cx + 2, by + 13], outline=colour, width=1)
    elif name == "ballot":
        draw.rectangle([bx + 4, by + 5, bx + 20, by + 21], outline=c, width=stroke)
        draw.line([(bx + 4, by + 9), (bx + 20, by + 9)], fill=c, width=stroke)
        draw.line([(bx + 8, by + 14), (bx + 11, by + 17), (bx + 17, by + 11)], fill=c, width=stroke)
    elif name == "shield":
        draw.polygon([(cx, by + 3), (bx + 19, by + 6), (bx + 19, by + 14), (cx, by + 21), (bx + 5, by + 14), (bx + 5, by + 6)], outline=c, width=stroke)
        draw.line([(bx + 8, cy), (bx + 11, cy + 3), (bx + 16, cy - 3)], fill=c, width=stroke)
    elif name == "building":
        draw.rectangle([bx + 5, by + 5, bx + 19, by + 21], outline=c, width=stroke)
        draw.rectangle([bx + 8, by + 8, bx + 11, by + 11], fill=c)
        draw.rectangle([bx + 13, by + 8, bx + 16, by + 11], fill=c)
        draw.rectangle([bx + 8, by + 14, bx + 11, by + 17], fill=c)
        draw.rectangle([bx + 13, by + 14, bx + 16, by + 17], fill=c)
    elif name == "star":
        pts = []
        for i in range(10):
            angle = i * math.pi / 5
            r = 9 if i % 2 == 0 else 4
            pts.append((cx + math.cos(angle) * r, cy + math.sin(angle) * r))
        draw.polygon(pts, fill=c)
    elif name == "bolt":
        draw.polygon([(cx + 2, by + 3), (bx + 5, cy + 2), (cx + 1, cy + 2), (bx + 8, by + 21), (bx + 17, cy - 1), (cx + 4, cy - 1)], fill=c)
    elif name == "ship":
        draw.polygon([(bx + 4, by + 15), (bx + 20, by + 15), (bx + 17, by + 20), (bx + 7, by + 20)], fill=c)
        draw.line([(cx, by + 5), (cx, by + 15)], fill=c, width=stroke)
        draw.polygon([(cx, by + 6), (bx + 15, by + 10), (cx, by + 14)], fill=c)
    else:
        draw.rectangle([bx + 6, by + 6, bx + 18, by + 18], fill=c)

def draw_pill(draw, x, y, label, colour, icon_name=""):
    """Draws a compact rounded pill filled with colour carrying icon and label. Returns pill width."""
    font = get_font(SANS_BOLD, 10)
    try:
        tw = font.getlength(label)
    except AttributeError:
        bbox = font.getbbox(label)
        tw = bbox[2] - bbox[0]
    
    pad_h = 6
    icon_w = 14 if icon_name else 0
    spacing = 4 if icon_name else 0
    pill_w = int(pad_h * 2 + icon_w + spacing + tw)
    pill_h = 17

    # Draw rounded rectangle pill
    draw.rounded_rectangle([x, y, x + pill_w, y + pill_h], radius=pill_h // 2, fill=colour)

    # Draw icon inside pill left end
    if icon_name:
        ibox = (x + 3, y + (pill_h - 14) / 2, 14, 14)
        draw_icon(draw, icon_name, ibox, colour)

    # Draw text
    tx = x + pad_h + icon_w + spacing
    ty = y + (pill_h - 10) / 2 - 1
    draw.text((tx, ty), label, fill=(255, 255, 255), font=font)
    return pill_w

def draw_mini_pill(draw, x, y, label, colour, icon_name=""):
    """Smaller pill for briefs (height 14). Returns width."""
    font = get_font(SANS_BOLD, 8)
    try:
        tw = font.getlength(label)
    except AttributeError:
        bbox = font.getbbox(label)
        tw = bbox[2] - bbox[0]

    icon_zone_w = 13
    pad_right = 4
    tx = x + 21
    pill_w = int(21 + tw + pad_right)
    pill_h = 14

    draw.rounded_rectangle([x, y, x + pill_w, y + pill_h], radius=7, fill=colour)
    if icon_name:
        ibx = x + (icon_zone_w - 10) / 2
        iby = y + (pill_h - 10) / 2
        ibox = (ibx, iby, 10, 10)
        draw_icon(draw, icon_name, ibox, colour)
    ty = y + 2
    draw.text((tx, ty), label, fill=(255, 255, 255), font=font)
    return pill_w

def point_in_polygon(pt, poly):
    x, y = pt
    n = len(poly)
    inside = False
    p1x, p1y = poly[0]
    for i in range(n + 1):
        p2x, p2y = poly[i % n]
        if y > min(p1y, p2y):
            if y <= max(p1y, p2y):
                if x <= max(p1x, p2x):
                    if p1y != p2y:
                        xinters = (y - p1y) * (p2x - p1x) / (p2y - p1y) + p1x
                        if p1x == p2x or x <= xinters:
                            inside = not inside
        p1x, p1y = p2x, p2y
    return inside

def main():
    # Create image
    img = Image.new("RGB", (WIDTH, HEIGHT), (18, 42, 32))
    draw = ImageDraw.Draw(img)

    # Sheet rectangle: cream (250,246,233) inset by 14px with thin gold inner rule (176,141,44)
    sheet_box = (14, 14, WIDTH - 14, HEIGHT - 14)
    draw.rectangle(sheet_box, fill=(250, 246, 233))
    # Gold inner rule
    draw.rectangle((18, 18, WIDTH - 18, HEIGHT - 18), outline=(176, 141, 44), width=1)

    # Ink colour
    ink = (26, 26, 24)
    dark_green = (23, 63, 44)
    breaking_red = (179, 32, 42)

    # 1. Masthead
    # Microline at y=24
    font_micro = get_font(SANS_BOLD, 11)
    draw.text((26, 24), "THE WORLD IN ONE PAGE", fill=dark_green, font=font_micro)
    right_text = "33 STORIES · 6 CONTINENTS"
    try:
        rw = font_micro.getlength(right_text)
    except:
        rw = 150
    draw.text((998 - rw, 24), right_text, fill=dark_green, font=font_micro)

    # Title "The Morning Atlas" LiberationSerif-Bold 54 centred at y=52
    font_title = get_font(SERIF_BOLD, 54)
    title_str = "The Morning Atlas"
    try:
        tw = font_title.getlength(title_str)
    except:
        tw = 400
    draw.text(((WIDTH - tw) / 2, 44), title_str, fill=dark_green, font=font_title)

    # Date line at y=98: "Thursday 19 November 2026" flanked by hairlines
    font_date = get_font(SERIF_ITALIC, 17)
    date_str = "Thursday 19 November 2026"
    try:
        dw = font_date.getlength(date_str)
    except:
        dw = 200
    dx = (WIDTH - dw) / 2
    dy = 98
    draw.text((dx, dy - 2), date_str, fill=ink, font=font_date)
    draw.line([(26, dy + 7), (dx - 10, dy + 7)], fill=(176, 141, 44), width=1)
    draw.line([(dx + dw + 10, dy + 7), (998, dy + 7)], fill=(176, 141, 44), width=1)

    # 2. Breaking strip y=112..140
    draw.rectangle([26, 112, 998, 140], fill=breaking_red)
    # Darker box at left for BREAKING NEWS
    draw.rectangle([26, 112, 160, 140], fill=(140, 20, 28))
    font_bn_label = get_font(SANS_BOLD, 13)
    draw.text((36, 119), "BREAKING NEWS", fill=(255, 255, 255), font=font_bn_label)
    
    font_bn_text = get_font(SANS_BOLD, 12)
    bn_msg = "SHENZHEN SUMMIT ENDS — TRUMP, XI AND PUTIN RENOUNCE NUCLEAR WAR AT FIRST-EVER TRILATERAL"
    draw.text((172, 120), bn_msg, fill=(255, 255, 255), font=font_bn_text)

    # 3. LEADS: y=148..344, 3 columns (x: 26, 350, 674; width 314)
    lead_x_coords = [26, 350, 674]
    lead_w = 314
    for i, lead in enumerate(stories.LEADS):
        lx = lead_x_coords[i]
        ly = 148
        # Illustration panel height 66
        panel_box = [lx, ly, lx + lead_w, ly + 66]
        # Draw symbolic art based on index
        if i == 0: # Summit
            # sky gradient background
            draw.rectangle(panel_box, fill=(43, 77, 111))
            # simple skyline silhouette along bottom
            draw.rectangle([lx + 20, ly + 40, lx + 50, ly + 66], fill=(23, 40, 60))
            draw.rectangle([lx + 70, ly + 25, lx + 110, ly + 66], fill=(23, 40, 60))
            draw.rectangle([lx + 130, ly + 35, lx + 160, ly + 66], fill=(23, 40, 60))
            draw.rectangle([lx + 190, ly + 20, lx + 230, ly + 66], fill=(23, 40, 60))
            draw.rectangle([lx + 250, ly + 45, lx + 280, ly + 66], fill=(23, 40, 60))
            # sun disc
            draw.ellipse([lx + 220, ly + 10, lx + 250, ly + 40], fill=(240, 200, 100))
            # flag poles & flags
            for fx in [lx + 90, lx + 150, lx + 210]:
                draw.line([(fx, ly + 15), (fx, ly + 45)], fill=(255, 255, 255), width=2)
                draw.polygon([(fx, ly + 15), (fx + 12, ly + 20), (fx, ly + 25)], fill=(179, 32, 42) if fx != lx+150 else (43, 77, 111))
        elif i == 1: # Court
            draw.rectangle(panel_box, fill=(90, 95, 100))
            # pediment triangle & columns
            draw.polygon([(lx + lead_w/2, ly + 10), (lx + 30, ly + 30), (lx + lead_w - 30, ly + 30)], fill=(220, 220, 220))
            for cx in range(int(lx + 50), int(lx + lead_w - 40), 35):
                draw.rectangle([cx, ly + 30, cx + 12, ly + 60], fill=(240, 240, 240))
            # scales glyph in pediment
            ibox = (lx + lead_w/2 - 10, ly + 12, 20, 15)
            draw_icon(draw, "scales", ibox, (90, 95, 100))
        else: # IPO
            draw.rectangle(panel_box, fill=(20, 30, 25))
            # rising polyline chart in gold with arrowhead + 3 bars + bell silhouette
            gold = (210, 170, 60)
            draw.line([(lx + 40, ly + 50), (lx + 90, ly + 40), (lx + 140, ly + 25), (lx + 200, ly + 15)], fill=gold, width=2)
            draw.polygon([(lx + 200, ly + 15), (lx + 192, ly + 11), (lx + 192, ly + 19)], fill=gold)
            # rising bars
            draw.rectangle([lx + 220, ly + 35, lx + 232, ly + 60], fill=(50, 80, 70))
            draw.rectangle([lx + 242, ly + 25, lx + 254, ly + 60], fill=(50, 80, 70))
            draw.rectangle([lx + 264, ly + 15, lx + 276, ly + 60], fill=(50, 80, 70))

        # Dark ribbon strip 14 high along panel bottom
        ribbon_y = ly + 66 - 14
        draw.rectangle([lx, ribbon_y, lx + lead_w, ly + 66], fill=(20, 20, 20))
        font_ribbon = get_font(SANS_BOLD, 9.5)
        draw.text((lx + 8, ribbon_y + 1), lead["ribbon"], fill=(255, 255, 255), font=font_ribbon)

        # Number disc overlapping top-left corner
        col_rgb = stories.REGION_COLOURS.get(lead["label"].split("·")[0].strip(), (50, 50, 50))
        disc_d = 20
        draw.ellipse([lx - 4, ly - 4, lx - 4 + disc_d, ly - 4 + disc_d], fill=col_rgb)
        font_disc = get_font(SANS_BOLD, 10)
        draw.text((lx + 1, ly - 2), str(lead["n"]), fill=(255, 255, 255), font=font_disc)

        # Headline LiberationSerif-Bold 18 wrapped to at most 2 lines
        head_y = ly + 72
        font_head, head_lines = fit_text(lead["head"], SERIF_BOLD, 18, lead_w, max_lines=2)
        curr_y = head_y
        for hl in head_lines:
            draw.text((lx, curr_y), hl, fill=ink, font=font_head)
            try:
                curr_y += font_head.size + 2
            except:
                curr_y += 20

        # Banner pill
        pill_y = curr_y + 4
        draw_pill(draw, lx, pill_y, lead["label"], col_rgb, lead["icon"])

        # Description sans 12 wrapped to at most 3 lines
        desc_y = pill_y + 22
        font_desc = get_font(SANS_REG, 12)
        desc_lines = wrap(lead["desc"], font_desc, lead_w)
        curr_y = desc_y
        for dl in desc_lines[:3]:
            draw.text((lx, curr_y), dl, fill=ink, font=font_desc)
            curr_y += 14

    # Divider line under leads
    draw.line([(26, 348), (998, 348)], fill=(176, 141, 44), width=1)

    # 4. TILES: y=352..584, two rows of five
    # Column width 188, gutter 8. x starts 26, 222, 418, 614, 810
    tile_xs = [26, 222, 418, 614, 810]
    tile_w = 188
    tile_h = 110
    for idx, tile in enumerate(stories.TILES):
        row = idx // 5
        col = idx % 5
        tx = tile_xs[col]
        ty = 354 + row * 114

        col_rgb = stories.REGION_COLOURS.get(tile["label"].split("·")[0].strip(), (50, 50, 50))

        # Top row: number disc (d=16), icon medallion (26x26 rounded sq), chip right-aligned
        disc_d = 16
        draw.ellipse([tx, ty, tx + disc_d, ty + disc_d], fill=col_rgb)
        font_tdisc = get_font(SANS_BOLD, 9)
        draw.text((tx + 4, ty + 1), str(tile["n"]), fill=(255, 255, 255), font=font_tdisc)

        # Icon medallion
        med_x = tx + 20
        med_y = ty - 2
        draw.rounded_rectangle([med_x, med_y, med_x + 24, med_y + 24], radius=6, fill=col_rgb)
        draw_icon(draw, tile["icon"], (med_x, med_y, 24, 24), col_rgb)

        # Chip right-aligned if present
        if tile["chip"]:
            font_chip = get_font(SERIF_BOLD, 13)
            try:
                cw = font_chip.getlength(tile["chip"])
            except:
                cw = 40
            draw.text((tx + tile_w - cw, ty), tile["chip"], fill=dark_green, font=font_chip)

        # Headline sans bold 14 wrapped to at most 2 lines
        head_y = ty + 28
        font_thead, thead_lines = fit_text(tile["head"], SANS_BOLD, 13, tile_w, max_lines=2)
        curr_y = head_y
        for thl in thead_lines:
            draw.text((tx, curr_y), thl, fill=ink, font=font_thead)
            curr_y += 15

        # Banner pill height 15, label 9
        pill_y = curr_y + 2
        # Draw mini pill for tile or regular pill adjusted
        draw_pill(draw, tx, pill_y, tile["label"], col_rgb, "") # tile has icon medallion already

        # Description sans 10.5 wrapped to at most 3 lines (capped with ellipsis if needed)
        desc_y = pill_y + 19
        font_tdesc = get_font(SANS_REG, 10.5)
        tdesc_lines = wrap_with_ellipsis(tile["desc"], font_tdesc, tile_w, max_lines=3)
        curr_y = desc_y
        for tdl in tdesc_lines:
            draw.text((tx, curr_y), tdl, fill=ink, font=font_tdesc)
            curr_y += 12

    # Divider line under tiles
    draw.line([(26, 586), (998, 586)], fill=(176, 141, 44), width=1)

    # 5. MAP BAND: y=592..752
    font_sec = get_font(SANS_BOLD, 12.5)
    draw.text((26, 592), "WHERE IT HAPPENED", fill=dark_green, font=font_sec)
    draw.line([(26, 608), (636, 608)], fill=(176, 141, 44), width=1)

    # Map area x 26..636, y 616..748
    mx1, my1, mx2, my2 = 26, 616, 636, 748
    mw = mx2 - mx1
    mh = my2 - my1
    draw.rectangle([mx1, my1, mx2, my2], fill=(242, 238, 226))

    # Simplified world map continent polygons (lon, lat)
    continents = [
        # North America
        [(-165, 70), (-130, 70), (-60, 60), (-50, 50), (-80, 25), (-115, 30), (-125, 50), (-165, 60)],
        # South America
        [(-80, 12), (-35, -5), (-40, -50), (-75, -50), (-80, -10)],
        # Africa
        [(-15, 35), (40, 35), (50, 12), (35, -35), (10, -35), (-5, 10)],
        # Eurasia
        [(-10, 36), (40, 70), (140, 70), (180, 65), (140, 25), (100, 10), (40, 40), (20, 36)],
        # Australia
        [(112, -11), (154, -11), (154, -39), (112, -39)],
    ]
    # Small islands/ellipses: Britain, Japan, Indonesia, Madagascar, New Zealand
    islands = [
        (-3, 53, 6, 8),     # Britain
        (138, 36, 6, 8),    # Japan
        (110, -2, 18, 6),   # Indonesia
        (47, -20, 6, 12),   # Madagascar
        (174, -40, 6, 10),  # New Zealand
    ]

    def lonlat_to_xy(lon, lat):
        # equirectangular lon -170..190, lat 84..-58
        x = mx1 + (lon - (-170)) / (190 - (-170)) * mw
        y = my1 + (84 - lat) / (84 - (-58)) * mh
        return x, y

    def inside_map(lon, lat):
        pt = (lon, lat)
        for poly in continents:
            if point_in_polygon(pt, poly):
                return True
        for (ilx, ily, iw, ih) in islands:
            ix, iy = lonlat_to_xy(ilx, ily)
            px, py = lonlat_to_xy(lon, lat)
            if abs(px - ix) <= iw and abs(py - iy) <= ih:
                return True
        return False

    # Draw dotted land map
    grid_step = 4.5
    gx = mx1 + 2
    while gx < mx2:
        gy = my1 + 2
        while gy < my2:
            # inverse transform to lon, lat
            lon = (gx - mx1) / mw * (190 - (-170)) + (-170)
            lat = 84 - (gy - my1) / mh * (84 - (-58))
            if inside_map(lon, lat):
                draw.ellipse([gx - 0.8, gy - 0.8, gx + 0.8, gy + 0.8], fill=(120, 132, 118))
            gy += grid_step
        gx += grid_step

    # Draw 13 main stories' pins on map
    all_main_stories = stories.LEADS + stories.TILES
    font_pin = get_font(SANS_BOLD, 8.5)
    for s in all_main_stories:
        if s.get("lat") is not None and s.get("lon") is not None:
            px, py = lonlat_to_xy(s["lon"], s["lat"])
            col = stories.REGION_COLOURS.get(s["label"].split("·")[0].strip(), (50, 50, 50))
            pin_d = 15
            draw.ellipse([px - pin_d/2, py - pin_d/2, px + pin_d/2, py + pin_d/2], fill=col)
            # number text centred
            n_str = str(s["n"])
            try:
                nw = font_pin.getlength(n_str)
            except:
                nw = 6
            draw.text((px - nw/2, py - 5), n_str, fill=(255, 255, 255), font=font_pin)

    # Draw briefs' locations as small 3px dots
    for b in stories.BRIEFS:
        if b.get("lat") is not None and b.get("lon") is not None:
            px, py = lonlat_to_xy(b["lon"], b["lat"])
            col = stories.REGION_COLOURS.get(b["label"].split("·")[0].strip(), (50, 50, 50))
            draw.ellipse([px - 1.5, py - 1.5, px + 1.5, py + 1.5], fill=col)

    # Right side x 652..998: "THE DAY IN NUMBERS" box
    nx1, ny1, nx2, ny2 = 652, 616, 998, 748
    draw.rectangle([nx1, ny1, nx2, ny2], fill=(243, 235, 214), outline=dark_green, width=1)
    draw.text((nx1 + 10, ny1 + 6), "THE DAY IN NUMBERS", fill=dark_green, font=font_sec)
    draw.line([(nx1 + 10, ny1 + 22), (nx2 - 10, ny1 + 22)], fill=(176, 141, 44), width=1)

    # Strict grid: 2 columns x 3 rows of fixed cells inside the box
    col_w_num = (nx2 - nx1 - 24) / 2
    row_h_num = 35
    font_num_val = get_font(SERIF_BOLD, 17)
    font_num_cap = get_font(SANS_REG, 8.5)

    for i, num in enumerate(stories.NUMBERS):
        c = i % 2
        r = i // 2
        cell_x = nx1 + 10 + c * (col_w_num + 12)
        cell_y = (ny1 + 26) + r * row_h_num
        cell_bottom = cell_y + row_h_num

        draw.text((cell_x, cell_y), num["value"], fill=dark_green, font=font_num_val)
        cap_lines = wrap(num["caption"], font_num_cap, col_w_num)
        cy = cell_y + 17
        for cl in cap_lines[:2]:
            if cy + 10 <= cell_bottom:
                draw.text((cell_x, cy), cl, fill=ink, font=font_num_cap)
            cy += 11

    # Divider under map band
    draw.line([(26, 754), (998, 754)], fill=(176, 141, 44), width=1)

    # 6. BRIEFS: heading at y=760
    draw.text((26, 760), "ALSO ON THURSDAY 19 NOVEMBER", fill=dark_green, font=font_sec)
    draw.line([(26, 776), (998, 776)], fill=(176, 141, 44), width=1)

    # Rows y=782..982: two columns (x 26..500 and 524..998), 10 rows each, row height 20
    brief_cols = [
        (26, 500, stories.BRIEFS[:10]),
        (524, 998, stories.BRIEFS[10:])
    ]
    brief_cols = [
        (26, 500, stories.BRIEFS[:10]),
        (524, 998, stories.BRIEFS[10:])
    ]
    font_brief = get_font(SANS_REG, 10)
    font_brief_bold = get_font(SANS_BOLD, 10)

    for bx1, bx2, b_list in brief_cols:
        for idx, brief in enumerate(b_list):
            by = 782 + idx * 20
            col_rgb = stories.REGION_COLOURS.get(brief["label"].split("·")[0].strip(), (50, 50, 50))

            # Draw number disc first
            disc_d = 14
            draw.ellipse([bx1, by + 2, bx1 + disc_d, by + 2 + disc_d], fill=col_rgb)
            font_bdisc = get_font(SANS_BOLD, 8)
            draw.text((bx1 + 3, by + 3), str(brief["n"]), fill=(255, 255, 255), font=font_bdisc)

            # Draw mini pill starting a clear 4 px after the disc
            pill_x = bx1 + disc_d + 4
            pill_w = draw_mini_pill(draw, pill_x, by + 2, brief["label"], col_rgb, brief["icon"])

            # Brief text starting after pill + 6px padding
            text_x = pill_x + pill_w + 6
            max_w = bx2 - text_x

            prefix = brief["prefix"]
            body = brief["text"]

            # Wrap text to 2 lines max with ellipsis on line 2 if needed
            words = body.split()
            line1_words = []
            i = 0
            while i < len(words):
                test_words = line1_words + [words[i]]
                try:
                    w = font_brief_bold.getlength(prefix + " ") + font_brief.getlength(" ".join(test_words))
                except AttributeError:
                    bbox_b = font_brief_bold.getbbox(prefix + " ")
                    bbox_r = font_brief.getbbox(" ".join(test_words))
                    w = (bbox_b[2] - bbox_b[0]) + (bbox_r[2] - bbox_r[0])
                if w <= max_w or not line1_words:
                    line1_words.append(words[i])
                    i += 1
                else:
                    break

            rem_words = words[i:]
            if not rem_words:
                lines = [" ".join([prefix] + line1_words)]
            else:
                line2_words = []
                i2 = 0
                while i2 < len(rem_words):
                    test_words = line2_words + [rem_words[i2]]
                    test_str = " ".join(test_words) + "…"
                    try:
                        w = font_brief.getlength(test_str)
                    except AttributeError:
                        bbox = font_brief.getbbox(test_str)
                        w = bbox[2] - bbox[0]
                    if w <= max_w or not line2_words:
                        line2_words.append(rem_words[i2])
                        i2 += 1
                    else:
                        break
                if i2 < len(rem_words):
                    line2_str = " ".join(line2_words) + "…"
                else:
                    line2_str = " ".join(line2_words)
                lines = [" ".join([prefix] + line1_words), line2_str]

            curr_by = by + 1
            line_height = 9.8
            for l_idx, line in enumerate(lines):
                ly = curr_by + l_idx * line_height
                if l_idx == 0:
                    rest = line[len(prefix):].lstrip()
                    draw.text((text_x, ly), prefix, fill=dark_green, font=font_brief_bold)
                    try:
                        pw = font_brief_bold.getlength(prefix + " ")
                    except:
                        pw = font_brief.getlength(prefix + " ")
                    draw.text((text_x + pw, ly), rest, fill=ink, font=font_brief)
                else:
                    draw.text((text_x, ly), line, fill=ink, font=font_brief)

    # Footer at y=990
    font_footer = get_font(SANS_REG, 9.5)
    footer_text = "Sources: Reuters, AP, AFP, BBC, WSJ, CNN, Le Monde, WHO, NASA, IEA. All illustrations are original drawings. Every story happened or was first reported on Thursday 19 November 2026."
    try:
        fw = font_footer.getlength(footer_text)
    except:
        fw = 800
    draw.text(((WIDTH - fw) / 2, 990), footer_text, fill=(100, 100, 100), font=font_footer)

    # Save output entry.png next to script
    script_dir = os.path.dirname(os.path.abspath(__file__))
    out_path = os.path.join(script_dir, "entry.png")
    img.save(out_path)
    print(f"Successfully generated {out_path}")

if __name__ == "__main__":
    main()
