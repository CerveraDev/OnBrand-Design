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
    image_workflow_id: str = ""


def apply_module_slots(
    module_id: str,
    row_html: str,
    slot_defs: dict,
    supplied_slots: dict,
    *,
    manifest_assets: dict[str, dict],
) -> tuple[str, list[UsedAsset]]:
    unknown = sorted(set(supplied_slots) - set(slot_defs))
    if unknown:
        raise SlotError(f"{module_id} has unknown slot(s): {', '.join(unknown)}")
    definitions = {name: _normalize_slot_definition(value) for name, value in slot_defs.items()}
    missing = sorted(
        name for name, definition in definitions.items()
        if definition.get("required") and name not in supplied_slots
    )
    if missing:
        raise SlotError(f"{module_id} is missing required slot(s): {', '.join(missing)}")
    html = row_html
    used: list[UsedAsset] = []
    missing_containers = {
        name: definition["container_annotation_anchor"]
        for name, definition in definitions.items()
        if name not in supplied_slots
        and definition.get("omit_if_missing")
        and definition.get("container_annotation_anchor")
    }
    for slot_name in supplied_slots:
        anchor = definitions[slot_name].get("annotation_anchor")
        owner = next(
            (
                owner_name
                for owner_name, container in missing_containers.items()
                if anchor and anchor != container and anchor in container
            ),
            None,
        )
        if owner:
            raise SlotError(f"{module_id}.{slot_name} requires container-owning slot {owner}")
    removed_containers: list[str] = []
    for slot_name, anchor in missing_containers.items():
        html = replace_once(html, anchor, "", f"{module_id}.{slot_name}.omit-container")
        removed_containers.append(anchor)
    for slot_name, definition in definitions.items():
        if slot_name in supplied_slots or not definition.get("omit_if_missing"):
            continue
        if definition.get("container_annotation_anchor"):
            continue
        anchor = definition.get("annotation_anchor")
        if not anchor:
            raise SlotError(f"{module_id}.{slot_name} cannot be omitted without an annotation anchor")
        if any(anchor in container for container in removed_containers):
            continue
        html = replace_once(html, anchor, "", f"{module_id}.{slot_name}.omit")
    for slot_name, definition in definitions.items():
        if slot_name not in supplied_slots:
            continue
        value = supplied_slots[slot_name]
        allowed_kinds = definition.get("allowed_kinds", [])
        if allowed_kinds and value.get("kind") not in allowed_kinds:
            raise SlotError(
                f"{module_id}.{slot_name} kind must be one of {', '.join(allowed_kinds)}"
            )
        if value.get("kind") in {"text", "safe_rich_text"}:
            word_count = len(re.findall(r"\b[\w'’-]+\b", value.get("value", "")))
            if definition.get("min_words") is not None and word_count < definition["min_words"]:
                raise SlotError(f"{module_id}.{slot_name} requires at least {definition['min_words']} words")
            if definition.get("max_words") is not None and word_count > definition["max_words"]:
                raise SlotError(f"{module_id}.{slot_name} allows at most {definition['max_words']} words")
        html, slot_assets = _apply_slot(
            module_id,
            slot_name,
            html,
            definition,
            value,
            manifest_assets,
        )
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
    definition: dict,
    value: dict,
    manifest_assets: dict[str, dict],
) -> tuple[str, list[UsedAsset]]:
    if not isinstance(value, dict):
        raise CampaignSpecError(f"{module_id}.{slot_name} slot value must be an object")
    kind = value.get("kind")
    rules = definition["rules"]
    rendered_text = ""
    image_src = ""
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
            used.append(
                UsedAsset(
                    source=src,
                    role=value.get("role", slot_name),
                    image_workflow_id=value.get("image_workflow_id", ""),
                )
            )
        image_src = src
        rendered_text = safe_attr(src)
    elif kind == "text_list":
        _validate_text_list(value, f"{module_id}.{slot_name}")
    elif kind == "amplified_list":
        _validate_amplified_list(value, f"{module_id}.{slot_name}")
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
                new_src=image_src,
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
        elif operation == "replace_image_src_first":
            if kind != "image":
                raise SlotError(f"{label} requires image")
            html = rewrite_first_img_by_src(
                html,
                rule["anchor"],
                new_src=image_src,
                alt=value.get("alt"),
                title=value.get("title", value.get("alt")),
                label=label,
            )
        elif operation == "annotation_replace_text":
            if kind not in {"text", "safe_rich_text"}:
                raise SlotError(f"{label} requires text or safe_rich_text")
            html = _replace_annotation(
                html,
                definition,
                rule,
                {rule["text_anchor"]: rendered_text},
                label,
            )
        elif operation == "annotation_replace_image":
            if kind != "image":
                raise SlotError(f"{label} requires image")
            anchor = _annotation_anchor(definition, label)
            rewritten = rewrite_img_by_src(
                anchor,
                rule["anchor"],
                new_src=image_src,
                alt=value.get("alt"),
                title=value.get("title", value.get("alt")),
                label=label,
            )
            html = replace_once(html, anchor, rewritten, label)
        elif operation == "annotation_repeat_text":
            if kind != "text_list":
                raise SlotError(f"{label} requires text_list")
            anchor = _annotation_anchor(definition, label)
            repeated = "".join(
                _replace_exact_once(anchor, rule["text_anchor"], safe_text(item), label)
                for item in value["items"]
            )
            html = replace_once(html, anchor, repeated, label)
        elif operation == "annotation_repeat_pairs":
            if kind != "amplified_list":
                raise SlotError(f"{label} requires amplified_list")
            anchor = _annotation_anchor(definition, label)
            blocks = []
            for item in value["items"]:
                block = _replace_exact_once(anchor, rule["text_anchor"], safe_text(item["term"]), label)
                block = _replace_exact_once(
                    block,
                    rule["secondary_text_anchor"],
                    safe_text(item["amplification"]),
                    label,
                )
                blocks.append(block)
            html = replace_once(html, anchor, "".join(blocks), label)
        elif operation == "annotation_replace_list":
            if kind != "text_list":
                raise SlotError(f"{label} requires text_list")
            anchor = _annotation_anchor(definition, label)
            items = "".join(
                rule["item_template"].replace("{item}", safe_text(item))
                for item in value["items"]
            )
            list_matches = list(re.finditer(r"(<ul\b[^>]*>)(.*?)(</ul>)", anchor, re.I | re.S))
            if len(list_matches) != 1:
                raise SlotError(f"{label} annotation must contain exactly one list; found {len(list_matches)}")
            match = list_matches[0]
            rewritten = anchor[: match.start(2)] + items + anchor[match.end(2) :]
            html = replace_once(html, anchor, rewritten, label)
        else:
            raise SlotError(f"{label} uses unknown operation {operation!r}")
    return html, used


