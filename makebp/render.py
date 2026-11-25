"""Render a scenario tree to Mermaid and a Make-style PNG."""

from __future__ import annotations

import textwrap
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

from makebp.allowlist import MODULES

FONT = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
FONT_BOLD = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"

APP_COLORS = {
    "google-email": "#EA4335",
    "google-sheets": "#0F9D58",
    "google-drive": "#4285F4",
    "google-docs": "#4285F4",
    "google-calendar": "#1A73E8",
    "google-forms": "#673AB7",
    "openai-gpt-3": "#10A37F",
    "anthropic-claude": "#C4A484",
    "gemini-ai": "#1A73E8",
    "perplexity-ai": "#20808D",
    "ai-local-agent": "#6D28D9",
    "slack": "#4A154B",
    "hubspotcrm": "#FF7A59",
    "twilio": "#F22F46",
    "airtable": "#E8B400",
    "notion": "#191919",
    "http": "#334155",
    "gateway": "#7C3AED",
    "builtin": "#D97706",
    "util": "#0284C7",
    "json": "#0369A1",
    "rss": "#EA580C",
    "linkedin": "#0A66C2",
    "facebook-pages": "#1877F2",
    "twitter": "#111827",
    "instagram-business": "#DB2777",
    "typeform": "#111827",
    "zendesk": "#03363D",
    "stripe": "#635BFF",
    "apify": "#6B9F00",
    "regexp": "#475569",
    "csv": "#475569",
    "email": "#EA4335",
    "scenario-service": "#64748B",
    "markdown": "#334155",
    "discord": "#5865F2",
    "telegram": "#229ED9",
    "dropbox": "#0061FF",
}

CELL_W = 168
CELL_H = 132
MARGIN_X = 36
MARGIN_Y = 28
HEADER = 78
FOOTER = 36


def _color(module: str) -> str:
    prefix = module.split(":", 1)[0]
    return APP_COLORS.get(prefix, "#475569")


def _initials(module: str) -> str:
    app = MODULES[module]["app"]
    parts = [part for part in app.replace("(", " ").replace(")", " ").split() if part[0].isalpha()]
    if len(parts) == 1:
        return parts[0][:2].upper()
    return (parts[0][0] + parts[1][0]).upper()


def mermaid(nodes: list[dict]) -> str:
    lines = ["flowchart LR"]

    def add_node(node: dict) -> None:
        label = f"{node['id']} · {node['name']}".replace('"', "'")
        if node["module"] == "builtin:BasicRouter":
            lines.append(f'  {node["key"]}{{"{label}"}}')
        else:
            lines.append(f'  {node["key"]}(("{label}"))')

    def link(source: str, target: str, text: str | None = None) -> None:
        if text:
            safe = text.replace('"', "'")
            lines.append(f'  {source} -->|"{safe}"| {target}')
        else:
            lines.append(f"  {source} --> {target}")

    def walk(items: list[dict], previous: str | None = None) -> None:
        for node in items:
            add_node(node)
            if previous:
                link(previous, node["key"])
            handler = node.get("onerror_nodes") or []
            if handler:
                link(node["key"], handler[0]["key"], "error")
                cursor = None
                for handler_node in handler:
                    add_node(handler_node)
                    if cursor:
                        link(cursor, handler_node["key"])
                    cursor = handler_node["key"]
            routes = node.get("routes") or []
            if routes:
                for branch in routes:
                    walk(branch["steps"], None)
                    link(node["key"], branch["steps"][0]["key"], branch["name"])
                previous = None
            else:
                previous = node["key"]

    walk(nodes, None)
    return "\n".join(lines) + "\n"


def _place(nodes: list[dict], col: int, row: int, placed: dict) -> tuple[int, int]:
    """Place a sequence. Returns (column after the sequence, row below the subtree)."""
    cursor = col
    bottom = row + 1
    for node in nodes:
        placed[node["key"]] = (cursor, row, node)
        node_bottom = row + 1
        if node.get("onerror_nodes"):
            handler_col = cursor
            for handler in node["onerror_nodes"]:
                placed[handler["key"]] = (handler_col, row + 1, handler)
                handler_col += 1
            node_bottom = row + 2
        if node.get("routes"):
            route_row = row
            widest = 0
            for branch in node["routes"]:
                end_col, end_row = _place(branch["steps"], cursor + 1, route_row, placed)
                widest = max(widest, end_col - (cursor + 1))
                route_row = end_row
            node_bottom = max(node_bottom, route_row)
            cursor = cursor + 1 + widest
        else:
            cursor += 1
        bottom = max(bottom, node_bottom)
    return cursor, bottom


