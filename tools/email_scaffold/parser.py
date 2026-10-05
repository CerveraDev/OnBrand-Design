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
_MARKER_PREFIX_RE = re.compile(r"^(START|END) - (.+)$")
_MARKER_TOKEN_RE = re.compile(r"(?:^|\s)(?:START|END) - ")


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
        marker = _marker_parts(self.text)
        return marker[1] if marker else None

    @property
    def marker_kind(self) -> str | None:
        marker = _marker_parts(self.text)
        return marker[0] if marker else None

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


@dataclass(frozen=True)
class MarkerElement:
    kind: str
    label: str
    text: str
    color: str
    row_number: int
    start: int
    end: int
    is_full_row: bool


@dataclass(frozen=True)
class AnnotationBoundary:
    label: str
    start_marker: MarkerElement
    end_marker: MarkerElement
    parent_module_label: str | None
    parent_annotation_label: str | None
    depth: int
    content_rows: tuple[int, ...]
    content_html: str


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


class _MarkerElementParser(HTMLParser):
    def __init__(self, html: str):
        super().__init__(convert_charrefs=True)
        self._html = html
        self._line_offsets = _line_offsets(html)
        self._active_paragraphs: list[dict] = []
        self.paragraphs: list[dict] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        attrs_dict = {key: value or "" for key, value in attrs}
        if tag == "p":
            self._active_paragraphs.append(
                {
                    "start": self._absolute_position(),
                    "texts": [],
                    "style_colors": Counter(_colors_in_style(attrs_dict.get("style", ""))),
                }
            )
        elif self._active_paragraphs and attrs_dict.get("style"):
            self._active_paragraphs[-1]["style_colors"].update(
                _colors_in_style(attrs_dict["style"])
            )

    def handle_endtag(self, tag: str) -> None:
        if tag != "p" or not self._active_paragraphs:
            return
        paragraph = self._active_paragraphs.pop()
        end = self._absolute_position() + len("</p>")
        paragraph["end"] = end
        paragraph["text"] = " ".join(paragraph["texts"]).strip()
        self.paragraphs.append(paragraph)

    def handle_data(self, data: str) -> None:
        if not self._active_paragraphs:
            return
        text = " ".join(data.split())
        if text:
            self._active_paragraphs[-1]["texts"].append(text)

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
        if row.marker_kind == "START":
            starts.append(row)
            continue
        if row.marker_kind == "END":
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


def parse_marker_elements(html: str, rows: Iterable[Row] | None = None) -> list[MarkerElement]:
    parsed_rows = list(rows) if rows is not None else parse_rows(html)
    parser = _MarkerElementParser(html)
    parser.feed(html)
    elements: list[MarkerElement] = []
    for paragraph in parser.paragraphs:
        marker = _marker_parts(paragraph["text"], require_single_token=False)
        if marker is None:
            continue
        kind, label = marker
        row = _containing_row(parsed_rows, paragraph["start"], paragraph["end"])
        expected_colors = START_MARKER_COLORS if kind == "START" else END_MARKER_COLORS
        local_colors = set(paragraph["style_colors"]) & expected_colors
        row_colors = set(row.style_colors) & expected_colors
        colors = sorted(local_colors or row_colors)
        if not colors:
            raise ScaffoldError(
                f"{kind} marker {label!r} in row {row.number} has no matching marker color"
            )
        elements.append(
            MarkerElement(
                kind=kind,
                label=label,
                text=paragraph["text"],
                color=colors[0],
                row_number=row.number,
                start=paragraph["start"],
                end=paragraph["end"],
                is_full_row=row.marker_kind == kind and row.marker_label == label,
            )
        )
    return sorted(elements, key=lambda element: element.start)


def find_annotation_boundaries(
    html: str, rows: Iterable[Row] | None = None
) -> list[AnnotationBoundary]:
    parsed_rows = list(rows) if rows is not None else parse_rows(html)
    markers = parse_marker_elements(html, parsed_rows)
    stack: list[tuple[MarkerElement, str | None, str | None, int]] = []
    annotations: list[AnnotationBoundary] = []
    for marker in markers:
        if marker.kind == "START":
            parent_module = next(
                (open_marker.label for open_marker, *_ in reversed(stack) if open_marker.is_full_row),
                None,
            )
            parent_annotation = next(
                (open_marker.label for open_marker, *_ in reversed(stack) if not open_marker.is_full_row),
                None,
            )
            depth = sum(1 for open_marker, *_ in stack if not open_marker.is_full_row)
            stack.append((marker, parent_module, parent_annotation, depth))
            continue
        if not stack:
            raise ScaffoldError(
                f"END marker {marker.label!r} in row {marker.row_number} has no matching START marker"
            )
        start, parent_module, parent_annotation, depth = stack.pop()
        if start.label != marker.label:
            raise ScaffoldError(
                f"Marker mismatch: row {start.row_number} is {start.label!r}, "
                f"row {marker.row_number} is {marker.label!r}"
            )
        if start.is_full_row != marker.is_full_row:
            raise ScaffoldError(
                f"Marker scope mismatch for {start.label!r}: START and END must both be "
                "row-level or both be inline"
            )
        if start.is_full_row:
            continue
        annotations.append(
            AnnotationBoundary(
                label=start.label,
                start_marker=start,
                end_marker=marker,
                parent_module_label=parent_module,
                parent_annotation_label=parent_annotation,
                depth=depth,
                content_rows=tuple(range(start.row_number, marker.row_number + 1)),
                content_html=html[start.end : marker.start],
            )
        )
    if stack:
        labels = ", ".join(
            f"{marker.row_number}:{marker.label}" for marker, *_ in stack
        )
        raise ScaffoldError(f"Unclosed START marker(s): {labels}")
    return sorted(annotations, key=lambda boundary: boundary.start_marker.start)


def render_without_marker_rows(html: str) -> str:
    rows = parse_rows(html)
    rendered = html
    for row in sorted((row for row in rows if row.is_marker), key=lambda item: item.start, reverse=True):
        rendered = rendered[: row.start] + rendered[row.end :]
    return rendered


def render_without_authoring_markers(html: str) -> str:
    rows = parse_rows(html)
    find_annotation_boundaries(html, rows)
    ranges = [(row.start, row.end) for row in rows if row.is_marker]
    ranges.extend(
        (marker.start, marker.end)
        for marker in parse_marker_elements(html, rows)
        if not marker.is_full_row
    )
    rendered = html
    for start, end in sorted(_merge_ranges(ranges), reverse=True):
        rendered = rendered[:start] + rendered[end:]
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


def _marker_parts(text: str, *, require_single_token: bool = True) -> tuple[str, str] | None:
    if require_single_token and len(_MARKER_TOKEN_RE.findall(text)) != 1:
        return None
    match = _MARKER_PREFIX_RE.fullmatch(text)
    if not match:
        return None
    return match.group(1), match.group(2).strip()


def _containing_row(rows: Iterable[Row], start: int, end: int) -> Row:
    for row in rows:
        if row.start <= start and end <= row.end:
            return row
    raise ScaffoldError(f"Marker element at offsets {start}-{end} is not inside a scaffold row")


def _merge_ranges(ranges: Iterable[tuple[int, int]]) -> list[tuple[int, int]]:
    merged: list[list[int]] = []
    for start, end in sorted(ranges):
        if merged and start <= merged[-1][1]:
            merged[-1][1] = max(merged[-1][1], end)
        else:
            merged.append([start, end])
    return [(start, end) for start, end in merged]
