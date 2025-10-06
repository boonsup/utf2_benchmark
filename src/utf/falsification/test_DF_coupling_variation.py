"""
Falsification Scheme 4: (D̂ ⊗ F̂) Coupling Variation
-----------------------------------------------------
Simulates quantum-to-classical energy transfer: as decoherence (D̂)
destroys quantum coherence, that "lost" information appears as
heat or turbulent energy in a classical field (F̂).

Checks:
  - Total energy balance between quantum and classical domains.
  - Correlation between decoherence rate and classical turbulence amplitude.
"""

import numpy as np

def decoherence_channel(amplitude, gamma=0.1, dt=1.0):
    """Simple exponential decay of coherence amplitude."""
    return amplitude * np.exp(-gamma * dt)

def classical_diffusion_step(E_classical, injection, diffusion=0.01):
    """Toy diffusion equation with injected energy from D̂."""
    return E_classical + diffusion * (injection - E_classical)

def df_coupling_simulation(steps=50, gamma=0.05, coupling=0.2):
    """
    Run a D̂⊗F̂ simulation:
      quantum_amp → decays via D̂
      classical_field → energized via F̂
    Returns arrays for plotting and analysis.
    """
    amp = 1.0           # quantum coherence amplitude (normalized)
    E_quantum = amp**2  # "quantum energy"
    E_classical = 0.0
    results = []

    for t in range(steps):
        amp_next = decoherence_channel(amp, gamma=gamma)
        dE_loss = (amp**2 - amp_next**2)
        E_classical = classical_diffusion_step(E_classical, injection=dE_loss * coupling)
        E_total = amp_next**2 + E_classical
        results.append((t, amp_next, E_classical, E_total))
        amp = amp_next

    return np.array(results)

def falsify_DF_operator():
    """Check conservation and correlation in the D̂⊗F̂ interface."""
    data = df_coupling_simulation()
    total_energy = data[:, 3]
    delta = np.abs(total_energy - total_energy[0])

    if np.any(delta > 1e-3):
        print(f"❌ Energy conservation failed in D̂⊗F̂: ΔE = {np.max(delta):.3e}")
        return False

    amp_decay = np.gradient(data[:, 1])
    class_growth = np.gradient(data[:, 2])
    corr = np.corrcoef(-amp_decay, class_growth)[0, 1]

    if corr < 0.8:
        print(f"⚠️ Weak coupling correlation: correlation={corr:.2f}")
        return False

    print(f"✅ D̂⊗F̂ coupling validated: ΔE < 1e-3, correlation={corr:.2f}")
    return True

def run_all_falsifications():
    from importlib import import_module
    modules = [
        "utf.falsification.test_T_energy_nonconservation",
        "utf.falsification.test_D_decoherence_violation",
        "utf.falsification.test_F_false_chaos_amplification",
        "utf.falsification.test_DF_coupling_variation",
    ]
    for mod in modules:
        m = import_module(mod)
        print(f"\n=== Running {mod} ===")
        m.main() if hasattr(m, "main") else m.__dict__[f"falsify_{mod.split('_')[-1]}_operator"]()


if __name__ == "__main__":
    falsify_DF_operator()
