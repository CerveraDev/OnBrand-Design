from __future__ import annotations

from dataclasses import dataclass
from html.parser import HTMLParser
import re

from .scaffold import FOOTER_MODULES, Scaffold, module_rows


class CopyAllocationError(ValueError):
    """Raised when campaign copy ownership or dedupe policy is unsafe."""


ALLOCATION_VERSION = "1.0"
APPROVED_STATUS = "approved"
CHANNELS = {"live-html", "baked-image-text", "alt-text", "metadata", "static", "legal", "footer"}
REUSE_POLICIES = {
    "single-use",
    "intentional-refrain",
    "required-legal",
    "static-brand",
    "required-name",
    "footer-contact",
    "metadata-required",
}
CLAIM_POLICIES = {"none", "requires-evidence", "approved-no-evidence-required"}
NEAR_DUPLICATE_WARN_THRESHOLD = 0.65
NEAR_DUPLICATE_BLOCK_THRESHOLD = 0.82


@dataclass(frozen=True)
class CopyRef:
    channel: str
    text: str = ""
    module_id: str = ""
    slot: str = ""
    metadata_field: str = ""
    image_workflow_id: str = ""
    static_block_id: str = ""

    @property
    def owner_key(self) -> str:
        parts = [self.channel]
        if self.module_id:
            parts.append(self.module_id)
        if self.slot:
            parts.append(self.slot)
        if self.metadata_field:
            parts.append(self.metadata_field)
        if self.image_workflow_id:
            parts.append(self.image_workflow_id)
        if self.static_block_id:
            parts.append(self.static_block_id)
        return "::".join(parts)


