# Footers

Footer HTML is locked by default. Do not rewrite, restyle, or reinterpret footer partials unless the user explicitly requests it.

## Footer Types

1. Branded Rider Residences footer
2. Broker-neutral outside-agent footer
3. Individual in-house agent footers

## Broker-Neutral Definition

Broker-neutral does not mean removing Rider project identity from the entire email.

It means removing sales attribution and direct contact ownership that would prevent an outside broker from using the email as their own marketing piece, including:

- Phone numbers
- Email addresses
- Web addresses
- Sales team logos
- Agent details
- Any direct routing to an in-house sales team

## Expected Footer Files

Place final footer partials here when available:

```text
assets/footers/
├── branded-footer.html
├── broker-neutral-footer.html
└── agents/
    ├── agent-01-footer.html
    ├── agent-02-footer.html
    ├── agent-03-footer.html
    ├── agent-04-footer.html
    ├── agent-05-footer.html
    └── agent-06-footer.html
```

Agent filenames may be renamed to actual agent names once the team list is supplied.

## Default Variant Set

Unless the user says otherwise, deliver:

- Branded version
- Broker-neutral outside-agent version
- One version per available in-house agent footer

The email body should remain consistent across variants unless the user requests body-level differences.
