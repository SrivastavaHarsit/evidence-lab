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
UNITS_PER_RESOURCE = 3
POINTS = {"High": 5, "Medium": 4, "Low": 3}


# Input: any value and a field name for diagnostics.
# Work: require a dictionary; its keys are checked by the caller.
# Output: the same dictionary, or ValueError for a different type.
def _mapping(value: object, field: str) -> dict[str, Any]:
    if not isinstance(value, dict):
        raise ValueError(f"{field} must be a JSON object")
    return value


# Input: a value, a diagnostic field name, and an inclusive maximum.
# Work: convert ASCII decimal strings; require an exact int from 0 to maximum.
# Output: a checked integer, or ValueError.
def _integer(value: object, field: str, maximum: int) -> int:
    if isinstance(value, str) and value.isascii() and value.isdecimal():
        value = int(value)
    if type(value) is not int or not 0 <= value <= maximum:
        raise ValueError(
            f"{field} must be an integer from 0 to {maximum}; got {value!r}"
        )
    return value


# Input: a raw dialogue dictionary.
# Work: require nonempty chat_logs and a dictionary with string text for every message.
# Output: the original message list, or ValueError; roles and offers are checked later.
def _messages(raw: dict[str, Any]) -> list[dict[str, Any]]:
    messages = raw.get("chat_logs")
    if not isinstance(messages, list) or not messages:
        raise ValueError("chat_logs must be a nonempty list")
    for message in messages:
        message = _mapping(message, "chat_logs entry")
        if not isinstance(message.get("text"), str):
            raise ValueError("chat_logs entry must have a text string")
    return messages


# Input: raw quantities and a diagnostic field name.
# Work: require exactly Food/Water/Firewood and check each quantity is from 0 to 3.
# Output: Resources in food/water/firewood order, or ValueError.
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


# Input: a participant ID, raw participant information, and checked allocation.
# Work: convert High/Medium/Low to 5/4/3 points per unit and read the recorded score.
# Output: a Participant, or ValueError; score comparison happens in verify_scores.
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


# Input: one raw accepted dialogue with its offer and participant information.
# Work: check roles ("you" means proposer), messages, resource totals, and scores.
# Output: a checked AcceptedDeal in fixed participant 1/2 order, or ValueError.
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


# Input: the Path of a local JSON file containing dialogue records.
# Work: skip walkaways and parse the first accepted record; stop after that deal.
# Output: one checked deal, or an error for bad input or no accepted deal.
def load_first_accepted(path: Path) -> AcceptedDeal:
    """Select the first accepted record in file order from an explicit local path."""

    records = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(records, list):
        raise ValueError("CaSiNo JSON must be a list of dialogues")

    for index, raw in enumerate(records):
        try:
            raw = _mapping(raw, "dialogue")
            terminal = _messages(raw)[-1]["text"]
            if terminal == "Accept-Deal":
                return parse_accepted(raw)

            if terminal != "Walk-Away":
                raise ValueError(f"Unexpected final event: {terminal!r}")
        except ValueError as error:
            raise ValueError(f"Record index {index}: {error}") from error
    raise ValueError("No accepted deal found")
