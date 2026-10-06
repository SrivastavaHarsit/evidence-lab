"""Fetch the exact source in the manifest; save only after both checks pass."""

import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path
from urllib.request import urlopen

ROOT = Path(__file__).resolve().parents[1]


# Input: no arguments; read the pinned URL, checksum, size, and path from manifest.
# Downloaded bytes -> SHA256/size checks -> local dataset and retrieval receipt.
# Output: those files and printed confirmation; the function itself returns None.
# A checksum/size mismatch raises an error before replacing the local dataset.
def download() -> None:
    manifest = json.loads((ROOT / "sources/casino.manifest.json").read_text())
    with urlopen(manifest["url"], timeout=60) as response:
        content = response.read()
    actual_hash = hashlib.sha256(content).hexdigest()
    if actual_hash != manifest["sha256"]:
        raise ValueError(
            f"SHA256 mismatch: expected {manifest['sha256']}, got {actual_hash}"
        )
    if len(content) != manifest["size_bytes"]:
        raise ValueError(
            f"Byte size mismatch: expected {manifest['size_bytes']}, got {len(content)}"
        )
    destination = ROOT / manifest["local_path"]
    destination.parent.mkdir(parents=True, exist_ok=True)
    temporary = destination.with_suffix(".json.part")
    temporary.write_bytes(content)
    temporary.replace(destination)
    receipt = {
        "retrieved_at_utc": datetime.now(timezone.utc).isoformat(),
        "url": manifest["url"],
        "revision": manifest["revision"],
        "sha256": actual_hash,
        "size_bytes": len(content),
    }
    (destination.parent / "casino.retrieval.json").write_text(
        json.dumps(receipt, indent=2) + "\n", encoding="utf-8"
    )
    print(f"Verified {len(content):,} bytes; SHA256 {actual_hash}")
    print(f"Saved {destination}")


if __name__ == "__main__":
    download()
