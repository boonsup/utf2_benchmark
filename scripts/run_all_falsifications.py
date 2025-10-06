#!/usr/bin/env python3
"""
UTF-2.0 Falsification Suite Runner (Color-Enhanced)
---------------------------------------------------
Executes all falsification schemes (T̂, D̂, F̂, D̂⊗F̂) with timing,
colored status output, and summary reporting.

Author: Boonsup Waikham
Date: 2025-10-06
"""

import importlib
import time
import sys

# ---- ANSI Colors ----
class Color:
    RESET = "\033[0m"
    BOLD = "\033[1m"
    GREEN = "\033[92m"
    RED = "\033[91m"
    YELLOW = "\033[93m"
    CYAN = "\033[96m"
    GRAY = "\033[90m"

MODULES = [
    ("T̂  Energy Non-Conservation", "src.utf.falsification.test_T_energy_nonconservation", "falsify_T_operator"),
    ("D̂  Decoherence Irreversibility", "src.utf.falsification.test_D_decoherence_violation", "falsify_D_operator"),
    ("F̂  Chaos Amplification", "src.utf.falsification.test_F_false_chaos_amplification", "falsify_F_operator"),
    ("D̂⊗F̂ Coupling Variation", "src.utf.falsification.test_DF_coupling_variation", "falsify_DF_operator"),
]


def run_module(title, mod_name, func_name):
    print(f"\n{Color.CYAN}{'='*80}{Color.RESET}")
    print(f"{Color.BOLD}{title}{Color.RESET}")
    print(f"{Color.GRAY}{mod_name}{Color.RESET}")
    print(f"{Color.CYAN}{'-'*80}{Color.RESET}")

    try:
        mod = importlib.import_module(mod_name)
        fn = getattr(mod, func_name)
    except Exception as e:
        print(f"{Color.RED}Import error: {e}{Color.RESET}")
        return False, 0.0

    t0 = time.time()
    try:
        ok = fn()
    except Exception as e:
        print(f"{Color.RED}Execution error: {e}{Color.RESET}")
        ok = False
    dt = time.time() - t0

    if ok:
        print(f"{Color.GREEN}✅ PASSED {Color.RESET}({dt:.3f}s)")
    else:
        print(f"{Color.RED}❌ FAILED {Color.RESET}({dt:.3f}s)")
    return ok, dt


def main():
    print(f"{Color.BOLD}UTF-2.0 Reproducible Falsification Suite{Color.RESET}")
    print(f"{Color.GRAY}Running all operators with colored summary...{Color.RESET}")

    results = []
    total_time = 0.0
    for title, mod, func in MODULES:
        ok, dt = run_module(title, mod, func)
        results.append(ok)
        total_time += dt

    passed = sum(results)
    total = len(results)
    print(f"\n{Color.BOLD}{'='*80}{Color.RESET}")
    if all(results):
        print(f"{Color.GREEN}🎉 ALL {total} TESTS PASSED — total runtime {total_time:.2f}s{Color.RESET}")
    else:
        print(f"{Color.RED}⚠️  {passed}/{total} TESTS PASSED — total runtime {total_time:.2f}s{Color.RESET}")
        sys.exit(1)


if __name__ == "__main__":
    main()
