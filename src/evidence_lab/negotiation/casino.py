"""Parse CaSiNo input (contract: sources/casino.input.md) into a checked deal."""

import json
from pathlib import Path
from typing import Any

from evidence_lab.negotiation.schema import (
    AcceptedDeal,
    Participant,
    Resources,
    verify_scores,
)

PARTICIPANT_IDS = ("mturk_agent_1", "mturk_agent_2")
ISSUES = ("Food", "Water", "Firewood")
UNITS_PER_RESOURCE = 3  # Total available to split between both participants.
# CaSiNo paper, section 2: High / Medium / Low are worth 5 / 4 / 3 per unit.
POINTS = {"High": 5, "Medium": 4, "Low": 3}


# Input: any raw value and a field name used in error messages.
# Check only that the value is a dictionary; required keys are checked elsewhere.
# Output: the same dictionary, or ValueError when the value has another type.
def _mapping(value: object, field: str) -> dict[str, Any]:
    if not isinstance(value, dict):
        raise ValueError(f"{field} must be a JSON object")
    return value


# Input: a raw number/string, an error-field name, and an inclusive upper limit.
# ASCII decimal string -> integer; reject bools, floats, and out-of-range values.
# Output: one integer from 0 to maximum, or ValueError for unacceptable input.
def _integer(value: object, field: str, maximum: int) -> int:
    # Source quantities are decimal strings. Never coerce None, floats, or bools.
    if isinstance(value, str) and value.isascii() and value.isdecimal():
        value = int(value)
    if type(value) is not int or not 0 <= value <= maximum:
        raise ValueError(
            f"{field} must be an integer from 0 to {maximum}; got {value!r}"
        )
    return value


# Input: one raw dialogue dictionary containing chat_logs.
# Require a nonempty list of dictionaries, each with a string text field.
# Output: that message list; participant IDs and offers are checked later.
def _messages(raw: dict[str, Any]) -> list[dict[str, Any]]:
    messages = raw.get("chat_logs")
    if not isinstance(messages, list) or not messages:
        raise ValueError("chat_logs must be a nonempty list")
    for message in messages:
        message = _mapping(message, "chat_logs entry")
        if not isinstance(message.get("text"), str):
            raise ValueError("chat_logs entry must have a text string")
    return messages


# Input: a raw allocation value and its field name; expect exactly the issue keys.
# Food/Water/Firewood quantities -> checked integers in the fixed ISSUES order.
# Three integers -> Resources(food=..., water=..., firewood=...).
# Output: one allocation with each quantity in 0..UNITS_PER_RESOURCE, or an error.
def _allocation(value: object, field: str) -> Resources:
    amounts = _mapping(value, field)
    if set(amounts) != set(ISSUES):
        raise ValueError(f"{field} must contain exactly Food, Water, Firewood")
    return Resources(
        *(
            _integer(amounts[issue], f"{field}.{issue}", UNITS_PER_RESOURCE)
            for issue in ISSUES
        )
    )


# Input: participant ID, raw participant information, and an existing allocation.
# High/Medium/Low preferences -> checked resource names -> points per unit.
# Read the recorded score; combine ID, numeric values, allocation, and that score.
# Output: a Participant object; calculated-versus-recorded checks happen later.
def _participant(
    participant_id: str, value: object, allocation: Resources
) -> Participant:
    info = _mapping(value, participant_id)
    preferences = _mapping(info.get("value2issue"), f"{participant_id}.value2issue")
    if set(preferences) != set(POINTS) or sorted(
        preferences.values(), key=str
    ) != sorted(ISSUES):
        raise ValueError(
            f"{participant_id}: High, Medium, Low must name each issue once"
        )
    values = {preferences[rank]: points for rank, points in POINTS.items()}
    outcomes = _mapping(info.get("outcomes"), f"{participant_id}.outcomes")
    recorded_score = _integer(
        outcomes.get("points_scored"),
        f"{participant_id}.points_scored",
        UNITS_PER_RESOURCE * sum(POINTS.values()),
    )
    return Participant(
        participant_id=participant_id,
        values=Resources(*(values[issue] for issue in ISSUES)),
        allocation=allocation,
        recorded_score=recorded_score,
    )


