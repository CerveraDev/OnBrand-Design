# Agent Data

Use one JSON record per verified in-house Rider agent.

```text
agent.schema.json
index.json
<agent-id>.json
template.example.json
archived/<former-agent-id>.json
```

- `agent.schema.json` defines the shared data shape.
- `index.json` defines active agents and deterministic output order.
- Each active `<agent-id>.json` contains user-verified contact data and a canonical manifest `dropbox_id` for the approved headshot.
- `template.example.json` is a neutral example for future records and is not an active agent.
- `archived/` preserves historical records that must never generate current campaign variants.

JSON owns verified agent data and stable asset references only. HTML owns markup, styling, legal text, developer branding, and footer structure. Do not store secrets, credentials, inferred facts, or campaign copy in agent records.

Paulie Hankin has a user-confirmed factual correction: Paulie is a woman. The current footer data model does not store gender or pronouns, so this note preserves the correction without adding inferred fields.

Resolve `headshot.asset_id` through the validated master manifest. The resolved record must be an image under `/20. People/In-house Agents/` and include `agent-footer` in `approved_for`. Never substitute an image by filename alone.
