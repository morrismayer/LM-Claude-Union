"""Streamlit app for visualizing upholstered furniture finishes.

Run:
    streamlit run examples/upholstered_furniture_visualizer.py
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Tuple

import streamlit as st
from PIL import Image, ImageDraw, ImageEnhance, ImageFilter


@dataclass
class VisualizerConfig:
    width: int = 1280
    height: int = 760
    body_color: str = "#7b5b43"
    leg_color: str = "#2f2a28"
    accent_color: str = "#d5bfa7"
    tufting: bool = True
    piping: bool = True
    seat_depth: int = 50
    arm_style: str = "Rounded"
    brightness: float = 1.0
    contrast: float = 1.0


def hex_to_rgb(hex_color: str) -> Tuple[int, int, int]:
    hex_color = hex_color.strip("#")
    return tuple(int(hex_color[i : i + 2], 16) for i in (0, 2, 4))


def draw_fabric_noise(img: Image.Image, color: Tuple[int, int, int]) -> Image.Image:
    noise = Image.effect_noise(img.size, 22).convert("L")
    grain = Image.new("RGB", img.size, color)
    grain.putalpha(noise)
    base = Image.new("RGB", img.size, tuple(max(0, c - 20) for c in color))
    merged = Image.alpha_composite(base.convert("RGBA"), grain)
    return merged.convert("RGB")


def render_sofa(cfg: VisualizerConfig) -> Image.Image:
    canvas = Image.new("RGB", (cfg.width, cfg.height), "#f4f1ed")
    draw = ImageDraw.Draw(canvas)

    # Background wall and floor
    draw.rectangle((0, 0, cfg.width, int(cfg.height * 0.62)), fill="#e8e2db")
    draw.rectangle((0, int(cfg.height * 0.62), cfg.width, cfg.height), fill="#cdb9a6")

    body_rgb = hex_to_rgb(cfg.body_color)
    accent_rgb = hex_to_rgb(cfg.accent_color)
    leg_rgb = hex_to_rgb(cfg.leg_color)

    sofa_w = int(cfg.width * 0.62)
    sofa_h = int(cfg.height * 0.35)
    x0 = (cfg.width - sofa_w) // 2
    y0 = int(cfg.height * 0.28)

    body = Image.new("RGB", (sofa_w, sofa_h), body_rgb)
    body = draw_fabric_noise(body, body_rgb)

    if cfg.arm_style == "Square":
        arm_offset = 0
    elif cfg.arm_style == "Flared":
        arm_offset = 25
    else:
        arm_offset = 12

    canvas.paste(body, (x0, y0))

    # Backrest and seat zones
    draw.rounded_rectangle((x0, y0, x0 + sofa_w, y0 + int(sofa_h * 0.45)), radius=38, outline=accent_rgb, width=3)
    seat_top = y0 + int(sofa_h * (1 - cfg.seat_depth / 100))
    draw.rounded_rectangle((x0, seat_top, x0 + sofa_w, y0 + sofa_h), radius=22, outline=accent_rgb, width=3)

    # Arms
    arm_w = int(sofa_w * 0.13)
    arm_h = int(sofa_h * 0.8)
    left_arm = (x0 - arm_offset, y0 + 12, x0 + arm_w, y0 + arm_h)
    right_arm = (x0 + sofa_w - arm_w, y0 + 12, x0 + sofa_w + arm_offset, y0 + arm_h)
    draw.rounded_rectangle(left_arm, radius=25, fill=body_rgb, outline=accent_rgb, width=3)
    draw.rounded_rectangle(right_arm, radius=25, fill=body_rgb, outline=accent_rgb, width=3)

    # Legs
    leg_y = y0 + sofa_h + 10
    for lx in [x0 + 45, x0 + sofa_w - 85, x0 + sofa_w // 2 - 20, x0 + sofa_w // 2 + 40]:
        draw.rounded_rectangle((lx, leg_y, lx + 20, leg_y + 70), radius=5, fill=leg_rgb)

    # Tufting details
    if cfg.tufting:
        cols = 8
        rows = 3
        for r in range(rows):
            for c in range(cols):
                cx = x0 + 55 + c * ((sofa_w - 110) // (cols - 1))
                cy = y0 + 45 + r * 45
                draw.ellipse((cx - 5, cy - 5, cx + 5, cy + 5), fill=tuple(max(0, ch - 40) for ch in body_rgb))

    # Piping
    if cfg.piping:
        draw.rounded_rectangle((x0 + 6, y0 + 6, x0 + sofa_w - 6, y0 + sofa_h - 6), radius=32, outline=accent_rgb, width=4)

    # Pillow accents
    pillows = [
        (x0 + 100, seat_top - 35, x0 + 220, seat_top + 65, "#f2efe9"),
        (x0 + sofa_w - 230, seat_top - 40, x0 + sofa_w - 100, seat_top + 60, "#b08a69"),
    ]
    for px0, py0, px1, py1, color in pillows:
        draw.rounded_rectangle((px0, py0, px1, py1), radius=25, fill=color)

    canvas = ImageEnhance.Brightness(canvas).enhance(cfg.brightness)
    canvas = ImageEnhance.Contrast(canvas).enhance(cfg.contrast)
    canvas = canvas.filter(ImageFilter.SMOOTH_MORE)
    return canvas


def main() -> None:
    st.set_page_config(page_title="Upholstered Furniture Visualizer", layout="wide")
    st.title("🛋️ Upholstered Furniture Visualizer")
    st.caption("Preview upholstery colors, arm styles, and construction details in a fast concept render.")

    with st.sidebar:
        st.header("Design Controls")
        body_color = st.color_picker("Body Fabric", "#7b5b43")
        accent_color = st.color_picker("Piping/Trim", "#d5bfa7")
        leg_color = st.color_picker("Leg Color", "#2f2a28")
        arm_style = st.selectbox("Arm Style", ["Rounded", "Square", "Flared"])
        seat_depth = st.slider("Seat Depth", min_value=35, max_value=70, value=50)
        tufting = st.toggle("Button Tufting", value=True)
        piping = st.toggle("Contrast Piping", value=True)
        brightness = st.slider("Brightness", min_value=0.7, max_value=1.3, value=1.0, step=0.05)
        contrast = st.slider("Contrast", min_value=0.7, max_value=1.3, value=1.0, step=0.05)

    cfg = VisualizerConfig(
        body_color=body_color,
        accent_color=accent_color,
        leg_color=leg_color,
        arm_style=arm_style,
        seat_depth=seat_depth,
        tufting=tufting,
        piping=piping,
        brightness=brightness,
        contrast=contrast,
    )

    result = render_sofa(cfg)
    st.image(result, caption="Rendered concept view", use_container_width=True)

    import io

    buf = io.BytesIO()
    result.save(buf, format="PNG")
    st.download_button(
        "Download Current Render",
        data=buf.getvalue(),
        file_name="upholstered_furniture_concept.png",
        mime="image/png",
    )


if __name__ == "__main__":
    main()
