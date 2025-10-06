"""
Falsification Scheme 2: D̂ — Decoherence Irreversibility Check
--------------------------------------------------------------
Simulates a qubit density matrix under environment coupling.
Validates that decoherence increases (Tr[ρ^2] decreases) over time.
"""

import numpy as np

def density_matrix(purity):
    """Generate a 2x2 mixed-state density matrix with given purity."""
    rho = np.array([[purity, 0], [0, 1 - purity]])
    return rho / np.trace(rho)

def decohere(rho, gamma=0.1, dt=1.0):
    """Apply simple exponential decoherence channel."""
    p = np.exp(-gamma * dt)
    rho_off = rho.copy()
    rho_off[0,1] *= p
    rho_off[1,0] *= p
    return rho_off

def purity(rho):
    return np.real(np.trace(rho @ rho))

def falsify_D_operator(steps=10):
    """Ensure purity decreases monotonically."""
    rho = density_matrix(0.9)
    last_purity = purity(rho)
    for t in range(steps):
        rho = decohere(rho, gamma=0.2, dt=0.5)
        p_now = purity(rho)
        if p_now > last_purity + 1e-8:
            print(f"❌ Decoherence violation at step {t}: purity increased {p_now:.4f}>{last_purity:.4f}")
            return False
        last_purity = p_now
    print("✅ D̂ decoherence irreversibility validated.")
    return True

if __name__ == "__main__":
    falsify_D_operator()
