# --- add near top of file ---
DEFAULT_UTF_KEYWORDS = [
    "reproducibility",
    "UTF-2.0",
    "quantum chaos",
    "decoherence",
    "chaos stability",
    "energy cascade",
    "multi-scale simulation",
    "Monte Carlo tuning",
    "open science",
    "Zenodo benchmark",
    "benchmarking",
    "scientific workflow",
    "Lyapunov exponent",
    "arXiv integration",
]

def _load_custom_keywords(cli_list: str | None, file_path: str | None) -> list[str]:
    user = []
    if cli_list:
        user.extend([k.strip() for k in cli_list.split(",") if k.strip()])
    if file_path and os.path.exists(file_path):
        with open(file_path, "r", encoding="utf-8") as f:
            for line in f:
                k = line.strip()
                if k:
                    user.append(k)
    return user

def _merge_keywords(existing: list[str] | None, *lists: list[list[str]]) -> list[str]:
    # Stable, case-insensitive dedupe; keep original capitalization of first occurrence
    seen = set()
    merged = []
    for seq in ([existing or []] + list(lists)):
        for k in seq:
            key = k.lower()
            if key not in seen:
                seen.add(key)
                merged.append(k)
    return merged
