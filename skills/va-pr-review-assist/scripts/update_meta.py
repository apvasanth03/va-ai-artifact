#!/usr/bin/env python3
"""Phase 4 Step 8: Update meta.json after a re-review round.

Usage: python update_meta.py <workspace_path> <new_oid> <round>

Updates reviewed_oid, headRefOid, and round in meta.json.
"""
import os, sys
sys.path.insert(0, os.path.dirname(__file__))
from _utils import read_meta, write_meta


def main() -> None:
    if len(sys.argv) < 4:
        print("Usage: update_meta.py <workspace> <new_oid> <round>", file=sys.stderr)
        sys.exit(1)

    workspace = sys.argv[1]
    new_oid   = sys.argv[2]
    round_n   = int(sys.argv[3])

    meta = read_meta(workspace)
    meta["reviewed_oid"] = new_oid
    meta["headRefOid"]   = new_oid
    meta["round"]        = round_n
    write_meta(workspace, meta)

    print(f"meta.json updated — reviewed_oid={new_oid[:8]}... round={round_n}")


if __name__ == "__main__":
    main()
