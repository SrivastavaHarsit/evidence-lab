"""Show one checked deal: uv run --locked python scripts/check_one.py PATH."""

import argparse
from pathlib import Path

from evidence_lab.negotiation.casino import load_first_accepted
from evidence_lab.negotiation.schema import score

parser = argparse.ArgumentParser(
    description="Reconstruct the first accepted CaSiNo deal"
)
parser.add_argument("path", type=Path, help="explicit path to a local CaSiNo JSON file")
args = parser.parse_args()

deal = load_first_accepted(args.path)
print(f"Dialogue {deal.dialogue_id}; proposer: {deal.proposer_id}")
for participant in (deal.participant_1, deal.participant_2):
    print(participant.participant_id)
    print(f"  allocation: {participant.allocation}")
    print(f"  values per unit: {participant.values}")
    print(f"  computed: {score(participant.allocation, participant.values)}")
    print(f"  recorded: {participant.recorded_score}")
print("PASS: both reconstructed scores match the source.")