def render_png(title: str, nodes: list[dict], path: Path) -> None:
    placed: dict[str, tuple[int, int, dict]] = {}
    _place(nodes, 0, 0, placed)
    if not placed:
        raise ValueError("nothing to draw")
    max_col = max(col for col, _, _ in placed.values())
    max_row = max(row for _, row, _ in placed.values())
    width = MARGIN_X * 2 + (max_col + 1) * CELL_W
    height = HEADER + FOOTER + MARGIN_Y * 2 + (max_row + 1) * CELL_H
    image = Image.new("RGB", (width, height), "#F6F7FB")
    draw = ImageDraw.Draw(image)
    title_font = ImageFont.truetype(FONT_BOLD, 22)
    small = ImageFont.truetype(FONT, 13)
    tiny = ImageFont.truetype(FONT, 12)
    bold = ImageFont.truetype(FONT_BOLD, 15)
    draw.rectangle((0, 0, width, HEADER), fill="#1E1B4B")
    draw.text((MARGIN_X, 18), _fit(title, title_font, width - MARGIN_X * 2), fill="white", font=title_font)
    draw.text((MARGIN_X, 48), "Make.com scenario  ·  portfolio demo  ·  not client work", fill="#C7D2FE", font=small)

    centers = {}
    for key, (col, row, node) in placed.items():
        cx = MARGIN_X + col * CELL_W + CELL_W // 2
        cy = HEADER + MARGIN_Y + row * CELL_H + 46
        centers[key] = (cx, cy, node)

    def edge(src: str, dst: str, color: str = "#94A3B8") -> None:
        x1, y1, _ = centers[src]
        x2, y2, _ = centers[dst]
        r = 34
        # Start at the circle edge closest to the target.
        if abs(x2 - x1) >= abs(y2 - y1):
            start = (x1 + r, y1) if x2 >= x1 else (x1 - r, y1)
            end = (x2 - r, y2) if x2 >= x1 else (x2 + r, y2)
        else:
            start = (x1, y1 + r) if y2 >= y1 else (x1, y1 - r)
            end = (x2, y2 - r) if y2 >= y1 else (x2, y2 + r)
        draw.line((start, end), fill=color, width=3)
        # Arrow head
        if end[0] != start[0] or end[1] != start[1]:
            ax, ay = end
            if abs(end[0] - start[0]) >= abs(end[1] - start[1]):
                direction = 1 if end[0] > start[0] else -1
                head = [(ax, ay), (ax - 10 * direction, ay - 6), (ax - 10 * direction, ay + 6)]
            else:
                direction = 1 if end[1] > start[1] else -1
                head = [(ax, ay), (ax - 6, ay - 10 * direction), (ax + 6, ay - 10 * direction)]
            draw.polygon(head, fill=color)

    def walk_edges(items: list[dict], previous: str | None = None) -> None:
        for node in items:
            if previous:
                edge(previous, node["key"])
            handler = node.get("onerror_nodes") or []
            if handler:
                edge(node["key"], handler[0]["key"], "#DC2626")
                cursor = handler[0]["key"]
                for nxt in handler[1:]:
                    edge(cursor, nxt["key"], "#DC2626")
                    cursor = nxt["key"]
            if node.get("routes"):
                for branch in node["routes"]:
                    edge(node["key"], branch["steps"][0]["key"], "#D97706")
                    walk_edges(branch["steps"], None)
                previous = None
            else:
                previous = node["key"]

    walk_edges(nodes)

    for key, (cx, cy, node) in centers.items():
        color = _color(node["module"])
        draw.ellipse((cx - 36, cy - 32, cx + 36, cy + 40), fill="#E2E8F0")
        draw.ellipse((cx - 34, cy - 34, cx + 34, cy + 34), fill=color)
        mark = _initials(node["module"])
        bbox = draw.textbbox((0, 0), mark, font=bold)
        draw.text((cx - (bbox[2] - bbox[0]) / 2, cy - 10), mark, fill="white", font=bold)
        label = textwrap.wrap(node["name"], width=18)[:3]
        text_y = cy + 40
        for line in label:
            bbox = draw.textbbox((0, 0), line, font=tiny)
            draw.text((cx - (bbox[2] - bbox[0]) / 2, text_y), line, fill="#1F2937", font=tiny)
            text_y += 14

    draw.text(
        (MARGIN_X, height - 26),
        "mustafaautomation  ·  *.quvantic.com  ·  import the blueprint, then connect your own accounts",
        fill="#64748B",
        font=tiny,
    )
    path.parent.mkdir(parents=True, exist_ok=True)
    image.save(path, format="PNG", optimize=True)


def _fit(text: str, font: ImageFont.FreeTypeFont, limit: int) -> str:
    if font.getlength(text) <= limit:
        return text
    trimmed = text
    while trimmed and font.getlength(trimmed + "…") > limit:
        trimmed = trimmed[:-1]
    return trimmed + "…"
