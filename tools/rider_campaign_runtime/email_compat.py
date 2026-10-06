from __future__ import annotations

from html import escape
import re


TABLE_TAG_RE = re.compile(r"</?table\b[^>]*>|</?td\b[^>]*>", re.IGNORECASE | re.DOTALL)
STYLE_RE = re.compile(r'\bstyle=(?P<quote>["\'])(?P<style>.*?)(?P=quote)', re.IGNORECASE | re.DOTALL)
BACKGROUND_URL_RE = re.compile(
    r"background-image\s*:\s*url\((?P<quote>['\"]?)(?P<url>[^)'\"]+)(?P=quote)\)",
    re.IGNORECASE,
)


def add_bulletproof_backgrounds(html: str) -> tuple[str, int]:
    """Add Gmail-compatible attributes and Outlook VML to cover-style table backgrounds."""
    count = 0
    search_from = 0
    while True:
        target = _next_background_table(html, search_from)
        if target is None:
            return html, count
        table_start, table_open_end, table_close_start, table_close_end, tag, style, url = target
        segment = html[table_start:table_close_end]
        if 'data-onbrand-background="true"' in segment:
            search_from = table_close_end
            continue

        cell = _first_top_level_cell(html, table_open_end, table_close_start)
        if cell is None:
            search_from = table_close_end
            continue
        cell_open_end, cell_close_start = cell

        width = _content_width(tag, style)
        color = _style_value(style, "background-color") or "#000000"
        safe_url = escape(url, quote=True)
        safe_color = escape(color, quote=True)
        rewritten_tag = _set_background_attr(tag, safe_url)
        vml_open = (
            '\n<!--[if gte mso 9]>\n'
            f'<v:rect xmlns:v="urn:schemas-microsoft-com:vml" fill="true" stroke="false" data-onbrand-background="true" style="width:{width}px;">\n'
            f'<v:fill type="frame" aspect="atleast" src="{safe_url}" color="{safe_color}" />\n'
            '<v:textbox inset="0,0,0,0" style="mso-fit-shape-to-text:true;">\n'
            '<![endif]-->\n'
        )
        vml_close = (
            '\n<!--[if gte mso 9]>\n'
            '</v:textbox>\n'
            '</v:rect>\n'
            '<![endif]-->\n'
        )

        html = (
            html[:table_start]
            + rewritten_tag
            + html[table_open_end:cell_open_end]
            + vml_open
            + html[cell_open_end:cell_close_start]
            + vml_close
            + html[cell_close_start:table_close_end]
            + html[table_close_end:]
        )
        count += 1
        search_from = table_close_end + len(rewritten_tag) - len(tag) + len(vml_open) + len(vml_close)


def bulletproof_background_counts(html: str) -> tuple[int, int]:
    """Return eligible CSS background count and injected VML marker count."""
    eligible = 0
    search_from = 0
    while True:
        target = _next_background_table(html, search_from)
        if target is None:
            break
        eligible += 1
        search_from = target[3]
    return eligible, html.count('data-onbrand-background="true"')


def _next_background_table(html: str, start: int):
    for match in re.finditer(r"<table\b[^>]*>", html[start:], flags=re.IGNORECASE | re.DOTALL):
        table_start = start + match.start()
        table_open_end = start + match.end()
        tag = match.group(0)
        style_match = STYLE_RE.search(tag)
        if not style_match:
            continue
        style = style_match.group("style")
        background_match = BACKGROUND_URL_RE.search(style)
        if not background_match:
            continue
        url = background_match.group("url").strip()
        if not url or not _is_cover_background(style):
            continue
        closing = _matching_table_close(html, table_start)
        if closing is None:
            continue
        return table_start, table_open_end, closing[0], closing[1], tag, style, url
    return None


def _is_cover_background(style: str) -> bool:
    repeat = (_style_value(style, "background-repeat") or "").lower()
    size = (_style_value(style, "background-size") or "").lower()
    return repeat == "no-repeat" or size == "cover"


def _matching_table_close(html: str, opening_start: int) -> tuple[int, int] | None:
    depth = 0
    for match in TABLE_TAG_RE.finditer(html, opening_start):
        tag = match.group(0).lower()
        if tag.startswith("<table"):
            depth += 1
        elif tag.startswith("</table"):
            depth -= 1
            if depth == 0:
                return match.start(), match.end()
    return None


def _first_top_level_cell(html: str, content_start: int, table_close_start: int) -> tuple[int, int] | None:
    table_depth = 1
    cell_depth = 0
    cell_open_end = None
    for match in TABLE_TAG_RE.finditer(html, content_start, table_close_start):
        tag = match.group(0).lower()
        if tag.startswith("<table"):
            table_depth += 1
        elif tag.startswith("</table"):
            table_depth -= 1
        elif tag.startswith("<td") and table_depth == 1:
            if cell_open_end is None:
                cell_open_end = match.end()
            cell_depth += 1
        elif tag.startswith("</td") and table_depth == 1 and cell_open_end is not None:
            cell_depth -= 1
            if cell_depth == 0:
                return cell_open_end, match.start()
    return None


def _content_width(tag: str, style: str) -> int:
    width_match = re.search(r'\bwidth=["\']?(\d+)', tag, flags=re.IGNORECASE)
    if width_match:
        width = int(width_match.group(1))
    else:
        style_width = _style_value(style, "width") or "600px"
        match = re.match(r"\s*(\d+)px", style_width, flags=re.IGNORECASE)
        width = int(match.group(1)) if match else 600
    for side in ("border-left", "border-right"):
        value = _style_value(style, side) or ""
        match = re.match(r"\s*(\d+)px", value, flags=re.IGNORECASE)
        if match:
            width -= int(match.group(1))
    return max(width, 1)


def _style_value(style: str, property_name: str) -> str | None:
    match = re.search(
        rf"(?:^|;)\s*{re.escape(property_name)}\s*:\s*([^;]+)",
        style,
        flags=re.IGNORECASE,
    )
    return match.group(1).strip() if match else None


def _set_background_attr(tag: str, url: str) -> str:
    if re.search(r"\bbackground\s*=", tag, flags=re.IGNORECASE):
        return re.sub(
            r"\bbackground\s*=\s*([\"']).*?\1",
            f'background="{url}"',
            tag,
            count=1,
            flags=re.IGNORECASE | re.DOTALL,
        )
    return tag[:-1] + f' background="{url}">'