def _normalize_slot_definition(value) -> dict:
    if isinstance(value, list):
        return {"rules": value, "required": False, "omit_if_missing": False}
    return value


def _annotation_anchor(definition: dict, label: str) -> str:
    anchor = definition.get("annotation_anchor")
    if not isinstance(anchor, str) or not anchor:
        raise SlotError(f"{label} requires an annotation anchor")
    return anchor


def _replace_annotation(
    html: str,
    definition: dict,
    rule: dict,
    replacements: dict[str, str],
    label: str,
) -> str:
    anchor = _annotation_anchor(definition, label)
    rewritten = anchor
    for old, new in replacements.items():
        rewritten = _replace_exact_once(rewritten, old, new, label)
    return replace_once(html, anchor, rewritten, label)


def _replace_exact_once(value: str, anchor: str, replacement: str, label: str) -> str:
    count = value.count(anchor)
    if count != 1:
        raise SlotError(f"{label} annotation anchor must resolve exactly once; found {count}")
    return value.replace(anchor, replacement, 1)


def _validate_text_list(value: dict, label: str) -> None:
    items = value.get("items")
    if not isinstance(items, list) or not items or not all(isinstance(item, str) and item for item in items):
        raise CampaignSpecError(f"{label}.items must be a non-empty array of strings")


def _validate_amplified_list(value: dict, label: str) -> None:
    items = value.get("items")
    if not isinstance(items, list) or not items:
        raise CampaignSpecError(f"{label}.items must be a non-empty array")
    for index, item in enumerate(items):
        if not isinstance(item, dict) or set(item) != {"term", "amplification"}:
            raise CampaignSpecError(
                f"{label}.items[{index}] must contain only term and amplification"
            )
        if not all(isinstance(item[field], str) and item[field] for field in item):
            raise CampaignSpecError(f"{label}.items[{index}] values must be non-empty strings")


def _set_attr(tag: str, attr: str, value: str) -> str:
    escaped = safe_attr(value)
    pattern = re.compile(rf'\b{re.escape(attr)}="[^"]*"', re.IGNORECASE)
    replacement = f'{attr}="{escaped}"'
    if pattern.search(tag):
        return pattern.sub(replacement, tag, count=1)
    insert_at = tag.rfind(">")
    return tag[:insert_at] + " " + replacement + tag[insert_at:]


def rewrite_first_img_by_src(
    html: str,
    old_src: str,
    *,
    new_src: str,
    alt: str | None,
    title: str | None,
    label: str,
) -> str:
    pattern = re.compile(r"<img\b[^>]*>", re.IGNORECASE)
    match = next((item for item in pattern.finditer(html) if f'src="{old_src}"' in item.group(0)), None)
    if match is None:
        raise SlotError(f"{label} image anchor was not found")
    tag = match.group(0)
    rewritten = _set_attr(tag, "src", new_src)
    if alt is not None:
        rewritten = _set_attr(rewritten, "alt", alt)
    if title is not None:
        rewritten = _set_attr(rewritten, "title", title)
    return html[: match.start()] + rewritten + html[match.end() :]


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
