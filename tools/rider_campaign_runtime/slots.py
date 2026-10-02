from __future__ import annotations

from dataclasses import dataclass
from html import escape
from html.parser import HTMLParser
import re

from .schema import CampaignSpecError, validate_href, validate_image_url


class SlotError(ValueError):
    """Raised when a deterministic slot cannot be applied exactly once."""


SAFE_RICH_TAGS = {"br", "strong", "em", "b", "i"}


@dataclass(frozen=True)
class UsedAsset:
    source: str
    role: str
    identity: str = ""
    filename: str = ""
    dropbox_path: str = ""


def apply_module_slots(
    module_id: str,
    row_html: str,
    slot_defs: dict,
    supplied_slots: dict,
    *,
    manifest_assets: dict[str, dict],
) -> tuple[str, list[UsedAsset]]:
    if not supplied_slots:
        return row_html, []
    unknown = sorted(set(supplied_slots) - set(slot_defs))
    if unknown:
        raise SlotError(f"{module_id} has unknown slot(s): {', '.join(unknown)}")
    html = row_html
    used: list[UsedAsset] = []
    for slot_name, value in supplied_slots.items():
        expected_rules = slot_defs[slot_name]
        html, slot_assets = _apply_slot(module_id, slot_name, html, expected_rules, value, manifest_assets)
        used.extend(slot_assets)
    return html, used


def safe_text(value: str) -> str:
    return escape(value, quote=False).replace("\n", "<br>")


def safe_attr(value: str) -> str:
    return escape(value, quote=True)


def safe_rich_text(value: str) -> str:
    parser = _SafeRichTextParser()
    parser.feed(value)
    parser.close()
    if parser.errors:
        raise SlotError("; ".join(parser.errors))
    return "".join(parser.output)


def replace_once(html: str, anchor: str, replacement: str, label: str) -> str:
    count = html.count(anchor)
    if count != 1:
        raise SlotError(f"{label} anchor must resolve exactly once; found {count}")
    return html.replace(anchor, replacement, 1)


def rewrite_img_by_src(
    html: str,
    old_src: str,
    *,
    new_src: str,
    alt: str | None = None,
    title: str | None = None,
    label: str,
) -> str:
    pattern = re.compile(r"<img\b[^>]*>", re.IGNORECASE)
    matches = [match for match in pattern.finditer(html) if f'src="{old_src}"' in match.group(0)]
    if len(matches) != 1:
        raise SlotError(f"{label} image anchor must resolve exactly once; found {len(matches)}")
    tag = matches[0].group(0)
    rewritten = _set_attr(tag, "src", new_src)
    if alt is not None:
        rewritten = _set_attr(rewritten, "alt", alt)
    if title is not None:
        rewritten = _set_attr(rewritten, "title", title)
    return html[: matches[0].start()] + rewritten + html[matches[0].end() :]


