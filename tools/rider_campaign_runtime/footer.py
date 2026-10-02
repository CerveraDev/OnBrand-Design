from __future__ import annotations

from .slots import SlotError, UsedAsset, replace_once, rewrite_img_by_src, safe_text


OUTSIDE_PLACEHOLDERS = {
    "name": "[OUTSIDE BROKER NAME]",
    "title": "[OUTSIDE BROKER TITLE]",
    "phone": "[OUTSIDE BROKER PHONE]",
    "email": "[OUTSIDE BROKER EMAIL]",
    "social": "[OUTSIDE BROKER SOCIAL]",
}
OUTSIDE_HEADSHOT_SRC = "https://media.beefree.cloud/pub/bfra/9dgc1zff/2k1/mfd/p35/generic-headshot.jpg"
AGENT_HEADSHOT_SRC = "https://media.beefree.cloud/pub/bfra/9dgc1zff/n1i/jvw/hkq/jake-lecce-hero.jpg"


def render_branded_footer(rows: list[str]) -> tuple[list[str], list[UsedAsset]]:
    return rows, []


def render_outside_broker_footer(rows: list[str], outside: dict, manifest_assets: dict[str, dict]) -> tuple[list[str], list[UsedAsset]]:
    rendered = list(rows)
    row = rendered[3]
    fields = {key: safe_text(outside.get(key) or value) for key, value in OUTSIDE_PLACEHOLDERS.items()}
    row = replace_once(row, "OUTSIDE BROKER NAME", fields["name"], "outside_broker.name")
    row = replace_once(row, "OUTSIDE BROKER TITLE", fields["title"], "outside_broker.title")
    row = replace_once(row, "305 XXX XXXX", fields["phone"], "outside_broker.phone")
    row = replace_once(row, "NAME@BROKERAHE.COM", fields["email"], "outside_broker.email")
    row = replace_once(row, "@SocialHandle", fields["social"], "outside_broker.social")

    used: list[UsedAsset] = []
    headshot = outside.get("headshot")
    if headshot:
        if "asset_id" in headshot:
            asset_id = headshot["asset_id"]
            if asset_id not in manifest_assets:
                raise SlotError(f"outside_broker.headshot asset_id is not in manifest: {asset_id}")
            asset = manifest_assets[asset_id]
            if asset.get("media_type") != "image":
                raise SlotError(f"outside_broker.headshot asset_id is not an image: {asset_id}")
            if "agent-footer" not in {item.lower() for item in asset.get("approved_for", [])}:
                raise SlotError(f"outside_broker.headshot asset_id is not approved for agent-footer: {asset_id}")
            src = asset["public_url"]
            used.append(
                UsedAsset(
                    source=src,
                    role="outside-broker-headshot",
                    identity=asset["dropbox_id"],
                    filename=asset["filename"],
                    dropbox_path=asset["dropbox_path"],
                )
            )
        else:
            src = headshot["src"]
            used.append(UsedAsset(source=src, role="outside-broker-headshot"))
        row = rewrite_img_by_src(
            row,
            OUTSIDE_HEADSHOT_SRC,
            new_src=src,
            alt=headshot.get("alt", outside.get("name", "Outside broker headshot")),
            title=headshot.get("title", headshot.get("alt", outside.get("name", "Outside broker headshot"))),
            label="outside_broker.headshot",
        )
    else:
        used.append(UsedAsset(source=OUTSIDE_HEADSHOT_SRC, role="outside-broker-placeholder-headshot"))
        row = rewrite_img_by_src(
            row,
            OUTSIDE_HEADSHOT_SRC,
            new_src=OUTSIDE_HEADSHOT_SRC,
            alt="Outside broker headshot placeholder",
            title="Outside broker headshot placeholder",
            label="outside_broker.headshot.placeholder",
        )
    rendered[3] = row
    return rendered, used


def render_agent_footer(rows: list[str], agent: dict) -> tuple[list[str], list[UsedAsset]]:
    rendered = list(rows)
    row = rendered[3]
    asset = agent["headshot"]["asset"]
    row = rewrite_img_by_src(
        row,
        AGENT_HEADSHOT_SRC,
        new_src=asset["public_url"],
        alt=agent["headshot"]["alt"],
        title=agent["headshot"]["alt"],
        label=f"agent.{agent['id']}.headshot",
    )
    row = replace_once(row, "JAKE LECCE", safe_text(agent["display_name"].upper()), f"agent.{agent['id']}.name")
    row = replace_once(row, "SALES DIRECTOR", safe_text(agent["title"].upper()), f"agent.{agent['id']}.title")
    row = replace_once(row, "305 432 9969", safe_text(agent["phone"]), f"agent.{agent['id']}.phone")
    row = replace_once(row, "JAKE@THERIDERRESIDENCES.COM", safe_text(agent["email"].upper()), f"agent.{agent['id']}.email")
    rendered[3] = row
    return rendered, [
        UsedAsset(
            source=asset["public_url"],
            role="agent-footer-headshot",
            identity=asset["dropbox_id"],
            filename=asset["filename"],
            dropbox_path=asset["dropbox_path"],
        )
    ]
