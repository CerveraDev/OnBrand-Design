"""Type-sensitive JSON value comparison and matching semantic hashes."""

import json
import math


def normalize_json(value):
    kind = type(value)
    if value is None or kind in (bool, str, int):
        return value
    if kind is float:
        if not math.isfinite(value):
            raise ValueError("Non-finite numbers are not JSON values")
        # JSON has one number type; integral floats (including negative zero)
        # share the exact parsed numeric value and representation of integers.
        return int(value) if value.is_integer() else value
    if kind is list:
        return [normalize_json(item) for item in value]
    if kind is dict:
        if any(type(key) is not str for key in value):
            raise ValueError("JSON object keys must be strings")
        return {key: normalize_json(item) for key, item in value.items()}
    raise ValueError(f"Unsupported JSON value type: {kind.__name__}")


def json_semantic_bytes(value):
    return (json.dumps(normalize_json(value), sort_keys=True, ensure_ascii=False,
                       allow_nan=False, indent=2) + "\n").encode("utf-8")


def json_semantic_equal(left, right):
    return json_semantic_bytes(left) == json_semantic_bytes(right)
