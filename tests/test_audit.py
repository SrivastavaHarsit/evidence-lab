"""Offline examples for whole-file accounting; never edit the raw dataset."""

import json
import subprocess
import sys
from copy import deepcopy
from pathlib import Path

import pytest

from evidence_lab.negotiation.audit import audit_record, audit_records, load_audit
from evidence_lab.negotiation.schema import Resources, verify_scores

PROJECT = Path(__file__).parents[1]
SOURCE_FIXTURE = PROJECT / "tests/fixtures/casino_dialogue_0.json"
AUDIT_FIXTURE = PROJECT / "tests/fixtures/casino_audit_small.json"
CHECK_ALL = PROJECT / "scripts/check_all.py"


# Input: the existing small source fixture, without reading the downloaded dataset.
# Work: decode a fresh dictionary for each test so experiments stay independent.
# Output: a raw accepted dialogue with verified source scores 19 and 18.
@pytest.fixture
def raw():
    return json.loads(SOURCE_FIXTURE.read_text(encoding="utf-8"))


# Input: a fresh dialogue, a nested field path, and one replacement value.
# Work: follow dictionaries/lists to the final field and replace only that field.
# Output: the same dialogue with one deliberate defect for an audit experiment.
def change_field(raw, fields, value):
    target = raw
    for field in fields[:-1]:
        target = target[field]
    target[fields[-1]] = value
    return raw


# Input: two valid deals, an invalid accepted deal between them, and a walkaway.
# Work: audit the checked-in four-record teaching example in file order.
# Output: every position is represented, the bad score is visible, counts reconcile.
def test_small_example_keeps_every_outcome_and_continues_after_error():
    result = load_audit(AUDIT_FIXTURE)

    assert [outcome.record_index for outcome in result.outcomes] == [0, 1, 2, 3]
    assert [outcome.dialogue_id for outcome in result.outcomes] == [100, 101, 102, 103]
    assert [outcome.status for outcome in result.outcomes] == [
        "accepted",
        "invalid",
        "walkaway",
        "accepted",
    ]
    assert result.total_records == 4
    assert result.accepted_endings == 3
    assert [deal.dialogue_id for deal in result.accepted_deals] == [100, 103]
    assert [outcome.dialogue_id for outcome in result.walkaways] == [102]
    assert len(result.invalid_records) == 1
    invalid = result.invalid_records[0]
    assert "computed score 19 != recorded score 20" in invalid.error
    assert invalid.deal is None
    assert result.walkaways[0].deal is None
    assert result.total_records == (
        len(result.accepted_deals) + len(result.walkaways) + len(result.invalid_records)
    )
    assert not result.ok


# Input: the two opposite-proposer accepted records in the teaching fixture.
# Work: obtain each checked deal from the audit rather than parse it separately.
# Output: participant order, quantities, and scores retain the original meaning.
def test_both_proposers_preserve_fixed_participant_allocations():
    result = load_audit(AUDIT_FIXTURE)
    assert {deal.proposer_id for deal in result.accepted_deals} == {
        "mturk_agent_1",
        "mturk_agent_2",
    }
    for deal in result.accepted_deals:
        assert deal.participant_1.participant_id == "mturk_agent_1"
        assert deal.participant_2.participant_id == "mturk_agent_2"
        assert deal.participant_1.allocation == Resources(1, 0, 3)
        assert deal.participant_2.allocation == Resources(2, 3, 0)
        assert deal.participant_1.values == Resources(4, 3, 5)
        assert deal.participant_2.values == Resources(3, 4, 5)
        assert verify_scores(deal) == (19, 18)


def test_several_valid_accepted_records_are_all_processed(raw):
    records = []
    for dialogue_id in [7, 8, 9]:
        record = deepcopy(raw)
        record["dialogue_id"] = dialogue_id
        records.append(record)
    result = audit_records(records)

    assert result.total_records == result.accepted_endings == 3
    assert [deal.dialogue_id for deal in result.accepted_deals] == [7, 8, 9]
    assert result.walkaways == result.invalid_records == []
    assert all(outcome.error is None for outcome in result.outcomes)
    assert result.ok


@pytest.mark.parametrize(
    ("fields", "value", "message"),
    [
        (("participant_info",), None, "participant_info must be a JSON object"),
        (
            ("participant_info", "mturk_agent_1", "outcomes", "points_scored"),
            20,
            "computed score 19 != recorded score 20",
        ),
        (
            ("participant_info", "mturk_agent_1", "value2issue", "High"),
            "Food",
            "High, Medium, Low must name each issue once",
        ),
        (
            ("chat_logs", 0, "task_data", "issue2youget", "Food"),
            True,
            "issue2youget.Food must be an integer",
        ),
        (
            ("chat_logs", 0, "task_data", "issue2youget", "Food"),
            "3",
            "food: allocations must sum to 3",
        ),
        (("chat_logs", 0, "text"), "Reject-Deal", "immediately follow Submit-Deal"),
        (("chat_logs", 1, "id"), "mturk_agent_2", "two different roles"),
    ],
)
def test_audit_preserves_strict_accepted_parser_failures(raw, fields, value, message):
    bad = change_field(deepcopy(raw), fields, value)
    bad["dialogue_id"] = 42
    result = audit_records([raw, bad, raw])

    assert [outcome.status for outcome in result.outcomes] == [
        "accepted",
        "invalid",
        "accepted",
    ]
    invalid = result.invalid_records[0]
    assert invalid.record_index == 1
    assert invalid.dialogue_id == 42
    assert invalid.terminal == "Accept-Deal"
    assert message in invalid.error
    assert result.accepted_endings == 3
    assert len(result.accepted_deals) == 2
    assert not result.ok


