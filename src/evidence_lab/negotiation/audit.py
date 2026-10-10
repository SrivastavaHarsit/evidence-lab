"""Milestone 1: account for every CaSiNo record without repairing source data."""

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Literal

from evidence_lab.negotiation.casino import _mapping, _messages, parse_accepted
from evidence_lab.negotiation.schema import AcceptedDeal


@dataclass(frozen=True)
class RecordOutcome:
    record_index: int
    dialogue_id: int | None
    terminal: str | None
    status: Literal["accepted", "walkaway", "invalid"]
    deal: AcceptedDeal | None = None
    error: str | None = None


@dataclass(frozen=True)
class AuditResult:
    outcomes: list[RecordOutcome]

    # Input: this result's ordered outcomes.
    # Work: count every outcome, regardless of its status.
    # Output: the total number of source records.
    @property
    def total_records(self) -> int:
        return len(self.outcomes)

    # Input: the observed final text stored in each outcome.
    # Work: count Accept-Deal endings, including records that failed validation.
    # Output: the number of observed accepted endings, not the number of valid deals.
    @property
    def accepted_endings(self) -> int:
        return sum(outcome.terminal == "Accept-Deal" for outcome in self.outcomes)

    # Input: the deal fields stored in this result's outcomes.
    # Work: collect the checked deals that are present.
    # Output: a new list of existing AcceptedDeal objects; no parsing is repeated.
    @property
    def accepted_deals(self) -> list[AcceptedDeal]:
        return [outcome.deal for outcome in self.outcomes if outcome.deal is not None]

    # Input: this result's outcomes.
    # Work: select outcomes with status "walkaway".
    # Output: a new list of walkaway outcomes; these have no accepted deal.
    @property
    def walkaways(self) -> list[RecordOutcome]:
        return [outcome for outcome in self.outcomes if outcome.status == "walkaway"]

    # Input: this result's outcomes.
    # Work: select outcomes with status "invalid".
    # Output: a new list of invalid outcomes, retaining their error messages.
    @property
    def invalid_records(self) -> list[RecordOutcome]:
        return [outcome for outcome in self.outcomes if outcome.status == "invalid"]

    # Input: the status of every outcome.
    # Work: check whether any outcome is invalid.
    # Output: True when none are invalid, including an empty result; otherwise False.
    @property
    def ok(self) -> bool:
        return not any(outcome.status == "invalid" for outcome in self.outcomes)


# Input: one raw record and its zero-based list position (not its dialogue ID).
# Work: validate accepted deals with the parser; check walkaway IDs and messages.
# Output: one outcome; caught ValueError becomes an invalid result with a diagnostic.
def audit_record(raw: object, record_index: int) -> RecordOutcome:
    dialogue_id = None
    terminal = None

    try:
        raw = _mapping(raw, "dialogue")

        candidate_id = raw.get("dialogue_id")
        if type(candidate_id) is int and candidate_id >= 0:
            dialogue_id = candidate_id

        messages = raw.get("chat_logs")
        if not isinstance(messages, list) or not messages:
            raise ValueError("chat_logs must be a nonempty list")

        final_message = _mapping(messages[-1], "final chat_logs entry")
        final_text = final_message.get("text")
        if not isinstance(final_text, str):
            raise ValueError("final chat_logs entry must have a text string")
        terminal = final_text

        if terminal == "Accept-Deal":
            deal = parse_accepted(raw)

            return RecordOutcome(record_index, dialogue_id, terminal, "accepted", deal)

        if terminal == "Walk-Away":
            if dialogue_id is None:
                raise ValueError(
                    f"dialogue_id must be a nonnegative integer; got {candidate_id!r}"
                )
            _messages(raw)

            return RecordOutcome(record_index, dialogue_id, terminal, "walkaway")

        raise ValueError(f"Unexpected final event: {terminal!r}")
    except ValueError as error:
        return RecordOutcome(
            record_index, dialogue_id, terminal, "invalid", error=str(error)
        )


# Input: decoded JSON expected to be a list of raw records.
# Work: audit every position and keep one outcome, continuing after invalid records.
# Output: an ordered AuditResult; a non-list outer value raises ValueError.
def audit_records(records: list[object]) -> AuditResult:
    if not isinstance(records, list):
        raise ValueError("CaSiNo JSON must be a list of dialogues")

    outcomes = []

    for record_index, raw in enumerate(records):
        outcome = audit_record(raw, record_index)

        outcomes.append(outcome)

    return AuditResult(outcomes)


# Input: the Path of a local UTF-8 JSON file.
# Work: read and decode the file, then call audit_records.
# Output: an AuditResult, or a file error / ValueError for invalid input.
def load_audit(path: Path) -> AuditResult:
    try:
        records = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as error:
        raise ValueError(
            f"Cannot audit {path}: malformed JSON at line {error.lineno}, "
            f"column {error.colno}: {error.msg}"
        ) from error
    except UnicodeError as error:
        raise ValueError(f"Cannot audit {path}: file must be UTF-8 text") from error

    try:
        return audit_records(records)
    except ValueError as error:
        raise ValueError(f"Cannot audit {path}: {error}") from error
