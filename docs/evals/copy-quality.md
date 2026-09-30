# Copy-Quality Evaluation Cases

Use these cases to evaluate decisions, not exact wording. A passing result protects facts and project voice while removing generic or unsupported copy.

## Case 1: Interchangeable Luxury Copy

Input:

> Discover a stunning new standard of elevated living in a vibrant destination where sophistication meets unparalleled comfort.

Expected behavior:

- Flag the copy as portable to nearly any development.
- Ask for or use approved project details rather than swapping in different adjectives.
- Do not invent amenities, location advantages, or design claims.

## Case 2: Approved Watchlist Term

Input context: The approved brand guide uses `elevated waterfront living` as a defined positioning line.

Expected behavior:

- Preserve the approved line unless the user asks to reconsider brand language.
- Avoid repeating `elevated` decoratively elsewhere.
- Do not treat a generic watchlist as stronger than supplied brand guidance.

## Case 3: Unsupported Urgency

Input:

> This is your final opportunity to secure one of the last remaining residences.

Expected behavior:

- Require supplied availability and deadline evidence.
- Remove or flag the statement when evidence is absent.
- Do not soften it into another unsupported scarcity claim.

## Case 4: Subject And Preview Duplication

Input:

- Subject: Tour the new model residence
- Preview: Tour the new model residence today

Expected behavior:

- Keep the subject if it fits the campaign.
- Revise preview text to add a supported detail or next step.
- Keep subject, preview, headline, and CTA aligned to one action.

## Case 5: Audit Without Rewrite

Input request: `Audit this copy, but do not rewrite it.`

Expected behavior:

- Quote each material passage, name the pattern or risk, explain its campaign impact, and suggest a correction direction.
- Do not return a detector score or claim to know whether AI wrote it.
- Do not provide a full rewritten draft.

## Case 6: Voice Preservation

Input context: A supplied draft is concise, slightly conversational, factually supported, and intentionally uses one sentence fragment as a headline.

Expected behavior:

- Preserve the useful fragment and recognizable cadence.
- Make only edits that improve clarity, accuracy, or campaign performance.
- Do not normalize every sentence or paragraph into the same polished structure.
