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

The active index contains six user-verified agents: Jake Lecce, Angelica Cruz, Julian Oliveros, Omar Santana, Pablo Rodriguez, and Yessika Arevalo. Each record references its approved Dropbox headshot through a canonical manifest `dropbox_id`; it does not store a direct URL.

Resolve each headshot through the validated manifest and require the `agent-footer` approval plus the `/20. People/In-house Agents/` path boundary. Assets under `/20. People/Diego Ojeda/` are likeness references for the separate image-generation workflow and must never qualify for footer rendering.

## Default Variant Set

Unless the user says otherwise, deliver:

- Branded version.
- Outside-broker customizable version.
- One version per active in-house agent record.

The email body should remain consistent across variants unless the user requests body-level differences.
