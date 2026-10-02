from __future__ import annotations

import json
import re
from pathlib import Path

from tools.asset_selection import ManifestError, resolve_manifest_asset


class AgentError(ValueError):
    """Raised when Rider agent data is not valid for runtime rendering."""


EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")
ID_RE = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
AGENT_FIELDS = {"id", "display_name", "title", "phone", "email", "headshot"}


def load_agents(agents_dir: Path, assets: list[dict], requested) -> list[dict]:
    index = json.loads((agents_dir / "index.json").read_text(encoding="utf-8"))
    active = index.get("active_agent_ids")
    order = index.get("output_order")
    if not isinstance(active, list) or not isinstance(order, list):
        raise AgentError("Agent index must contain active_agent_ids and output_order arrays")
    if any(not isinstance(item, str) for item in active + order):
        raise AgentError("Agent index arrays must contain only strings")
    active_set = set(active)
    if not set(order).issubset(active_set):
        raise AgentError("Agent output_order must be a subset of active_agent_ids")

    selected_ids = order if requested == "all" else requested
    unknown = sorted(set(selected_ids) - active_set)
    if unknown:
        raise AgentError("Requested inactive or unknown agent(s): " + ", ".join(unknown))

    agents = []
    for agent_id in selected_ids:
        path = agents_dir / f"{agent_id}.json"
        if not path.exists():
            raise AgentError(f"Agent record is missing: {agent_id}")
        agent = json.loads(path.read_text(encoding="utf-8"))
        validate_agent(agent, path.name)
        asset = resolve_manifest_asset(
            assets,
            agent["headshot"]["asset_id"],
            media_type="image",
            required_approval="agent-footer",
            required_path_prefix="/20. People/In-house Agents",
        )
        agent = dict(agent)
        agent["headshot"] = dict(agent["headshot"])
        agent["headshot"]["asset"] = asset
        agents.append(agent)
    return agents


def validate_agent(agent: object, label: str) -> None:
    if not isinstance(agent, dict):
        raise AgentError(f"{label} must be a JSON object")
    unknown = sorted(set(agent) - AGENT_FIELDS)
    if unknown:
        raise AgentError(f"{label} has unknown field(s): {', '.join(unknown)}")
    missing = sorted(AGENT_FIELDS - set(agent))
    if missing:
        raise AgentError(f"{label} is missing field(s): {', '.join(missing)}")
    if not isinstance(agent["id"], str) or not ID_RE.match(agent["id"]):
        raise AgentError(f"{label} has invalid id")
    for field in ("display_name", "title", "phone", "email"):
        if not isinstance(agent[field], str) or not agent[field]:
            raise AgentError(f"{label}.{field} must be a non-empty string")
    if not EMAIL_RE.match(agent["email"]):
        raise AgentError(f"{label}.email is invalid")
    headshot = agent["headshot"]
    if not isinstance(headshot, dict) or set(headshot) != {"asset_id", "alt"}:
        raise AgentError(f"{label}.headshot must contain only asset_id and alt")
    if not isinstance(headshot["asset_id"], str) or not headshot["asset_id"].startswith("id:"):
        raise AgentError(f"{label}.headshot.asset_id must start with id:")
    if not isinstance(headshot["alt"], str):
        raise AgentError(f"{label}.headshot.alt must be a string")
