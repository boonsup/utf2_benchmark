import json, os
from pathlib import Path

def build_badge_table(json_log="data/release_history.json", out="README.md"):
    if not Path(json_log).exists():
        print("⚠️ No release history found.")
        return
    releases = json.load(open(json_log))
    table = "\n\n| Version | DOI | Date |\n|:--|:--|:--|\n"
    for r in releases[-10:][::-1]:
        badge = f"[![DOI](https://zenodo.org/badge/DOI/{r['doi']}.svg)](https://doi.org/{r['doi']})"
        table += f"| {r['version']} | {badge} | {r['date']} |\n"

    md = Path(out).read_text()
    new = re.sub(r"\| Version \| DOI \| Date \|.*", table, md, flags=re.S)
    Path(out).write_text(new)
    print("✅ Updated Zenodo badge table in README.md")