# Input: one accepted dialogue dictionary with chat_logs and participant_info.
# Final offer pair -> proposer-relative quantities -> allocations for fixed IDs.
# Allocations + participant information -> two Participants -> one AcceptedDeal.
# Output: that deal after totals and both scores pass; invalid input raises errors.
def parse_accepted(raw: dict[str, Any]) -> AcceptedDeal:
    """Validate required fields and scores; never repair or skip a bad deal."""
    raw = _mapping(raw, "dialogue")
    dialogue_id = raw.get("dialogue_id")
    if type(dialogue_id) is not int or dialogue_id < 0:
        raise ValueError("dialogue_id must be a nonnegative integer")
    messages = _messages(raw)
    if len(messages) < 2 or messages[-1]["text"] != "Accept-Deal":
        raise ValueError(f"Dialogue {dialogue_id}: expected a final Accept-Deal")
    proposal, acceptance = messages[-2:]
    if proposal["text"] != "Submit-Deal":
        raise ValueError("Accept-Deal must immediately follow Submit-Deal")
    proposer_id = proposal.get("id")
    acceptor_id = acceptance.get("id")
    if (
        proposer_id not in PARTICIPANT_IDS
        or acceptor_id not in PARTICIPANT_IDS
        or proposer_id == acceptor_id
    ):
        raise ValueError(
            "Proposal and acceptance must come from the two different roles"
        )
    info = _mapping(raw.get("participant_info"), "participant_info")
    if set(info) != set(PARTICIPANT_IDS):
        raise ValueError("participant_info must contain exactly mturk_agent_1 and 2")
    task = _mapping(proposal.get("task_data"), "Submit-Deal.task_data")
    # 'you' means the proposer, who can be either participant.
    allocations = {
        proposer_id: _allocation(task.get("issue2youget"), "issue2youget"),
        acceptor_id: _allocation(task.get("issue2theyget"), "issue2theyget"),
    }
    for resource in ("food", "water", "firewood"):
        total = sum(getattr(amounts, resource) for amounts in allocations.values())
        if total != UNITS_PER_RESOURCE:
            raise ValueError(
                f"{resource}: allocations must sum to {UNITS_PER_RESOURCE}; got {total}"
            )
    # Fixed output order: participant_1 is always mturk_agent_1 (and likewise 2).
    deal = AcceptedDeal(
        dialogue_id=dialogue_id,
        proposer_id=proposer_id,
        participant_1=_participant(
            PARTICIPANT_IDS[0],
            info[PARTICIPANT_IDS[0]],
            allocations[PARTICIPANT_IDS[0]],
        ),
        participant_2=_participant(
            PARTICIPANT_IDS[1],
            info[PARTICIPANT_IDS[1]],
            allocations[PARTICIPANT_IDS[1]],
        ),
    )
    verify_scores(deal)
    return deal


# Input: a local Path to JSON containing a list of dialogue dictionaries.
# Read the list, pass over walkaways, and parse the first accepted record in order.
# Output: one checked AcceptedDeal; later records remain unprocessed.
# A broken encountered record raises an error; this loader does not check SHA256.
def load_first_accepted(path: Path) -> AcceptedDeal:
    """Select the first accepted record in file order from an explicit local path."""

    # File on disk
    # ↓ read_text()
    # Text containing JSON
    #     ↓ json.loads()
    # Python list containing dictionaries
    records = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(records, list):
        raise ValueError("CaSiNo JSON must be a list of dialogues")

    for index, raw in enumerate(records):
        try:
            # Check that raw is a dictionary; this does not check its keys.
            raw = _mapping(raw, "dialogue")
            # obtain a checked list of messages
            terminal = _messages(raw)[-1]["text"]
            if terminal == "Accept-Deal":
                return parse_accepted(raw)

            # Walkaways have no accepted allocation. Unknown endings are errors.
            if terminal != "Walk-Away":
                raise ValueError(f"Unexpected final event: {terminal!r}")
        except ValueError as error:
            raise ValueError(f"Record index {index}: {error}") from error
    raise ValueError("No accepted deal found")
