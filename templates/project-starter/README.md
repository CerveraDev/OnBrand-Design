# OnBrand Design: __PROJECT_NAME__

Project-specific OnBrand Design pack for __PROJECT_NAME__, used with the shared core.

## Skills

- `$onbrand-__PROJECT_SLUG__-email`: campaign strategy, copy, asset selection, HTML variants, packaging, and QA.
- `$onbrand-__PROJECT_SLUG__-image`: separately invoked image-generation and editing workflow.

Both skills are explicit-only. Brand, template, footer, and asset rules remain provisional until calibrated from approved __PROJECT_NAME__ materials.

## Download Boundary

Keep this project folder with the shared core; it is not a standalone runtime. `adapter.json` declares a null runtime until project implementation/calibration is complete. Use the core's `tools.platform_adapters.cli install` with this project's slug for explicit-only workspace wrappers. Do not include private `.env` files, credentials, or unapproved assets. Phase 12 restricted distribution stays deferred.

Campaign generation should use the project's configured public manifest and approved public asset URLs. Dropbox app credentials belong only in the framework maintainer's ignored `tools/dropbox-manifest/.env` and must not be copied into this package.

## License And Attribution

The OnBrand Design source framework in this package is licensed under Apache-2.0. Retain `LICENSE`, `NOTICE`, `AUTHORS.md`, and `THIRD_PARTY_NOTICES.md` when redistributing it. Project logos, photographs, renderings, templates, and campaign assets may be subject to separate rights.
