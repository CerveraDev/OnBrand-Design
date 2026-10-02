# Agent Data

Use one JSON record per verified in-house __PROJECT_NAME__ agent.

- `agent.schema.json` defines the shared data shape.
- `index.json` defines active agents and deterministic output order.
- `template.example.json` is a neutral example for future records and is not an active agent.

JSON owns verified agent data and stable asset references only. HTML owns markup, styling, legal text, project branding, and footer structure. Do not store secrets, credentials, inferred facts, or campaign copy in agent records.

Resolve `headshot.asset_id` through the project's validated master manifest. Require the project's agent-footer approval label, expected headshot media type, and configured agent-assets path before rendering or packaging it.
