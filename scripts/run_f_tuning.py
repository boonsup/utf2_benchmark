"""
Local CLI runner for F̂ chaos kernel tuning sweep.
Integrates Monte-Carlo sweep, best-fit selection, and logging.
"""
import os, sys 

project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, project_root)

import pandas as pd, numpy as np
from src.utf.tuning.logger import log_tuning_result
from src.utf.tuning.visualizer import plot_history

from src.utf.falsification.test_F_false_chaos_amplification import falsify_F_operator

def run_real_sweep(n=200, path="data/f_sweep_results.csv"):
    """Monte Carlo sweep across r, tolerance, and adapt to find stable configurations."""
    os.makedirs(os.path.dirname(path), exist_ok=True)
    results = []
    for r in np.linspace(3.6, 3.8, 25):
        for tol in np.linspace(0.06, 0.1, 10):
            for adapt in np.linspace(0.003, 0.006, 5):
                ok = falsify_F_operator(r=r, tolerance=tol, DEBUG=False)
                results.append((r, tol, adapt, ok))
    df = pd.DataFrame(results)
    df.to_csv(path, header=False, index=False)
    print(f"✅ Real Monte Carlo sweep saved → {path}")


def run_local_tuning(csv_path="data/f_sweep_results.csv"):
    if not os.path.exists("data/f_sweep_results.csv"):
        from src.utf.falsification.test_F_false_chaos_amplification import falsify_F_operator
        run_real_sweep()  # fallback to auto-generate

    df = pd.read_csv(csv_path, header=None,
                     names=["r", "tolerance", "adapt", "passed"])
    stable = df[df["passed"] == True]
    if stable.empty:
        print("⚠️ No stable results — check sweep parameters.")
        return

    # Select best-fit (minimum adapt)
    best_fit = stable.loc[stable["adapt"].astype(float).idxmin()]
    result = {"r": float(best_fit["r"]),
              "tolerance": float(best_fit["tolerance"]),
              "adapt": float(best_fit["adapt"])}

    entry = log_tuning_result(result, num_samples=len(df))
    print(f"Best-fit: {entry}")

    # Optional visualization
    # plot_history()

if __name__ == "__main__":
    run_local_tuning()
