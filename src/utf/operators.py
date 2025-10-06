# src/utf/operators.py
# UTF-2.0 Modular Operator Library
# Author: Boonsup Waikham | UTF-2.0 Beta | 2025-10-06

import numpy as np

class Transmutor:
    """
    Operator T̂: Quantum Transmutation
    ---------------------------------
    Models mass–energy conversion and defines α (conversion efficiency).
    """
    def __init__(self, mass_defect, c=3e8):
        self.mass_defect = mass_defect  # in kg
        self.c = c

    def compute_alpha(self, energy_out):
        """Compute α = E_out / (Δm c^2)"""
        denom = self.mass_defect * self.c ** 2
        return np.nan if denom == 0 else energy_out / denom

    def simulate(self, t):
        """Toy dynamic for α(t)"""
        return 0.001 * (1 + 0.1 * np.sin(2 * np.pi * t / 5))


class Transducer:
    """
    Operator D̂: Thermodynamic Transduction
    ---------------------------------------
    Models energy downconversion / decoherence efficiency.
    Defines β = E_out / E_in.
    """
    def __init__(self, E_in):
        self.E_in = E_in

    def compute_beta(self, E_out):
        """Compute β = E_out / E_in"""
        return np.nan if self.E_in == 0 else E_out / self.E_in

    def simulate(self, t):
        """Toy dynamic for β(t)"""
        return 0.6 * (1 - 0.05 * np.cos(2 * np.pi * t / 10))


class Transfuser:
    """
    Operator F̂: Classical Transfusion / Chaos
    -----------------------------------------
    Models energy cascade and chaotic amplification.
    Defines λ (Lyapunov exponent) and exponential growth.
    """
    def __init__(self, lambda0=0.1):
        self.lambda0 = lambda0

    def compute_lambda(self, beta, beta0=0.6):
        """Compute λ as nonlinear function of β"""
        return self.lambda0 * (1 + 0.1 * (beta / beta0))

    def amplify(self, t, lam):
        """Return normalized exponential amplification"""
        amp = np.exp(lam * t)
        return amp / np.max(amp)


class UTFSimulation:
    """
    UTF-2.0 Unified Benchmark Controller
    ------------------------------------
    Couples T̂, D̂, and F̂ operators into a reproducible pipeline.
    Outputs α(t), β(t), λ(t), and energy totals.
    """
    def __init__(self, timesteps=1000, dt=0.01):
        self.timesteps = timesteps
        self.dt = dt
        self.time = np.arange(0, timesteps * dt, dt)

        # Initialize operators
        self.T = Transmutor(mass_defect=1e-6)
        self.D = Transducer(E_in=1.0)
        self.F = Transfuser()

    def run(self):
        """Execute the UTF tri-operator simulation"""
        t = self.time
        alpha = self.T.simulate(t)
        beta = self.D.simulate(t)
        lam = self.F.compute_lambda(beta)
        E_T = alpha
        E_D = beta
        E_F = self.F.amplify(t, lam)
        E_total = (E_T + E_D + E_F) / np.max(E_T + E_D + E_F)

        return {
            "time": t,
            "alpha": alpha,
            "beta": beta,
            "lambda": lam,
            "E_total": E_total
        }

# --- Example usage ---
if __name__ == "__main__":
    utf = UTFSimulation()
    results = utf.run()
    print("✅ UTF-2.0 simulation completed.")
    print(f"α range: {results['alpha'].min():.4f}-{results['alpha'].max():.4f}")
    print(f"β range: {results['beta'].min():.4f}-{results['beta'].max():.4f}")
    print(f"λ range: {results['lambda'].min():.4f}-{results['lambda'].max():.4f}")