def validate_copy_allocation(spec: dict, *, scaffold: Scaffold) -> dict:
    allocation = spec.get("copy_allocation")
    if not isinstance(allocation, dict):
        raise CopyAllocationError("copy_allocation is required")
    if allocation.get("version") != ALLOCATION_VERSION:
        raise CopyAllocationError(f"copy_allocation.version must be {ALLOCATION_VERSION}")
    if allocation.get("status") != APPROVED_STATUS:
        raise CopyAllocationError("copy_allocation.status must be approved before runtime assembly")

    units = allocation.get("content_units")
    if not isinstance(units, list) or not units:
        raise CopyAllocationError("copy_allocation.content_units must be a non-empty array")
    unit_ids = [unit.get("id", "") for unit in units if isinstance(unit, dict)]
    duplicates = sorted({unit_id for unit_id in unit_ids if unit_ids.count(unit_id) > 1})
    if duplicates:
        raise CopyAllocationError("Duplicate copy allocation content unit id(s): " + ", ".join(duplicates))

    refs = _collect_runtime_copy_refs(spec)
    ref_by_owner = {ref.owner_key: ref for ref in refs}
    checks: list[dict] = []
    occurrences: list[dict] = []
    normalized_units: dict[str, str] = {}
    max_by_unit: dict[str, int] = {}
    reuse_by_unit: dict[str, str] = {}
    exempted = _exemption_keys(allocation.get("dedupe_exemptions", []))

    owner_counts: dict[str, list[str]] = {}
    for index, unit in enumerate(units):
        if not isinstance(unit, dict):
            raise CopyAllocationError(f"copy_allocation.content_units[{index}] must be an object")
        unit_id = _require_str(unit, "id", f"copy_allocation.content_units[{index}]")
        text = _require_str(unit, "text", f"copy_allocation.content_units[{index}]")
        owner = _require_object(unit, "owner", f"copy_allocation.content_units[{index}]")
        channel = _require_str(owner, "channel", f"copy_allocation.content_units[{index}].owner")
        if channel not in CHANNELS:
            raise CopyAllocationError(f"{unit_id} owner.channel is not supported: {channel}")
        approval_status = _require_str(unit, "approval_status", f"copy_allocation.content_units[{index}]")
        if approval_status != APPROVED_STATUS:
            raise CopyAllocationError(f"{unit_id} approval_status must be approved")
        reuse_policy = unit.get("reuse_policy", "single-use")
        if reuse_policy not in REUSE_POLICIES:
            raise CopyAllocationError(f"{unit_id} reuse_policy is not supported: {reuse_policy}")
        max_occurrences = unit.get("max_occurrences", 1)
        if type(max_occurrences) is not int or max_occurrences < 1:
            raise CopyAllocationError(f"{unit_id} max_occurrences must be a positive integer")

        key = _owner_key(owner)
        owner_counts.setdefault(key, []).append(unit_id)
        normalized_text = normalize_text(text)
        if not normalized_text:
            raise CopyAllocationError(f"{unit_id} has no normalized copy text")
        normalized_units[unit_id] = normalized_text
        max_by_unit[unit_id] = max_occurrences
        reuse_by_unit[unit_id] = reuse_policy

        if channel in {"live-html", "alt-text", "metadata"}:
            if channel != "metadata" and owner.get("slot") not in scaffold.slot_map.get(owner.get("module_id"), {}):
                raise CopyAllocationError(f"{unit_id} owner is unknown to the scaffold slot map")
            ref = ref_by_owner.get(key)
            if ref is None:
                raise CopyAllocationError(f"{unit_id} owner is unknown or stale: {key}")
            if ref.text != text:
                raise CopyAllocationError(f"{unit_id} text does not match its owner slot")
        elif channel == "baked-image-text":
            image_id = _require_str(owner, "image_workflow_id", f"{unit_id}.owner")
            _validate_baked_image_owner(spec, image_id, unit)
            refs.append(CopyRef(channel="baked-image-text", image_workflow_id=image_id, text=text))
        elif channel == "static":
            static_id = _require_str(owner, "static_block_id", f"{unit_id}.owner")
            if static_id not in scaffold.static_boundaries:
                raise CopyAllocationError(f"{unit_id} static owner is unknown: {static_id}")
            if not any(item.get("id") == static_id for item in spec.get("modules", [])):
                raise CopyAllocationError(f"{unit_id} static owner is excluded: {static_id}")
            _validate_locked_text(scaffold, static_id, normalized_text, unit_id)
            refs.append(CopyRef(channel=channel, static_block_id=static_id, text=text))
        elif channel in {"legal", "footer"}:
            module_id = _require_str(owner, "module_id", f"{unit_id}.owner")
            if module_id not in FOOTER_MODULES:
                raise CopyAllocationError(f"{unit_id} protected owner is unknown: {module_id}")
            _validate_locked_text(scaffold, module_id, normalized_text, unit_id)
            refs.append(CopyRef(channel=channel, module_id=module_id, slot=owner.get("slot", ""), text=text))

        if reuse_policy != "single-use" and unit_id not in exempted:
            raise CopyAllocationError(f"{unit_id} reuse_policy {reuse_policy} requires a dedupe_exemption")
        if reuse_policy == "single-use" and max_occurrences != 1:
            raise CopyAllocationError(f"{unit_id} single-use max_occurrences must be 1")

        claim_policy = unit.get("claim_policy", "none")
        if claim_policy not in CLAIM_POLICIES:
            raise CopyAllocationError(f"{unit_id} claim_policy is not supported: {claim_policy}")
        claim_refs = unit.get("claim_references", [])
        if not isinstance(claim_refs, list) or any(not isinstance(item, str) or not item for item in claim_refs):
            raise CopyAllocationError(f"{unit_id} claim_references must be an array of strings")
        if claim_policy == "requires-evidence" and not claim_refs:
            raise CopyAllocationError(f"{unit_id} has unsupported claim requiring evidence")

    _validate_allocation_links(allocation, units, exempted)
    baked_ids = {unit["owner"].get("image_workflow_id") for unit in units if unit["owner"]["channel"] == "baked-image-text"}
    for item in spec.get("image_workflow", {}).get("items", []):
        if item.get("prompt_record", {}).get("text_policy") == "baked-approved" and item.get("image_id") not in baked_ids:
            raise CopyAllocationError(f"Baked image {item.get('image_id')} is missing declared copy text")

    ambiguous = {owner: ids for owner, ids in owner_counts.items() if len(ids) > 1}
    if ambiguous:
        details = ", ".join(f"{owner} => {', '.join(ids)}" for owner, ids in sorted(ambiguous.items()))
        raise CopyAllocationError("Ambiguous copy owner allocation: " + details)

    unit_owner_keys = set(owner_counts)
    unallocated = sorted(ref.owner_key for ref in refs if ref.owner_key not in unit_owner_keys)
    if unallocated:
        raise CopyAllocationError("Unallocated runtime copy owner(s): " + ", ".join(unallocated))

    for unit_id, normalized_text in sorted(normalized_units.items()):
        max_occurrences = max_by_unit[unit_id]
        count = _normalized_occurrence_count(normalized_text, refs)
        occurrences.append(
            {
                "content_unit_id": unit_id,
                "normalized_text": normalized_text,
                "occurrences": count,
                "max_occurrences": max_occurrences,
                "reuse_policy": reuse_by_unit[unit_id],
            }
        )
        _check(
            checks,
            f"copy-unit:{unit_id}:occurrences",
            count <= max_occurrences,
            f"{count} occurrence(s), max {max_occurrences}",
        )

    restricted_results = _check_restricted_phrases(allocation.get("restricted_phrases", []), refs, exempted)
    checks.extend(restricted_results["checks"])
    similarity = _similarity_checks(units, normalized_units, exempted)
    checks.extend(similarity["checks"])
    failed = [item["name"] for item in checks if not item["passed"]]
    if failed:
        raise CopyAllocationError("Copy allocation QA failed: " + ", ".join(failed))

    return {
        "version": ALLOCATION_VERSION,
        "plan_id": allocation.get("plan_id", ""),
        "status": APPROVED_STATUS,
        "approved_by": allocation.get("approved_by", ""),
        "approved_at": allocation.get("approved_at", ""),
        "content_unit_count": len(units),
        "runtime_copy_owner_count": len(refs),
        "restricted_phrase_count": len(allocation.get("restricted_phrases", [])),
        "content_units": units,
        "dedupe_exemptions": allocation.get("dedupe_exemptions", []),
        "occurrences": occurrences,
        "restricted_phrases": restricted_results["phrases"],
        "similarity": similarity["pairs"],
        "thresholds": {
            "near_duplicate_warning": NEAR_DUPLICATE_WARN_THRESHOLD,
            "near_duplicate_blocking": NEAR_DUPLICATE_BLOCK_THRESHOLD,
        },
        "checks": checks,
        "passed": all(item["passed"] for item in checks),
    }


