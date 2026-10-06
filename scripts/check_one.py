"""Show one checked deal: uv run --locked python scripts/check_one.py PATH."""

import argparse # helps read the arguments typed in the terminal.
from pathlib import Path # Path represents a filesystem location.

from evidence_lab.negotiation.casino import load_first_accepted
from evidence_lab.negotiation.schema import score


# The user must provide one argument called path. Convert it into a Path object.
# Input comes from the command line or VS Code launch args, not from this file.
# Argument parsing -> Namespace called args -> Path available as args.path.
parser = argparse.ArgumentParser(
    description="Reconstruct the first accepted CaSiNo deal"
)
parser.add_argument("path", type=Path, help="explicit path to a local CaSiNo JSON file")
args = parser.parse_args()

# Input: args.path, the location of the local JSON dataset.
# Path -> loader -> parser -> one checked AcceptedDeal, stored as deal.
# Output: the loop below displays allocations, values, and both scores, then PASS.
deal = load_first_accepted(args.path)
print(f"Dialogue {deal.dialogue_id}; proposer: {deal.proposer_id}")
for participant in (deal.participant_1, deal.participant_2):
    print(participant.participant_id)
    print(f"  allocation: {participant.allocation}")
    print(f"  values per unit: {participant.values}")
    print(f"  computed: {score(participant.allocation, participant.values)}")
    print(f"  recorded: {participant.recorded_score}")
print("PASS: both reconstructed scores match the source.")