def _apply_slot(
    module_id: str,
    slot_name: str,
    html: str,
    rules: list[dict],
    value: dict,
    manifest_assets: dict[str, dict],
) -> tuple[str, list[UsedAsset]]:
    if not isinstance(value, dict):
        raise CampaignSpecError(f"{module_id}.{slot_name} slot value must be an object")
    kind = value.get("kind")
    rendered_text = ""
    used: list[UsedAsset] = []
    if kind == "text":
        rendered_text = safe_text(value["value"])
    elif kind == "safe_rich_text":
        rendered_text = safe_rich_text(value["value"])
    elif kind == "url":
        validate_href(value["href"], f"{module_id}.{slot_name}.href")
        rendered_text = safe_attr(value["href"])
    elif kind == "image":
        if "asset_id" in value:
            asset_id = value["asset_id"]
            if asset_id not in manifest_assets:
                raise SlotError(f"{module_id}.{slot_name} asset_id is not in manifest: {asset_id}")
            asset = manifest_assets[asset_id]
            if asset.get("media_type") != "image":
                raise SlotError(f"{module_id}.{slot_name} asset_id is not an image: {asset_id}")
            required_approvals = {
                rule.get("required_approval") for rule in rules if rule.get("required_approval")
            }
            if len(required_approvals) > 1:
                raise SlotError(f"{module_id}.{slot_name} has conflicting approval rules")
            if required_approvals:
                required_approval = next(iter(required_approvals))
                approved_for = {item.lower() for item in asset.get("approved_for", [])}
                if required_approval.lower() not in approved_for:
                    raise SlotError(
                        f"{module_id}.{slot_name} asset_id is not approved for {required_approval}: {asset_id}"
                    )
            src = asset["public_url"]
            used.append(
                UsedAsset(
                    source=src,
                    role=value.get("role", slot_name),
                    identity=asset["dropbox_id"],
                    filename=asset["filename"],
                    dropbox_path=asset["dropbox_path"],
                )
            )
        else:
            src = value["src"]
            validate_image_url(src, f"{module_id}.{slot_name}.src")
            used.append(UsedAsset(source=src, role=value.get("role", slot_name)))
        rendered_text = safe_attr(src)
    else:
        raise CampaignSpecError(f"{module_id}.{slot_name} has unsupported kind {kind!r}")

    for rule in rules:
        operation = rule["operation"]
        label = f"{module_id}.{slot_name}.{operation}"
        if operation == "replace_text":
            if kind not in {"text", "safe_rich_text"}:
                raise SlotError(f"{label} requires text or safe_rich_text")
            html = replace_once(html, rule["anchor"], rendered_text, label)
        elif operation == "replace_text_in_context":
            if kind not in {"text", "safe_rich_text"}:
                raise SlotError(f"{label} requires text or safe_rich_text")
            context = rule["anchor"]
            text_anchor = rule["text_anchor"]
            if context.count(text_anchor) != 1:
                raise SlotError(f"{label} context must contain its text anchor exactly once")
            rewritten_context = context.replace(text_anchor, rendered_text, 1)
            html = replace_once(html, context, rewritten_context, label)
        elif operation == "replace_href":
            if kind != "url":
                raise SlotError(f"{label} requires url")
            html = replace_once(html, f'href="{rule["anchor"]}"', f'href="{rendered_text}"', label)
        elif operation == "replace_image_src":
            if kind != "image":
                raise SlotError(f"{label} requires image")
            html = rewrite_img_by_src(
                html,
                rule["anchor"],
                new_src=rendered_text,
                alt=value.get("alt"),
                title=value.get("title", value.get("alt")),
                label=label,
            )
        elif operation == "replace_background_url":
            if kind != "image":
                raise SlotError(f"{label} requires image")
            html = replace_once(
                html,
                f"background-image: url('{rule['anchor']}')",
                f"background-image: url('{rendered_text}')",
                label,
            )
        else:
            raise SlotError(f"{label} uses unknown operation {operation!r}")
    return html, used


def _set_attr(tag: str, attr: str, value: str) -> str:
    escaped = safe_attr(value)
    pattern = re.compile(rf'\b{re.escape(attr)}="[^"]*"', re.IGNORECASE)
    replacement = f'{attr}="{escaped}"'
    if pattern.search(tag):
        return pattern.sub(replacement, tag, count=1)
    insert_at = tag.rfind(">")
    return tag[:insert_at] + " " + replacement + tag[insert_at:]


class _SafeRichTextParser(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=False)
        self.output: list[str] = []
        self.errors: list[str] = []

    def handle_starttag(self, tag, attrs):
        if tag not in SAFE_RICH_TAGS:
            self.errors.append(f"safe rich text tag <{tag}> is not allowed")
            return
        if attrs:
            self.errors.append(f"safe rich text tag <{tag}> may not have attributes")
            return
        self.output.append(f"<{tag}>")

    def handle_endtag(self, tag):
        if tag not in SAFE_RICH_TAGS or tag == "br":
            self.errors.append(f"safe rich text closing tag </{tag}> is not allowed")
            return
        self.output.append(f"</{tag}>")

    def handle_data(self, data):
        self.output.append(safe_text(data))

    def handle_entityref(self, name):
        self.output.append(f"&{name};")

    def handle_charref(self, name):
        self.output.append(f"&#{name};")
