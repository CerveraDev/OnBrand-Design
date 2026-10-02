# Templates

The Rider email skill uses the Beefree scaffold in `scaffold/`.

```text
scaffold/
├── rider-scaffolding.source.html
└── rider-scaffolding.canonical.html
```

- `rider-scaffolding.source.html` is the immutable provenance copy of the user-supplied Beefree export.
- `rider-scaffolding.canonical.html` is the runtime scaffold. It corrects `REQUEST MORE INFORMAITON`, corrects `ARTTS`, and renames the former unbranded footer markers as the outside-broker customizable footer.

Do not modify the source copy. Future runtime assembly should parse the canonical file structurally, compose validated row ranges, and exclude marker rows from generated emails.
