# Rider Composition Preview Catalog

Use these stable codes to select a Design Proof composition before image generation or final HTML assembly.

| Code | Type | Module | Header | Image | Slots | Notes |
|---|---|---|---|---|---|---|
| H-01 | header | TWO-COLUMN HEADER | standalone | no | headline, logo_link | Dark two-column standalone header with Rider logo and live text headline. |
| AI-01 | hero | AI GENERATED IMAGE BASED ON PROMPT | none | yes | hero_image | Image-led hero module for approved generated imagery. |
| B-01 | body | BODY - MASONRY LAYOUT | none | no | locked | Dark masonry-style editorial body content. |
| H-02 | header | ONE-COLUMN HEADER DARK | standalone | no | logo_link | Dark one-column standalone header with white Rider logo. |
| HR-01 | hero | HERO - LIVE TEXT HEADING - DARK FRAMED LAYOUT | none | yes | background_image, headline | Dark framed hero with editable live text heading and background art. |
| B-02 | body | BODY - LIGHT THEN DARK LAYOUT | none | no | locked | Light-to-dark editorial body module with image and CTA content. |
| H-03 | header | INVITE - TWO-COLUMN HEADER - COLLABORATION | standalone | no | locked | Invite collaboration header with Rider and partner logo placement. |
| B-03 | body | INVITE - DARK BODY | none | no | locked | Dark invite body module with supporting image and CTA content. |
| HH-01 | hero | HEADER & HERO - LIVE TEXT HEADING - FULL-WIDTH | includes | yes | background_image, headline, logo_link | Full-width hero that includes its own Rider header/logo. |
| H-04 | header | ONE-COLUMN HEADER LIGHT | standalone | no | logo_link | Light one-column standalone header with black Rider logo. |
| HR-02 | hero | HERO - LIVE TEXT HEADING - LIGHT LAYOUT - FRAMED | none | yes | background_image, headline | Light framed hero with editable live text heading and background art. |
| B-04 | body | BODY - DARK THEN LIGHT LAYOUT | none | yes | amenity_kicker, amenity_statement, anchor_line, anchor_name, arrival_image, gallery_image, list_item_1, list_item_2, list_item_3, primary_cta, section_1_copy, section_1_heading, section_2_copy, section_2_heading, section_3_copy, section_3_heading, section_4_copy, section_4_heading, section_label | Dark-to-light editorial body module; nested static blocks are locked and selected separately. |
| S-01 | static | STATIC BLOCK | none | no | locked | From the creators of The Bond on Brickell and JP Morgan Tower; Own Better brand lockup. |
| S-02 | static | STATIC BLOCK | none | no | locked | Curated design to please both your eyes and soul. |
| S-03 | static | STATIC BLOCK | none | no | locked | Limited edition furnished residences availability and price range. |
| S-04 | static | STATIC BLOCK | none | no | locked | Opportunity is knocking at your door. |

A standalone header cannot be selected with a hero whose header behavior is `includes`.
Every static block code must receive an include/exclude decision.
Open `hero-gallery.html` to choose a complete labeled `CFG-*` header/hero configuration.
