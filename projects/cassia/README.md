# OnBrand Design: Cassia

Project-specific OnBrand Design scaffold for Cassia, used with the shared core.

## Skills

- `$onbrand-cassia-email`: campaign strategy, copy, asset selection, HTML variants, packaging, and QA.
- `$onbrand-cassia-image`: separately invoked image-generation and editing workflow.

Both skills are explicit-only. Brand, template, footer, and asset rules remain provisional until calibrated from approved Cassia materials.

## Download Boundary

Keep this folder with the shared core. `adapter.json` declares a null runtime: [workspace wrappers](../../docs/COMPATIBILITY.md) provide references but reject campaign builds until Cassia is calibrated and implemented. Do not include private `.env` files, credentials, or unapproved assets. Phase 12 restricted distribution stays deferred.

Campaign generation should use Cassia's configured public manifest and approved public asset URLs. Dropbox app credentials belong only in the framework maintainer's ignored `tools/dropbox-manifest/.env` and must not be copied into this package.

## License And Attribution

The OnBrand Design source framework in this package is licensed under Apache-2.0. Retain `LICENSE`, `NOTICE`, `AUTHORS.md`, and `THIRD_PARTY_NOTICES.md` when redistributing it. Cassia logos, photographs, renderings, templates, and campaign assets may be subject to separate rights.
