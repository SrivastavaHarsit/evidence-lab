# Status

- **Current study:** E000 — among accepted negotiations, how often could another
  feasible allocation improve at least one assigned score without reducing the
  other's? Milestone 1 (complete record accounting) is implemented.
- **Verified on 10 October 2026:** The original dataset still matches its manifest
  SHA256 and 4,300,019-byte size. The full audit visits all **1,030 records**:
  **1,005 accepted endings, 1,005 valid accepted deals, 25 walkaways, 0 invalid**.
  Allocation conservation and both reconstructed scores pass the existing parser
  for every accepted deal. Accounting reconciles: **1,030 = 1,005 + 25 + 0**.
- **Checks:** All **61 offline tests** and both Ruff checks pass. The intentional
  four-record example reports **4 = 2 valid accepted + 1 walkaway + 1 invalid**,
  keeps the later valid deal, and returns FAIL with the bad score diagnostic.
- **Comments:** Short Input / Work / Output headers sit above functions and
  properties. Teaching comments inside function bodies have been removed;
  parser, scoring, and audit behavior are unchanged.
- **Archived study material:** [Offline HTML study guide](MILESTONE_1_WALKTHROUGH.html),
  with 39 zoomable flowcharts, 41 source-linked code excerpts, and seven embedded
  source/configuration/fixture files. Copy this single file to a second device.
  These guides capture the 8 October annotated source, before comment cleanup.
  Their line numbers and embedded source reflect that earlier layout; find the
  quoted statements in current files when placing breakpoints.
  The [Markdown version](MILESTONE_1_WALKTHROUGH.md) contains the same lesson:
  flowcharts and line-by-line reading before debugger and fixture exercises.
  Offline Chrome checks pass for desktop, tablet, and phone layouts, search,
  source links, code copying, zoom/fullscreen, checkpoints, reading-position
  recovery, and print export. The lesson remains readable with JavaScript disabled.
  [MILESTONE_1.md](MILESTONE_1.md) remains a shorter reference.
  The original one-record checker still returns dialogue 0 with scores 19 and 18.
- **Scope:** Accepted records use the unchanged strict parser. Walkaways require
  a valid dialogue ID and message-list shape; no deal or score is constructed.
  Unused source fields are not checked. Full JSON is loaded into memory.
- **Debugger verification of the 8 October snapshot:** The installed adapter
  verified all 22 walkthrough
  breakpoint anchors at 75 stops (61 distinct variable observations), including
  both proposer orientations, resource totals, scores, the invalid diagnostic,
  the walkaway, and final counts. Expected small-example exit code: 1. This checks
  the adapter, not VS Code UI interaction.
- **Walkthrough experiments:** All five planned changes were independently
  verified on temporary fixture copies: correct the bad score, add a malformed
  earlier message, exceed a resource total, use an unknown ending, and break the
  outer JSON. Their predicted accounting and exit statuses match the actual runs.
- **Remaining milestone-1 implementation work:** None identified after checks.
  Milestone 1 is complete and ready for the next study stage.
- **Next study stage, when requested:** Milestone 2, exact Pareto dominance.
  Reproducible saved results, run information, and a report remain milestone 3.
