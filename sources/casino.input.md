# CaSiNo input contract — accepted parser and milestone-1 audit

A contract describes the shape and meaning of data a function expects.
This document describes the fields our parser and audit consume, not every field
in the complete CaSiNo release. It is documentation, not an executable validator.
The source identity is in [casino.manifest.json](casino.manifest.json).

```text
casino.json                         Original input, including chat_logs
    ↓ json.loads()
list of Python dictionaries
    ↓ load_first_accepted() selects one dictionary
parse_accepted(raw)                 Checks and translates the raw fields
    ↓
AcceptedDeal                        Output type defined in schema.py
```

`schema.py` defines the output structure. It does not define the input JSON.
`casino.py` reads and validates the input described here.

## Required shape for an accepted record

The entire file must contain a JSON array (a Python `list` after loading).
Each selected accepted record is a JSON object (a Python `dict`):

```text
raw: dictionary
├── dialogue_id: integer, at least 0; booleans are rejected
├── chat_logs: nonempty list of message dictionaries
│   ├── earlier messages, if present
│   │   └── text: string
│   ├── second-last message: submission
│   │   ├── text: "Submit-Deal"
│   │   ├── id: "mturk_agent_1" or "mturk_agent_2"
│   │   └── task_data: dictionary
│   │       ├── issue2youget: resource-quantity dictionary
│   │       └── issue2theyget: resource-quantity dictionary
│   └── last message: acceptance
│       ├── text: "Accept-Deal"
│       └── id: the other participant's ID
└── participant_info: dictionary with exactly the two participant keys
    ├── mturk_agent_1: participant-information dictionary
    └── mturk_agent_2: participant-information dictionary
```

Every resource-quantity dictionary has exactly these keys:

```text
Food:     whole-number quantity from 0 to 3
Water:    whole-number quantity from 0 to 3
Firewood: whole-number quantity from 0 to 3
```

The pinned source stores these quantities as strings, such as `"2"`. The parser
accepts integers or strings consisting of ASCII decimal digits, converts strings
to integers, and checks the range. It rejects `None`, booleans, floats, negative
values, and values above 3. It does not trim whitespace; leading zeros are allowed.

Every participant-information dictionary contains:

```text
value2issue: dictionary with exactly these priority keys
├── High:   one of "Food", "Water", "Firewood"
├── Medium: one of "Food", "Water", "Firewood"
└── Low:    one of "Food", "Water", "Firewood"

outcomes: dictionary
└── points_scored: whole-number score from 0 to 36
```

Each resource must appear exactly once in a participant's preferences.
High, Medium, and Low become 5, 4, and 3 points per unit, respectively.
The recorded score accepts integers or ASCII decimal strings under the same
conversion rule as quantities, with a maximum of 36.

## Relationships that must also hold

- The final acceptance immediately follows a submission by the other participant.
- `issue2youget` belongs to the submission's `id`, whichever participant proposed.
- `issue2theyget` belongs to the other participant.
- For each resource, the two quantities must sum to exactly 3.
- Each participant's reconstructed score must equal their recorded score.

These are checks on meaning as well as types. Correct field names alone are not
enough to establish a valid record.

## What each function guarantees

| Function | Input → output | Checks |
| --- | --- | --- |
| `load_first_accepted(path)` | Local `Path` → `AcceptedDeal` | Loads an outer list; selects the first record ending in `Accept-Deal`; passes it to the parser. |
| `_messages(raw)` | Dictionary → `list[dict[str, Any]]` | `chat_logs` is a nonempty list; every entry is a dictionary with a string `text`. It does not validate `id` or `task_data`. |
| `parse_accepted(raw)` | One dictionary → `AcceptedDeal` | Checks the required fields and relationships above, then builds and verifies the output. |

`dict[str, Any]` is a broad Python type hint: it does not declare which keys are
required. The checks in `casino.py` enforce the requirements at runtime.

Walkaways are passed over during selection after checking their message-list
shape and final `"Walk-Away"` text. Their allocations and participant information
are not validated. Unknown final events and invalid encountered accepted records
raise errors. Records after the selected deal are not checked.

## Milestone-1 complete audit

`load_audit(path)` in `audit.py` reads an outer JSON list and calls
`audit_records(records)`. The latter visits every position and delegates each raw
value to `audit_record(raw, record_index)`. Each result is exactly one of:

- `accepted`: the unchanged `parse_accepted()` returned a checked `AcceptedDeal`.
- `walkaway`: a dictionary has a nonnegative integer `dialogue_id` (not a bool),
  every message has the shape required by `_messages()`, and the final text is
  `"Walk-Away"`. Its participant information, sender IDs, allocations, and scores
  are not validated; its outcome has no deal or score.
- `invalid`: the record failed validation or has an unknown final event. Its
  outcome retains the zero-based file position, valid ID when available, observed
  final text when available, and the failure reason. Later records are visited.

The audit's ID requirement for walkaways is stronger than the original
`load_first_accepted()` selector's requirement. That selector is unchanged.
IDs that are missing or invalid become `None` in outcome metadata; they do not
prevent the file position and validation reason from being preserved.

The audit observes only the final message before accepted parsing. The strict
parser checks the complete accepted message list once, so an invalid earlier
message with a final `"Accept-Deal"` counts as an accepted ending and an invalid
record. An accepted ending is not proof of a valid deal.

`AuditResult.outcomes` preserves source order. Checked deals, walkaway outcomes,
invalid outcomes, counts, and `ok` are derived from it. Total records reconcile
with valid accepted deals + walkaways + invalid records. An empty outer list is
a clean audit of zero records. This does not establish an accepted study cohort.

Invalid JSON, invalid UTF-8, and a non-list outer value produce contextual
file-level errors without fabricated accounting. File read failures propagate.
The script displays these as input errors. Unexpected programming exceptions
are not converted into ordinary invalid-record outcomes.

Extra fields are ignored except where exact keys are required above. In
particular, acceptance `task_data`, ordinary-message IDs, demographics, and
annotations are not validated by this accepted parser. Neither loader checks
the local file's checksum; the download script does that during acquisition.

For a concrete example, open
[casino_dialogue_0.json](../tests/fixtures/casino_dialogue_0.json).
That fixture contains one record object; the complete source file wraps records
in an outer array. Its [fixture notes](../tests/fixtures/README.md) explain its
origin and omitted fields.
