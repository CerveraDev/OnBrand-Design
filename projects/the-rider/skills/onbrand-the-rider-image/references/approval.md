# Approval Workflow

Generated or edited imagery should be approved before final email HTML is built.

## Candidate Output

Return:

- Candidate images or image descriptions
- The base image used
- The generation/edit prompt
- Notes about what changed
- Any uncertainty or risk
- The proposed `image_workflow` record fields needed by the email runtime, including source assets, output checksum/dimensions, placement constraints, and approval metadata

## Approval Questions

Ask the user to choose, revise, or reject candidates. Do not proceed to final email assembly until the selected visual direction is clear.

Only an approved candidate may be handed back for runtime assembly. Candidate or rejected images can be discussed, but they must not be referenced by a campaign image slot.
