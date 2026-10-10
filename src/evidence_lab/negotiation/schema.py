"""Plain records; casino.py validates the source before returning these objects."""

from dataclasses import dataclass


@dataclass(frozen=True)
class Resources:
    """Food, water, and firewood, used for quantities or points per unit."""

    food: int
    water: int
    firewood: int


@dataclass(frozen=True)
class Participant:
    participant_id: str
    values: Resources
    allocation: Resources
    recorded_score: int


@dataclass(frozen=True)
class AcceptedDeal:
    dialogue_id: int
    proposer_id: str
    participant_1: Participant
    participant_2: Participant


# Input: received quantities and points per unit, both stored as Resources.
# Work: multiply each quantity by its value and add the three contributions.
# Output: the calculated score; recorded source scores are not used.
def score(allocation: Resources, values: Resources) -> int:
    """Each resource contributes quantity multiplied by points per unit."""
    return (
        allocation.food * values.food
        + allocation.water * values.water
        + allocation.firewood * values.firewood
    )


# Input: a deal with both allocations, values, and recorded scores.
# Work: calculate each score and compare it with that participant's recorded score.
# Output: (participant_1_score, participant_2_score), or ValueError on a mismatch.
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
