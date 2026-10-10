# Day-1 decisions

| Decision | Why | What would make us reconsider it |
| --- | --- | --- |
| One Python package with two small entry scripts | Keep the parser and score calculation together and easy to import; scripts only start the work. | A second real study demonstrates a different need. |
| uv is the only environment and dependency workflow | One lockfile and one set of commands locally and in CI. | A deployment environment cannot use uv. |
| Use Python 3.12 | A conservative Python series already available on this machine. | Support or a required dependency calls for an upgrade. |
| Do not commit the raw external dataset | Preserve source identity without putting a large external file into Git. | A justified, licensed archival requirement arises. |
| Separate the parser from plain Python records | Only the parser needs CaSiNo's raw field names; it validates data before returning immutable dataclasses. | A second source shows an actual shared parsing need. |
| Keep pytest examples offline | Small examples make errors easy to reproduce and understand. | Add a separate, explicitly requested integration check. |
| CI checks code and fixtures without fetching CaSiNo | Routine checks should not depend on an external dataset download. | A separately scheduled source audit becomes necessary. |

## Milestone 1

| Decision | Why | What would make us reconsider it |
| --- | --- | --- |
| Put complete-record accounting in `audit.py`; preserve parser and score behavior | The existing parser already validates accepted deals. Short Input/Work/Output function headers explain the reused behavior without changing executable logic. | A concrete shared parsing change becomes necessary. |
| Retain one `RecordOutcome` per file position | Every accepted deal, walkaway, and invalid record stays inspectable in source order. | Measured input size makes retaining the ledger impractical. |
| Derive selections and counts from one outcome list | Separate stored counters could disagree with the represented outcomes. | Repeated queries show a measured performance need. |
| Observe only the final message before calling the accepted parser | Preserve accepted-ending counts for invalid accepted records and avoid a second complete message scan. | A different terminal-event contract is introduced. |
| Collect expected `ValueError` failures; unexpected exceptions propagate | Bad source records remain visible while processing continues; programming failures are not disguised as ordinary invalid data. | An explicit internal-error accounting requirement is introduced. |
| Require a nonnegative integer dialogue ID for audited walkaways | Keep the outcome identity usable. This strengthens the audit contract relative to the original one-record selector, which remains unchanged. | A documented source variant lacks those identities. |
| Keep the existing shared helpers internal to the negotiation package | Reuse the same object/message checks without copying their implementation or adding another validation layer. | Another consumer needs a supported public helper API. |
| Add `check_all.py` as an observation script | Print reconciliation and diagnostics with exit codes, while leaving official saved outputs and reports to milestone 3. | We reach milestone 3. |
