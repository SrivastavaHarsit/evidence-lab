"""Plain records; casino.py validates the source before returning these objects."""

from dataclasses import dataclass


# Input: food, water, and firewood fields, intended to contain integer values.
# Output: a frozen Resources object used for quantities or points per unit.
# The caller determines the meaning; construction does not validate the fields.
@dataclass(frozen=True)
class Resources:
    """Food, water, and firewood, used for quantities or points per unit."""

    food: int
    water: int
    firewood: int


# Input: an ID, Resources for values and allocation, and a source-recorded score.
# Output: a frozen Participant grouping everything needed to reconstruct a score.
# Construction stores fields; the parser and verify_scores perform the checks.
@dataclass(frozen=True)
class Participant:
    participant_id: str
    values: Resources
    allocation: Resources
    recorded_score: int


# Input: dialogue/proposer IDs and the two Participants in fixed participant order.
# Output: a frozen AcceptedDeal containing one negotiated outcome.
# Participant 1 stays participant 1 even when participant 2 proposes the offer.
@dataclass(frozen=True)
class AcceptedDeal:
    dialogue_id: int
    proposer_id: str
    participant_1: Participant
    participant_2: Participant


# Input: Resources for received quantities and Resources for points per unit.
# Multiply each quantity by its value, then add the three contributions.
# Output: the calculated integer score; this function does not read source scores.
def score(allocation: Resources, values: Resources) -> int:
    """Each resource contributes quantity multiplied by points per unit."""
    return (
        allocation.food * values.food
        + allocation.water * values.water
        + allocation.firewood * values.firewood
    )


# Input: one AcceptedDeal containing both allocations, values, and recorded scores.
# Recalculate each participant's score and compare it with the source-recorded one.
# Output: (participant_1_score, participant_2_score), or ValueError on disagreement.
def verify_scores(deal: AcceptedDeal) -> tuple[int, int]:
    """Return scores in participant 1/2 order, or raise on any disagreement."""
    computed = []
    for participant in (deal.participant_1, deal.participant_2):
        reconstructed = score(participant.allocation, participant.values)
        if reconstructed != participant.recorded_score:
            raise ValueError(
                f"Dialogue {deal.dialogue_id}, {participant.participant_id}: "
                f"computed score {reconstructed} != recorded score "
                f"{participant.recorded_score}"
            )
        computed.append(reconstructed)
    return computed[0], computed[1]
