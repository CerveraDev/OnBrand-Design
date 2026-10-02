# Footers

Footer HTML is locked by default. Do not rewrite, restyle, or reinterpret footer partials unless the user explicitly requests it.

## Footer Types

1. Branded __PROJECT_NAME__ footer
2. Outside-broker customizable footer
3. Individual in-house agent footers

## Outside-Broker Customizable Definition

Outside-broker customizable does not mean removing __PROJECT_NAME__ project identity from the entire email.

It means replacing in-house contact ownership with supplied outside-broker personalization or clear placeholders, including:

- Headshot
- Name
- Title
- Phone
- Email

Preserve project branding and required legal content unless a project-specific approved footer says otherwise.

## Expected Footer Files

Place final footer partials here when available:

```text
assets/footers/
├── branded-footer.html
├── outside-broker-customizable-footer.html
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
- Outside-broker customizable version
- One version per available in-house agent footer

The email body should remain consistent across variants unless the user requests body-level differences.
