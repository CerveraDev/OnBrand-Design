# OnBrand Design: The Rider

Self-contained OnBrand Design implementation for The Rider.

## Skills

- `$onbrand-the-rider-email`: campaign strategy, copy, asset selection, HTML variants, packaging, and QA.
- `$onbrand-the-rider-image`: separately invoked image-generation and editing workflow.

Both skills are explicit-only. The Rider email scaffold is calibrated from the supplied Beefree export. Runtime HTML assembly, campaign packaging, build modes, Composition Preview approval, grounded generated-image provenance, and blocking package QA are implemented for Rider pilot campaigns.

## Download Boundary

Distribute this entire `the-rider/` folder when sharing the project-specific implementation. Do not include private `.env` files or Dropbox credentials.

Campaign generation should use The Rider's configured manifest source and approved public asset URLs. No stable public manifest URL is configured yet; the current supported path is the validated local-cache fallback recorded in `manifest-source.json`. Dropbox app credentials belong only in the framework maintainer's ignored `tools/dropbox-manifest/.env` and must not be copied into this package.

## License And Attribution

The OnBrand Design source framework in this package is licensed under Apache-2.0. Retain `LICENSE`, `NOTICE`, `AUTHORS.md`, and `THIRD_PARTY_NOTICES.md` when redistributing it. Rider logos, photographs, renderings, templates, and campaign assets may be subject to separate rights.
