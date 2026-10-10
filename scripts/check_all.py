"""Observe milestone 1: uv run --locked python scripts/check_all.py PATH."""

import argparse
import sys
from pathlib import Path

from evidence_lab.negotiation.audit import load_audit


# Input: a local JSON path from terminal arguments or VS Code launch args.
# Work: audit every record, reconcile counts, and print any invalid diagnostics.
# Output: exit code 0 (clean), 1 (invalid records), or 2 (file/input error).
def main() -> int:
    parser = argparse.ArgumentParser(description="Audit every CaSiNo record")

    parser.add_argument("path", type=Path, help="explicit path to local CaSiNo JSON")

    args = parser.parse_args()
    try:
        result = load_audit(args.path)
    except (OSError, ValueError) as error:
        print(f"INPUT ERROR: {error}", file=sys.stderr)
        return 2

    accepted_deals = result.accepted_deals

    walkaways = result.walkaways

    invalid_records = result.invalid_records

    accounted = len(accepted_deals) + len(walkaways) + len(invalid_records)

    if accounted != result.total_records:
        raise RuntimeError("Audit accounting does not reconcile")

    print(f"Total records: {result.total_records}")
    print(f"Accepted endings: {result.accepted_endings}")
    print(f"Valid accepted deals: {len(accepted_deals)}")
    print(f"Walkaways: {len(walkaways)}")
    print(f"Invalid records: {len(invalid_records)}")
    print(
        f"Accounting: {result.total_records} = {len(accepted_deals)} valid accepted "
        f"+ {len(walkaways)} walkaways + {len(invalid_records)} invalid"
    )

    for outcome in invalid_records:
        identity = (
            f"dialogue {outcome.dialogue_id}"
            if outcome.dialogue_id is not None
            else "dialogue ID unavailable"
        )

        print(f"Record index {outcome.record_index}; {identity}: {outcome.error}")

    if not result.ok:
        print("FAIL: audit contains invalid records.")
        return 1

    print("PASS: all records accounted for; no invalid records.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