def normalize_text(value: str) -> str:
    text = _html_to_text(value)
    text = text.replace("’", "'").replace("‘", "'").replace("“", '"').replace("”", '"')
    text = text.replace("—", " ").replace("–", " ")
    text = re.sub(r"https?://\S+", " ", text.lower())
    text = re.sub(r"[^a-z0-9']+", " ", text)
    return re.sub(r"\s+", " ", text).strip()


def _collect_runtime_copy_refs(spec: dict) -> list[CopyRef]:
    refs: list[CopyRef] = []
    campaign = spec.get("campaign", {})
    for field in ("subject", "preview_text"):
        value = campaign.get(field, "")
        if isinstance(value, str) and value.strip():
            refs.append(CopyRef(channel="metadata", metadata_field=field, text=value))
    for module in spec.get("modules", []):
        module_id = module.get("id", "")
        for slot_name, slot in module.get("slots", {}).items():
            if not isinstance(slot, dict):
                continue
            kind = slot.get("kind")
            if kind in {"text", "safe_rich_text"} and slot.get("value", "").strip():
                refs.append(CopyRef(channel="live-html", module_id=module_id, slot=slot_name, text=slot["value"]))
            if kind == "image" and slot.get("alt", "").strip():
                refs.append(
                    CopyRef(
                        channel="alt-text",
                        module_id=module_id,
                        slot=slot_name,
                        text=slot["alt"],
                        image_workflow_id=slot.get("image_workflow_id", ""),
                    )
                )
    return refs


def _validate_baked_image_owner(spec: dict, image_id: str, unit: dict) -> None:
    workflows = {
        item.get("image_id"): item
        for item in spec.get("image_workflow", {}).get("items", [])
        if isinstance(item, dict)
    }
    workflow = workflows.get(image_id)
    if workflow is None:
        raise CopyAllocationError(f"{unit['id']} baked-image owner references unknown image_workflow_id: {image_id}")
    text_policy = workflow.get("prompt_record", {}).get("text_policy")
    if text_policy != "baked-approved":
        raise CopyAllocationError(f"{unit['id']} baked-image text requires image_workflow text_policy baked-approved")
    declared_source = unit.get("declared_text_source", "")
    if declared_source not in {"ocr", "creator-declared"}:
        raise CopyAllocationError(f"{unit['id']} baked-image text requires declared_text_source ocr or creator-declared")


def _validate_locked_text(scaffold: Scaffold, module_id: str, text: str, unit_id: str) -> None:
    if f" {text} " not in f" {normalize_text(''.join(module_rows(scaffold, module_id)))} ":
        raise CopyAllocationError(f"{unit_id} text does not match its locked owner")


