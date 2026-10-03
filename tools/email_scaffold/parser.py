from __future__ import annotations

from collections import Counter
from dataclasses import dataclass
from html.parser import HTMLParser
import re
from typing import Iterable


START_MARKER_COLOR = "#55ebb9"
END_MARKER_COLOR = "#ff81fb"
STATIC_START_MARKER_COLOR = "#ffd675"
STATIC_END_MARKER_COLOR = "#75edff"
MARKER_TEXT_COLOR = "#393d47"
START_MARKER_COLORS = {START_MARKER_COLOR, STATIC_START_MARKER_COLOR}
END_MARKER_COLORS = {END_MARKER_COLOR, STATIC_END_MARKER_COLOR}
MARKER_COLORS = START_MARKER_COLORS | END_MARKER_COLORS

_HEX_COLOR_RE = re.compile(r"#[0-9a-fA-F]{3}(?:[0-9a-fA-F]{3})?\b")


class ScaffoldError(ValueError):
    """Raised when a Beefree scaffold cannot be parsed into valid modules."""


@dataclass(frozen=True)
class Row:
    number: int
    classes: tuple[str, ...]
    start: int
    end: int
    html: str
    text: str
    style_colors: Counter[str]

    @property
    def marker_label(self) -> str | None:
        if self.text.startswith("START - "):
            return self.text.removeprefix("START - ")
        if self.text.startswith("END - "):
            return self.text.removeprefix("END - ")
        return None

    @property
    def is_marker(self) -> bool:
        colors = set(self.style_colors)
        has_marker_color = bool(colors & MARKER_COLORS)
        return has_marker_color and self.marker_label is not None


@dataclass(frozen=True)
class ModuleBoundary:
    label: str
    start_marker_row: int
    end_marker_row: int
    content_rows: tuple[int, ...]


class _RowParser(HTMLParser):
    def __init__(self, html: str):
        super().__init__(convert_charrefs=True)
        self._html = html
        self._line_offsets = _line_offsets(html)
        self._table_stack: list[int | None] = []
        self._active_rows: list[dict] = []
        self.rows: list[Row] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        attrs_dict = {key: value or "" for key, value in attrs}
        row_number = _row_number(tag, attrs_dict.get("class", ""))
        if tag == "table":
            self._table_stack.append(row_number)
        if row_number is not None:
            start = self._absolute_position()
            self._active_rows.append(
                {
                    "number": row_number,
                    "classes": tuple(attrs_dict.get("class", "").split()),
                    "start": start,
                    "texts": [],
                    "style_colors": Counter(_colors_in_style(attrs_dict.get("style", ""))),
                    "table_depth": len(self._table_stack),
                }
            )
        elif self._active_rows and attrs_dict.get("style"):
            self._active_rows[-1]["style_colors"].update(_colors_in_style(attrs_dict["style"]))

    def handle_endtag(self, tag: str) -> None:
        if tag == "table" and self._table_stack:
            row_number = self._table_stack.pop()
            if row_number is not None:
                row = self._active_rows.pop()
                end = self._absolute_position() + len("</table>")
                self.rows.append(
                    Row(
                        number=row["number"],
                        classes=row["classes"],
                        start=row["start"],
                        end=end,
                        html=self._html[row["start"] : end],
                        text=" ".join(row["texts"]).strip(),
                        style_colors=row["style_colors"],
                    )
                )

    def handle_data(self, data: str) -> None:
        if self._active_rows:
            text = " ".join(data.split())
            if text:
                self._active_rows[-1]["texts"].append(text)

    def _absolute_position(self) -> int:
        line, column = self.getpos()
        return self._line_offsets[line - 1] + column


def parse_rows(html: str) -> list[Row]:
    parser = _RowParser(html)
    parser.feed(html)
    rows = sorted(parser.rows, key=lambda row: row.number)
    expected = list(range(1, len(rows) + 1))
    actual = [row.number for row in rows]
    if actual != expected:
        raise ScaffoldError(f"Expected contiguous row numbers {expected!r}; got {actual!r}")
    return rows


def find_module_boundaries(rows: Iterable[Row]) -> list[ModuleBoundary]:
    rows_by_number = {row.number: row for row in rows}
    starts: list[Row] = []
    boundaries: list[ModuleBoundary] = []
    for row in sorted(rows_by_number.values(), key=lambda item: item.number):
        if not row.is_marker:
            continue
        if row.text.startswith("START - "):
            starts.append(row)
            continue
        if row.text.startswith("END - "):
            if not starts:
                raise ScaffoldError(f"END marker at row {row.number} has no matching START marker")
            start = starts.pop()
            if start.marker_label != row.marker_label:
                raise ScaffoldError(
                    f"Marker mismatch: row {start.number} is {start.marker_label!r}, "
                    f"row {row.number} is {row.marker_label!r}"
                )
            boundaries.append(
                ModuleBoundary(
                    label=start.marker_label or "",
                    start_marker_row=start.number,
                    end_marker_row=row.number,
                    content_rows=tuple(range(start.number + 1, row.number)),
                )
            )
    if starts:
        labels = ", ".join(f"{row.number}:{row.marker_label}" for row in starts)
        raise ScaffoldError(f"Unclosed START marker(s): {labels}")
    return boundaries


def render_without_marker_rows(html: str) -> str:
    rows = parse_rows(html)
    rendered = html
    for row in sorted((row for row in rows if row.is_marker), key=lambda item: item.start, reverse=True):
        rendered = rendered[: row.start] + rendered[row.end :]
    return rendered


def analyze_style_colors(rows: Iterable[Row], *, include_marker_rows: bool = False) -> Counter[str]:
    colors: Counter[str] = Counter()
    for row in rows:
        if row.is_marker and not include_marker_rows:
            continue
        colors.update(row.style_colors)
    return colors


def apply_canonical_text_corrections(html: str) -> str:
    return (
        html.replace("REQUEST MORE INFORMAITON", "REQUEST MORE INFORMATION")
        .replace("ARTTS", "ARTS")
        .replace("START - UNBRANDED FOOTER", "START - OUTSIDE-BROKER CUSTOMIZABLE FOOTER")
        .replace("END - UNBRANDED FOOTER", "END - OUTSIDE-BROKER CUSTOMIZABLE FOOTER")
    )


def _line_offsets(html: str) -> list[int]:
    offsets = [0]
    for match in re.finditer("\n", html):
        offsets.append(match.end())
    return offsets


def _row_number(tag: str, class_value: str) -> int | None:
    if tag != "table":
        return None
    tokens = class_value.split()
    if "row" not in tokens:
        return None
    for token in tokens:
        if token.startswith("row-") and token[4:].isdigit():
            return int(token[4:])
    return None


def _colors_in_style(style: str) -> list[str]:
    return [color.lower() for color in _HEX_COLOR_RE.findall(style)]
