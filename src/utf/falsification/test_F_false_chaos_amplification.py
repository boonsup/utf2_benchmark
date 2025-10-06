"""
Falsification Scheme 3: F̂ — False Chaos Amplification Check
------------------------------------------------------------
Verifies that chaos (sensitivity to initial conditions) does not produce net energy gain.
"""

import numpy as np

def logistic_map(x, r=3.9):
    return r * x * (1 - x)

def falsify_F_operator(steps=1000):
    """Check Lyapunov divergence vs. total energy."""
    x0 = 0.500
    x1 = 0.500001
    E0 = x0**2  # pseudo energy
    E1 = x1**2
    d0 = abs(x1 - x0)

    for _ in range(steps):
        x0, x1 = logistic_map(x0), logistic_map(x1)
        d = abs(x1 - x0)
        if (x0**2 - E0) > 1e-3 or (x1**2 - E1) > 1e-3:
            print("❌ Energy inflation detected — chaos amplified energy.")
            return False
        if np.isnan(d) or d > 1e6:
            break

    print("✅ F̂ chaos growth validated — no spurious energy amplification.")
    return True

if __name__ == "__main__":
    falsify_F_operator()
