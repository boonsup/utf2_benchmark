# scripts/check_bib_keys.py
from pathlib import Path
import re

main_path = Path("tex/references.bib")
patch_path = Path("tex/references_patch.bib")

def extract_keys(text):
    return re.findall(r"@\w+\{([^,]+),", text)

main_keys = extract_keys(main_path.read_text(encoding="utf-8"))
patch_keys = extract_keys(patch_path.read_text(encoding="utf-8"))

print("📚 Main references.bib keys:", len(main_keys))
for k in main_keys:
    print(" -", k)

print("\n📎 Patch references_patch.bib keys:", len(patch_keys))
for k in patch_keys:
    print(" -", k)

missing = [k for k in patch_keys if k not in main_keys]
if missing:
    print("\n❌ Missing in main.bib:", missing)
else:
    print("\n✅ All patch keys already exist in main.bib!")