@pytest.mark.parametrize(
    ("raw", "message"),
    [
        (None, "dialogue must be a JSON object"),
        ([], "dialogue must be a JSON object"),
        ({"dialogue_id": 4}, "chat_logs must be a nonempty list"),
        ({"dialogue_id": 4, "chat_logs": {}}, "chat_logs must be a nonempty list"),
        ({"dialogue_id": 4, "chat_logs": []}, "chat_logs must be a nonempty list"),
        ({"dialogue_id": 4, "chat_logs": [None]}, "chat_logs entry"),
        ({"dialogue_id": 4, "chat_logs": [{}]}, "text string"),
        ({"dialogue_id": 4, "chat_logs": [{"text": 7}]}, "text string"),
        (
            {"dialogue_id": 4, "chat_logs": [{"text": "Unexpected"}]},
            "Unexpected final event",
        ),
    ],
)
def test_unknown_or_malformed_record_has_a_diagnostic(raw, message):
    outcome = audit_record(raw, record_index=12)

    assert outcome.record_index == 12
    assert outcome.status == "invalid"
    assert outcome.deal is None
    assert message in outcome.error


# Input: accepted endings with a bad earlier message or an invalid dialogue ID.
# Work: distinguish observable final text from full record validity.
# Output: both contribute to accepted endings, neither becomes a checked deal.
def test_accepted_ending_is_counted_even_when_the_record_is_invalid(raw):
    bad_message = deepcopy(raw)
    bad_message["chat_logs"].insert(0, None)
    bad_id = deepcopy(raw)
    bad_id["dialogue_id"] = True
    result = audit_records([bad_message, bad_id])

    assert result.total_records == result.accepted_endings == 2
    assert result.accepted_deals == []
    assert len(result.invalid_records) == 2
    assert [outcome.terminal for outcome in result.outcomes] == [
        "Accept-Deal",
        "Accept-Deal",
    ]
    assert "chat_logs entry" in result.outcomes[0].error
    assert "dialogue_id must be a nonnegative integer" in result.outcomes[1].error


def test_walkaway_does_not_invent_a_deal_or_validate_unused_fields():
    raw = {
        "dialogue_id": 17,
        "chat_logs": [
            {"text": "No agreement", "id": "someone_else"},
            {"text": "Walk-Away", "task_data": {"issue2youget": "bad"}},
        ],
        "participant_info": "unused and deliberately malformed",
    }
    result = audit_records([raw])
    outcome = result.walkaways[0]

    assert outcome.record_index == 0
    assert outcome.dialogue_id == 17
    assert outcome.terminal == "Walk-Away"
    assert outcome.status == "walkaway"
    assert outcome.deal is outcome.error is None
    assert result.total_records == 1
    assert result.accepted_endings == 0
    assert result.accepted_deals == result.invalid_records == []
    assert result.ok


@pytest.mark.parametrize("dialogue_id", [None, True, -1, "17", 17.0])
def test_walkaway_requires_a_nonnegative_integer_dialogue_id(dialogue_id):
    raw = {"dialogue_id": dialogue_id, "chat_logs": [{"text": "Walk-Away"}]}
    result = audit_records([raw])

    assert result.walkaways == []
    assert len(result.invalid_records) == 1
    assert "dialogue_id must be a nonnegative integer" in result.outcomes[0].error


@pytest.mark.parametrize("earlier_message", [None, {}, {"text": 8}])
def test_walkaway_requires_every_message_to_have_valid_shape(earlier_message):
    raw = {
        "dialogue_id": 17,
        "chat_logs": [earlier_message, {"text": "Walk-Away"}],
    }
    result = audit_records([raw])

    assert result.walkaways == []
    assert result.outcomes[0].status == "invalid"
    assert result.outcomes[0].terminal == "Walk-Away"
    assert "chat_logs entry" in result.outcomes[0].error


def test_empty_list_is_a_clean_complete_audit():
    result = audit_records([])

    assert result.total_records == result.accepted_endings == 0
    assert result.outcomes == result.accepted_deals == []
    assert result.walkaways == result.invalid_records == []
    assert result.ok


@pytest.mark.parametrize("records", [None, {}, (), "[]"])
def test_record_interpreter_rejects_non_list_outer_input(records):
    with pytest.raises(ValueError, match="list"):
        audit_records(records)


@pytest.mark.parametrize(
    ("contents", "reason"),
    [
        (b"[{", "json"),
        (b"{}", "list"),
        (b"\xff", "utf"),
    ],
)
def test_file_input_errors_are_contextual(tmp_path, contents, reason):
    path = tmp_path / "broken-casino.json"
    path.write_bytes(contents)

    with pytest.raises(ValueError) as caught:
        load_audit(path)

    assert str(path) in str(caught.value)
    assert reason in str(caught.value).lower()


# Input: a file containing clean records, an invalid record, or malformed JSON.
# Work: launch the real checker with the current test interpreter, fully offline.
# Output: success/error status is visible to people and tools through exit codes.
@pytest.mark.parametrize(
    ("contents", "expected_code"),
    [("[]", 0), ('[{"dialogue_id": 7, "chat_logs": []}]', 1), ("[{", 2)],
)
def test_checker_exit_status_distinguishes_results_from_input_failure(
    tmp_path, contents, expected_code
):
    path = tmp_path / "casino.json"
    path.write_text(contents, encoding="utf-8")
    completed = subprocess.run(
        [sys.executable, str(CHECK_ALL), str(path)],
        cwd=PROJECT,
        capture_output=True,
        text=True,
        check=False,
    )

    assert completed.returncode == expected_code, completed.stdout + completed.stderr
    assert "Traceback" not in completed.stdout + completed.stderr
