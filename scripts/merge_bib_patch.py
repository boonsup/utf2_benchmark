#!/usr/bin/env python3
"""
merge_bib_patch.py — Merge SOTA citations into main references.bib
------------------------------------------------------------------
Scans `references_patch.bib` and appends new entries to `references.bib`
only if their citation keys don't already exist.

Usage:
  python scripts/merge_bib_patch.py --main tex/references.bib --patch tex/references_patch.bib
"""

import re
import argparse
from pathlib import Path
from datetime import datetime

parser = argparse.ArgumentParser(description="Merge patch BibTeX entries into main references.bib.")
parser.add_argument("--main", default="tex/references.bib", help="Path to main .bib file.")
parser.add_argument("--patch", default="tex/references_patch.bib", help="Path to patch .bib file.")
parser.add_argument("--output", default=None, help="Optional output path (default = overwrite main).")
args = parser.parse_args()

main_path = Path(args.main)
patch_path = Path(args.patch)
output_path = Path(args.output) if args.output else main_path

if not patch_path.exists():
    raise FileNotFoundError(f"❌ Patch file not found: {patch_path}")
if not main_path.exists():
    raise FileNotFoundError(f"❌ Main references file not found: {main_path}")

def parse_bib_keys(text):
    """Extract citation keys from BibTeX text."""
    return re.findall(r"@\w+\{([^,]+),", text)

main_text = main_path.read_text(encoding="utf-8")
patch_text = patch_path.read_text(encoding="utf-8")

main_keys = set(parse_bib_keys(main_text))
patch_entries = re.findall(r"(@\w+\{[^@]+?})", patch_text, flags=re.DOTALL)

new_entries = []
for entry in patch_entries:
    m = re.search(r"@\w+\{([^,]+),", entry)
    if not m:
        continue
    key = m.group(1).strip()
    if key not in main_keys:
        new_entries.append(entry)
        main_keys.add(key)

if not new_entries:
    print("✅ No new entries found — references.bib is already up to date.")
else:
    merged = main_text.strip() + "\n\n% --- Auto-merged on {} ---\n\n".format(
        datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S UTC")
    )
    merged += "\n\n".join(new_entries)
    output_path.write_text(merged.strip() + "\n", encoding="utf-8")
    print(f"✅ Added {len(new_entries)} new entries → {output_path}")

print("🎯 Merge complete.")
