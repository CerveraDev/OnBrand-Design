# Calibration From Supplied HTML

Use this workflow when the user provides the Beefree-generated __PROJECT_NAME__ HTML sample.

## Analyze

Extract:

- Color palette
- Font stack and typography scale
- Container width
- Section rhythm and spacing
- Hero structure
- Image handling
- Button markup
- Footer boundary
- Responsive behavior
- Outlook-specific or conditional markup
- Reusable row/module patterns

## Update References

Update:

- `brand.md`
- `email-design-system.md`
- `beefree-html-structure.md`
- `html-email.md`
- `modules.md`, if the sample reveals concrete module structures
- `footers.md`, if footer partial boundaries are provided

## Preserve Source Truth

Do not overwrite the supplied sample. Save it as:

```text
templates/master-email.html
```

If multiple samples are supplied, keep meaningful names and document which sample is canonical.
