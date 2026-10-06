import json
from copy import deepcopy
from pathlib import Path

import pytest

from evidence_lab.negotiation.casino import load_first_accepted, parse_accepted
from evidence_lab.negotiation.schema import Resources, score, verify_scores

FIXTURE = Path(__file__).parent / "fixtures/casino_dialogue_0.json"


# Input: no arguments; read the small local fixture for source dialogue 0.
# Output: a fresh raw dictionary for each test, so edits do not leak between tests.
@pytest.fixture
def raw():
    return json.loads(FIXTURE.read_text(encoding="utf-8"))


# Input: invented Resources objects with a hand-calculated result.
# Assert the arithmetic returns 19 for the example and zero for no received items.
def test_hand_calculated_score():
    # Invented example: two food and three firewood = 2*5 + 0*4 + 3*3 = 19.
    allocation = Resources(food=2, water=0, firewood=3)
    values = Resources(food=5, water=4, firewood=3)
    assert score(allocation, values) == 19
    assert score(Resources(0, 0, 0), values) == 0


# Input: the dialogue fixture and either participant as the proposer.
# Assert both offer orientations produce the same allocations, values, and scores.
@pytest.mark.parametrize("proposer", ["mturk_agent_1", "mturk_agent_2"])
def test_source_record_with_both_proposer_orientations(raw, proposer):
    proposal, acceptance = raw["chat_logs"]
    if proposer == "mturk_agent_1":
        # Same deal, represented as if participant 1 had submitted it.
        proposal["id"], acceptance["id"] = acceptance["id"], proposal["id"]
        task = proposal["task_data"]
        task["issue2youget"], task["issue2theyget"] = (
            task["issue2theyget"],
            task["issue2youget"],
        )
    deal = parse_accepted(raw)
    assert deal.dialogue_id == 0
    assert deal.proposer_id == proposer
    assert deal.participant_1.participant_id == "mturk_agent_1"
    assert deal.participant_2.participant_id == "mturk_agent_2"
    assert deal.participant_1.allocation == Resources(food=1, water=0, firewood=3)
    assert deal.participant_2.allocation == Resources(food=2, water=3, firewood=0)
    assert deal.participant_1.values == Resources(food=4, water=3, firewood=5)
    assert deal.participant_2.values == Resources(food=3, water=4, firewood=5)
    assert verify_scores(deal) == (19, 18)


# Input: the dialogue fixture and one unacceptable raw quantity.
# Assert parsing raises ValueError rather than silently converting bad input.
@pytest.mark.parametrize("quantity", [None, True, 1.5, "1.5", "4", "-1"])
def test_invalid_quantity_fails(raw, quantity):
    raw["chat_logs"][0]["task_data"]["issue2youget"]["Food"] = quantity
    with pytest.raises(ValueError, match="issue2youget.Food must be an integer"):
        parse_accepted(raw)


# Input: a dialogue whose individual food quantities fit bounds but total four.
# Assert parsing rejects a combined total above the available three units.
def test_resources_must_be_conserved(raw):
    raw["chat_logs"][0]["task_data"]["issue2youget"]["Food"] = "3"
    with pytest.raises(ValueError, match="food: allocations must sum to 3"):
        parse_accepted(raw)


# Input: the dialogue fixture with one required preference removed.
# Assert parsing rejects the incomplete High/Medium/Low mapping.
def test_missing_preference_fails(raw):
    del raw["participant_info"]["mturk_agent_1"]["value2issue"]["High"]
    with pytest.raises(ValueError, match="High, Medium, Low must name each issue once"):
        parse_accepted(raw)


# Input: the dialogue fixture with a missing (None) recorded score.
# Assert parsing reports an error instead of treating missing data as zero.
def test_missing_score_is_not_zero(raw):
    raw["participant_info"]["mturk_agent_1"]["outcomes"]["points_scored"] = None
    with pytest.raises(ValueError, match="points_scored must be an integer"):
        parse_accepted(raw)


# Input: a dialogue with valid allocations but an incorrect source-recorded score.
# Assert independent score reconstruction detects the disagreement.
def test_recorded_score_disagreement_fails(raw):
    raw["participant_info"]["mturk_agent_1"]["outcomes"]["points_scored"] = 20
    with pytest.raises(ValueError, match="computed score 19 != recorded score 20"):
        parse_accepted(raw)


# Input: a dialogue changed so the same participant proposes and accepts.
# Assert the parser requires two different participant roles.
def test_cannot_accept_your_own_proposal(raw):
    raw["chat_logs"][-1]["id"] = "mturk_agent_2"
    with pytest.raises(ValueError, match="two different roles"):
        parse_accepted(raw)


# Input: a dialogue where Accept-Deal no longer follows Submit-Deal.
# Assert parsing rejects that invalid final-event sequence.
def test_acceptance_requires_immediately_preceding_submission(raw):
    raw["chat_logs"][0]["text"] = "Reject-Deal"
    with pytest.raises(ValueError, match="immediately follow Submit-Deal"):
        parse_accepted(raw)


# Input: a temporary dataset with a walkaway followed by two accepted dialogues.
# Assert selection returns the first accepted dialogue, preserving file order.
def test_loads_first_accepted_in_file_order(tmp_path, raw):
    walkaway = {"chat_logs": [{"text": "Walk-Away"}]}
    later = deepcopy(raw)
    later["dialogue_id"] = 1
    path = tmp_path / "casino.json"
    path.write_text(json.dumps([walkaway, raw, later]), encoding="utf-8")
    assert load_first_accepted(path).dialogue_id == 0


# Input: a temporary dataset with a broken accepted record before a valid one.
# Assert the loader reports the broken record instead of skipping to success.
def test_bad_accepted_record_is_not_skipped(tmp_path, raw):
    bad = deepcopy(raw)
    bad["participant_info"]["mturk_agent_1"]["outcomes"]["points_scored"] = 20
    path = tmp_path / "casino.json"
    path.write_text(json.dumps([bad, raw]), encoding="utf-8")
    with pytest.raises(ValueError, match="Record index 0:.*computed score"):
        load_first_accepted(path)


# Input: temporary malformed/empty datasets and their expected error messages.
# Assert the loader rejects each input instead of returning an accepted deal.
@pytest.mark.parametrize(
    ("records", "message"),
    [
        ({}, "must be a list"),
        ([], "No accepted deal"),
        ([{"chat_logs": []}], "nonempty list"),
        ([{"chat_logs": [{"text": "Unexpected"}]}], "Unexpected final event"),
    ],
)
def test_invalid_or_absent_accepted_input_fails(tmp_path, records, message):
    path = tmp_path / "casino.json"
    path.write_text(json.dumps(records), encoding="utf-8")
    with pytest.raises(ValueError, match=message):
        load_first_accepted(path)
