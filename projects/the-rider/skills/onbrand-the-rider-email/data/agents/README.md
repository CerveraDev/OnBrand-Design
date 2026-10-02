# Agent Data

Use one JSON record per verified in-house Rider agent.

```text
agent.schema.json
index.json
jake-lecce.json
template.example.json
```

- `agent.schema.json` defines the shared data shape.
- `index.json` defines active agents and deterministic output order.
- `jake-lecce.json` contains only facts present in the canonical scaffold.
- `template.example.json` is a neutral example for future records and is not an active agent.

JSON owns verified agent data and stable asset references only. HTML owns markup, styling, legal text, developer branding, and footer structure. Do not store secrets, credentials, inferred facts, or campaign copy in agent records.