def _validate_allocation_links(allocation: dict, units: list[dict], exempted: set[str]) -> None:
    by_id = {unit["id"]: unit for unit in units}
    phrase_ids = [item["id"] for item in allocation.get("restricted_phrases", [])]
    if len(phrase_ids) != len(set(phrase_ids)) or set(phrase_ids) & set(by_id):
        raise CopyAllocationError("Restricted phrase IDs must be unique and distinct from content unit IDs")
    for key in exempted:
        if key in by_id or key in phrase_ids:
            continue
        pair = key.split("+")
        if len(pair) != 2 or pair[0] == pair[1] or any(item not in by_id for item in pair):
            raise CopyAllocationError(f"Unknown dedupe exemption target: {key}")
    seen = set()
    for item in allocation.get("slot_allocation", []):
        unit_id = item["content_unit_id"]
        if unit_id not in by_id:
            raise CopyAllocationError(f"Unknown slot_allocation content unit: {unit_id}")
        owner = by_id[unit_id]["owner"]
        if (item["module_id"], item["slot"], item["rendering_type"]) != (
            owner.get("module_id"), owner.get("slot"), owner["channel"]
        ):
            raise CopyAllocationError(f"Stale slot_allocation for {unit_id}")
        if unit_id in seen:
            raise CopyAllocationError(f"Duplicate slot_allocation for {unit_id}")
        seen.add(unit_id)


def _check_restricted_phrases(phrases: object, refs: list[CopyRef], exempted: set[str]) -> dict:
    if phrases is None:
        phrases = []
    if not isinstance(phrases, list):
        raise CopyAllocationError("copy_allocation.restricted_phrases must be an array")
    checks: list[dict] = []
    results: list[dict] = []
    corpus = [normalize_text(ref.text) for ref in refs]
    for index, item in enumerate(phrases):
        if not isinstance(item, dict):
            raise CopyAllocationError(f"copy_allocation.restricted_phrases[{index}] must be an object")
        phrase_id = _require_str(item, "id", f"copy_allocation.restricted_phrases[{index}]")
        phrase = normalize_text(_require_str(item, "phrase", f"copy_allocation.restricted_phrases[{index}]"))
        if not phrase:
            raise CopyAllocationError(f"{phrase_id} has no normalized restricted phrase")
        max_occurrences = item.get("max_occurrences", 1)
        if type(max_occurrences) is not int or max_occurrences < 1:
            raise CopyAllocationError(f"{phrase_id} max_occurrences must be a positive integer")
        count = sum(len(re.findall(r"(?<!\w)" + re.escape(phrase) + r"(?!\w)", text)) for text in corpus if phrase)
        if max_occurrences > 1 and phrase_id not in exempted:
            raise CopyAllocationError(f"{phrase_id} repeated restricted phrase requires a dedupe_exemption")
        passed = count <= max_occurrences
        checks.append(
            {
                "name": f"restricted-phrase:{phrase_id}",
                "passed": passed,
                "message": f"{count} occurrence(s), max {max_occurrences}: {phrase}",
            }
        )
        results.append({"id": phrase_id, "phrase": phrase, "occurrences": count, "max_occurrences": max_occurrences})
    return {"checks": checks, "phrases": results}


def _similarity_checks(units: list[dict], normalized_units: dict[str, str], exempted: set[str]) -> dict:
    checks: list[dict] = []
    pairs: list[dict] = []
    ids = [unit["id"] for unit in units]
    for left_index, left_id in enumerate(ids):
        for right_id in ids[left_index + 1 :]:
            left = normalized_units[left_id]
            right = normalized_units[right_id]
            if min(len(left.split()), len(right.split())) < 4:
                continue
            score = similarity_score(left, right)
            if score < NEAR_DUPLICATE_WARN_THRESHOLD:
                continue
            exempt = (left_id in exempted and right_id in exempted) or f"{left_id}+{right_id}" in exempted or f"{right_id}+{left_id}" in exempted
            blocking = score >= NEAR_DUPLICATE_BLOCK_THRESHOLD and not exempt
            passed = not blocking
            pairs.append({"left": left_id, "right": right_id, "score": round(score, 3), "blocking": blocking})
            checks.append(
                {
                    "name": f"copy-similarity:{left_id}:{right_id}",
                    "passed": passed,
                    "message": f"similarity {score:.3f}; warning >= {NEAR_DUPLICATE_WARN_THRESHOLD}, blocking >= {NEAR_DUPLICATE_BLOCK_THRESHOLD}",
                }
            )
    return {"checks": checks, "pairs": pairs}


