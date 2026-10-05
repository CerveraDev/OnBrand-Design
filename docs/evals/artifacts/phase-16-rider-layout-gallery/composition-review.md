# Rider Composition Preview Catalog

Use these stable codes to select a Design Proof composition before image generation or final HTML assembly.

| Code | Type | Module | Header | Image | Slots | Notes |
|---|---|---|---|---|---|---|
| H-01 | header | Two-Column Header, Dark | includes | no | headline, logo_link | Two-Column Header, Dark |
| AI-01 | hero | AI-Generated Image Hero | none | yes | hero_image | AI-Generated Image Hero |
| B-01 | body | Masonry Image Body | none | yes | image_1, image_2, image_3, image_4, image_5, image_6, image_7, image_8 | Masonry Image Body |
| H-02 | header | One-Column Header, Dark | includes | no | logo_link | One-Column Header, Dark |
| HR-01 | hero | Framed Live-Text Hero, Dark | none | yes | background_image, headline | Framed Live-Text Hero, Dark |
| H-03 | header | Invite Collaboration Header | includes | yes | collaborator_logo | Invite Collaboration Header |
| B-03 | body | Invite Body, Dark | none | yes | supporting_image | Invite Body, Dark |
| HH-01 | hero | Integrated Header and Full-Width Hero | includes | yes | background_image, headline, logo_link | Integrated Header and Full-Width Hero |
| H-04 | header | One-Column Header, Light | includes | no | logo_link | One-Column Header, Light |
| HR-02 | hero | Framed Live-Text Hero, Light | none | yes | background_image, headline | Framed Live-Text Hero, Light |
| B-04 | body | Long-Form Editorial Body | none | yes | amplified_list, body_copy_primary, body_copy_secondary, followup_list, inline_image_primary, leading_terms, list_eyebrow, list_payoff, subheading | Long-Form Editorial Body |
| S-01 | static | Developer Authority Static Block | none | no | locked | Developer Authority Static Block |
| S-02 | static | Curated Design Static Block | none | no | locked | Consider this block for wellness-related emails and invites when its sauna scene supports the campaign narrative. |
| I-02 | body | Between-Copy Image Block, Secondary | none | yes | image | Optional standalone image row placed between compatible long-form copy blocks; its scaffold placeholder must always be replaced. |
| C-01 | body | Highlighted Text Callout | none | no | callout_copy, footnote | Highlighted Text Callout |
| S-03 | body | Residence Specs, Semi-Static | none | no | price | Residence Specs, Semi-Static |
| S-04 | static | Opportunity Static Block | none | no | locked | Consider this block when the campaign narrative concerns arriving at, entering, visiting, or being welcomed to The Rider. |
| PF-01 | body | Closing CTA Pre-Footer | none | no | closing_cta_copy | Closing CTA Pre-Footer |

A standalone header cannot be selected with a hero whose header behavior is `includes`.
Every static block code must receive an include/exclude decision.
Open `hero-gallery.html` to choose a complete labeled `CFG-*` header/hero configuration.
Open `module-gallery.html` to inspect every selectable block in isolation.
For refined scaffolds, open `sequence-gallery.html` to review complete `SEQ-*` compositions.
