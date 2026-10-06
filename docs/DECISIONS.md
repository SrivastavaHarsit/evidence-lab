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
