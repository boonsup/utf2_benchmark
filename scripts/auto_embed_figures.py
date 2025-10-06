#!/usr/bin/env python3
"""
UTF-2.0 — Auto-Embed Benchmark Figures into README.md
Run after DOI sync to always show latest reproducibility visuals.
"""

import os, glob, re
from pathlib import Path

FIG_DIR = Path("figures")
README = Path("README.md")
SECTION_HEADER = "## 📊 Latest Benchmarks"

def make_markdown_gallery():
    """Generate markdown image block for all .png figures."""
    images = sorted(FIG_DIR.glob("*.png"), key=os.path.getmtime, reverse=True)
    if not images:
        return f"{SECTION_HEADER}\n\n*(No figures available — run benchmarks first.)*\n"
    lines = [SECTION_HEADER, ""]
    for img in images:
        rel = img.as_posix()
        lines.append(f"![{img.stem}]({rel})")
    return "\n".join(lines) + "\n"

def update_readme():
    md = README.read_text(encoding="utf-8") if README.exists() else ""
    block = make_markdown_gallery()
    pattern = re.compile(rf"{SECTION_HEADER}.*?(?=\n## |\Z)", re.S)
    if pattern.search(md):
        new_md = pattern.sub(block.strip() + "\n", md)
    else:
        new_md = md.rstrip() + "\n\n" + block + "\n"
    if new_md != md:
        README.write_text(new_md, encoding="utf-8", newline="\n")
        print("✅ README.md updated with latest figures.")
    else:
        print("ℹ️ No changes needed — figures unchanged.")

if __name__ == "__main__":
    update_readme()
