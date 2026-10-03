---
name: onbrand-cassia-email
description: Explicitly invoked OnBrand cassia email workflow.
---

# onbrand-cassia-email

Run only after a HUMAN explicitly invokes $onbrand-cassia-email. Ordinary topic matches are not invocation.

Read [the canonical workflow](../../../projects/cassia/skills/onbrand-cassia-email/SKILL.md); resolve its references from its own folder. Do not copy project rules or approve inputs on behalf of the user.

The core repository is at `.` relative to this workspace. Run commands from that core root, using Python 3.10+ with the standard library.

For an approved campaign request file, use the shared dispatcher:

```bash
python3 -m tools.platform_adapters.cli build --platform codex --request <request.json> --output <output-folder> --explicit
```

Use `emit` instead of `build` to validate and emit canonical JSON without downloading assets. Image work follows the canonical image skill; this adapter does not provide an image generator. Do not invoke another skill automatically. If shell execution is unavailable, provide the same command for the human; never bypass QA or reconstruct a package manually.
