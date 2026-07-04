#!/usr/bin/env python3
"""Generate EVOLION Open Graph share preview from A9.png + header logo."""

from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "assets/home/A9.png"
LOGO = ROOT / "assets/home/screenshot-743-1.png"
OUT = ROOT / "assets/og-share.png"
FONTS = ROOT / "assets/fonts"

OG_W, OG_H = 1200, 630
GOLD = (169, 130, 75)  # #A9824B
WHITE = (255, 255, 255)

# Left black zone in A9.png (2048px wide) — do not alter base layout.
BASE_LEFT_EDGE = 740

BRAND_TEXT = "E V O L I O N"
TAGLINE_TEXT = "GENERATIONAL HEALTH"


def scale_base_to_og(base: Image.Image) -> Image.Image:
    """Fit A9.png to 1200x630, preserving its composition."""
    src_w, src_h = base.size
    scale = OG_W / src_w
    new_h = int(src_h * scale)
    resized = base.resize((OG_W, new_h), Image.Resampling.LANCZOS)
    top = (new_h - OG_H) // 2
    return resized.crop((0, top, OG_W, top + OG_H))


def text_size(draw: ImageDraw.ImageDraw, text: str, font: ImageFont.FreeTypeFont) -> tuple[int, int]:
    bbox = draw.textbbox((0, 0), text, font=font)
    return bbox[2] - bbox[0], bbox[3] - bbox[1]


def fit_font(
    draw: ImageDraw.ImageDraw,
    text: str,
    font_path: str,
    start_size: int,
    max_width: int,
    min_size: int = 14,
) -> ImageFont.FreeTypeFont:
    size = start_size
    while size >= min_size:
        font = ImageFont.truetype(font_path, size)
        width, _ = text_size(draw, text, font)
        if width <= max_width:
            return font
        size -= 1
    return ImageFont.truetype(font_path, min_size)


def draw_centered(
    draw: ImageDraw.ImageDraw,
    text: str,
    font: ImageFont.FreeTypeFont,
    center_x: int,
    top_y: int,
    fill: tuple[int, int, int],
) -> int:
    """Draw text centered on center_x; return bottom y."""
    bbox = draw.textbbox((0, 0), text, font=font)
    text_w = bbox[2] - bbox[0]
    text_h = bbox[3] - bbox[1]
    x = center_x - text_w // 2 - bbox[0]
    y = top_y - bbox[1]
    draw.text((x, y), text, fill=fill, font=font)
    return top_y + text_h


def main() -> None:
    canvas = scale_base_to_og(Image.open(BASE).convert("RGBA"))
    logo = Image.open(LOGO).convert("RGBA")
    draw = ImageDraw.Draw(canvas)

    left_w = int(BASE_LEFT_EDGE * (OG_W / 2048))
    center_x = left_w // 2
    max_text_w = int(left_w * 0.88)
    font_path = str(FONTS / "Poppins-Medium.ttf")

    poppins_lg = fit_font(draw, BRAND_TEXT, font_path, start_size=38, max_width=max_text_w, min_size=24)
    poppins_sm = fit_font(draw, TAGLINE_TEXT, font_path, start_size=14, max_width=max_text_w, min_size=10)

    logo_target_h = 110
    logo_scale = logo_target_h / logo.height
    logo_size = (int(logo.width * logo_scale), logo_target_h)
    logo_resized = logo.resize(logo_size, Image.Resampling.LANCZOS)

    _, brand_h = text_size(draw, BRAND_TEXT, poppins_lg)
    _, tag_h = text_size(draw, TAGLINE_TEXT, poppins_sm)

    gap_logo_brand = 22
    gap_brand_tag = 14
    block_h = logo_size[1] + gap_logo_brand + brand_h + gap_brand_tag + tag_h
    cursor_y = (OG_H - block_h) // 2

    logo_x = center_x - logo_size[0] // 2
    canvas.paste(logo_resized, (logo_x, cursor_y), logo_resized)
    cursor_y += logo_size[1] + gap_logo_brand

    cursor_y = draw_centered(draw, BRAND_TEXT, poppins_lg, center_x, cursor_y, WHITE)
    cursor_y += gap_brand_tag

    draw_centered(draw, TAGLINE_TEXT, poppins_sm, center_x, cursor_y, GOLD)

    OUT.parent.mkdir(parents=True, exist_ok=True)
    canvas.convert("RGB").save(OUT, "PNG", optimize=True)
    print(f"Saved {OUT} ({OG_W}x{OG_H}) from {BASE.name}")


if __name__ == "__main__":
    main()
