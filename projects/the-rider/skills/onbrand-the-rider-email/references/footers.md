# Footers

Footer HTML is scaffold-owned by default. Do not rewrite, restyle, or reinterpret footer modules unless the user explicitly requests it.

## Footer Types

1. Branded Rider footer: content rows 62-69.
2. Outside-broker customizable footer: content rows 72-79.
3. In-house agent footer: content rows 82-89.

The paired marker rows identify module boundaries but must never ship in generated emails.

## Outside-Broker Customizable Definition

The former "unbranded footer" is now the outside-broker customizable footer.

This footer is not a contact-free broker-neutral footer and does not remove Rider project identity, developer branding, Equal Housing Opportunity marks, pricing language, legal copy, or required disclaimers. It provides a personalization area for a non-in-house broker:

- Headshot
- Name
- Title
- Phone
- Email

If outside-broker data is not supplied, keep clear placeholders rather than inventing contact details.

## In-House Agent Data

Use one JSON record per in-house agent in `data/agents/`. The shared schema is `data/agents/agent.schema.json`, and `data/agents/index.json` defines active agents and deterministic output order.

Current factual record:

- `jake-lecce.json`: Jake Lecce, Sales Director, `305 432 9969`, `jake@theriderresidences.com`, and the Beefree-hosted Jake headshot from the scaffold.

Do not fabricate additional agents. Add future agents only from verified source material.

## Default Variant Set

Unless the user says otherwise, deliver:

- Branded version.
- Outside-broker customizable version.
- One version per active in-house agent record.

The email body should remain consistent across variants unless the user requests body-level differences.