def similarity_score(left: str, right: str) -> float:
    left_tokens = left.split()
    right_tokens = right.split()
    token_score = _jaccard(set(left_tokens), set(right_tokens))
    bigram_score = _jaccard(_ngrams(left_tokens, 2), _ngrams(right_tokens, 2))
    char_score = _jaccard(_char_ngrams(left, 4), _char_ngrams(right, 4))
    return max(token_score, (bigram_score + char_score) / 2)


def _normalized_occurrence_count(normalized_text: str, refs: list[CopyRef]) -> int:
    return sum(1 for ref in refs if normalize_text(ref.text) == normalized_text)


def _owner_key(owner: dict) -> str:
    return CopyRef(
        channel=owner.get("channel", ""),
        module_id=owner.get("module_id", ""),
        slot=owner.get("slot", ""),
        metadata_field=owner.get("metadata_field", ""),
        image_workflow_id=owner.get("image_workflow_id", ""),
        static_block_id=owner.get("static_block_id", ""),
    ).owner_key


def _exemption_keys(exemptions: object) -> set[str]:
    if exemptions is None:
        return set()
    if not isinstance(exemptions, list):
        raise CopyAllocationError("copy_allocation.dedupe_exemptions must be an array")
    keys: set[str] = set()
    exemption_ids: set[str] = set()
    for index, item in enumerate(exemptions):
        if not isinstance(item, dict):
            raise CopyAllocationError(f"copy_allocation.dedupe_exemptions[{index}] must be an object")
        exemption_id = _require_str(item, "id", f"copy_allocation.dedupe_exemptions[{index}]")
        if exemption_id in exemption_ids:
            raise CopyAllocationError(f"Duplicate dedupe exemption ID: {exemption_id}")
        exemption_ids.add(exemption_id)
        _require_str(item, "reason", f"copy_allocation.dedupe_exemptions[{index}]")
        _require_str(item, "scope", f"copy_allocation.dedupe_exemptions[{index}]")
        _require_str(item, "approved_by", f"copy_allocation.dedupe_exemptions[{index}]")
        _require_str(item, "approved_at", f"copy_allocation.dedupe_exemptions[{index}]")
        for key in _require_str_array(item, "applies_to", f"copy_allocation.dedupe_exemptions[{index}]"):
            keys.add(key)
    return keys


def _html_to_text(value: str) -> str:
    parser = _TextParser()
    parser.feed(value.replace("<br>", " <br> ").replace("<br/>", " <br/> ").replace("<br />", " <br /> "))
    parser.close()
    return " ".join(parser.parts)


class _TextParser(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.parts: list[str] = []

    def handle_data(self, data):
        if data.strip():
            self.parts.append(data)


def _jaccard(left: set, right: set) -> float:
    if not left or not right:
        return 0.0
    return len(left & right) / len(left | right)


def _ngrams(tokens: list[str], size: int) -> set[tuple[str, ...]]:
    if len(tokens) < size:
        return set()
    return {tuple(tokens[index : index + size]) for index in range(len(tokens) - size + 1)}


def _char_ngrams(text: str, size: int) -> set[str]:
    compact = text.replace(" ", "")
    if len(compact) < size:
        return set()
    return {compact[index : index + size] for index in range(len(compact) - size + 1)}


def _check(checks: list[dict], name: str, passed: bool, message: str) -> None:
    checks.append({"name": name, "passed": bool(passed), "message": message})


def _require_object(obj: dict, field: str, label: str) -> dict:
    value = obj.get(field)
    if not isinstance(value, dict):
        raise CopyAllocationError(f"{label}.{field} must be an object")
    return value


def _require_str(obj: dict, field: str, label: str) -> str:
    value = obj.get(field)
    if not isinstance(value, str) or not value:
        raise CopyAllocationError(f"{label}.{field} must be a non-empty string")
    return value


def _require_str_array(obj: dict, field: str, label: str) -> list[str]:
    value = obj.get(field)
    if not isinstance(value, list) or not all(isinstance(item, str) and item for item in value):
        raise CopyAllocationError(f"{label}.{field} must be an array of strings")
    return value
