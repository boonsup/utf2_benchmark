# -*- coding: utf-8 -*-
"""
Toy model: Composite superoperator ℒ_UTF = ℒ_T + ℒ_D + ℒ_F + η[ℒ_D, ℒ_F]

- 2-level density matrix ρ (2x2)
- ℒ_T : unitary drive (σ_x) with frequency ω (energy exchange proxy α)
- ℒ_D : single Lindblad jump (σ_z dephasing) with rate γ (transduction efficiency β)
- ℒ_F : classical chaos kernel couples as weak stochastic Hamiltonian modulation via λ
- η   : commutator coupling strength between ℒ_D and ℒ_F (formal “bridge” term)

Outputs:
- time series of Tr(ρ H), “energy” proxy E(t)
- boundedness statistics and drift
"""
from __future__ import annotations
import numpy as np
from dataclasses import dataclass
from pathlib import Path

σx = np.array([[0, 1], [1, 0]], dtype=complex)
σy = np.array([[0, -1j], [1j, 0]], dtype=complex)
σz = np.array([[1, 0], [0, -1]], dtype=complex)
I2 = np.eye(2, dtype=complex)

def dagger(A): return A.conj().T

def lindblad(ρ, L):
    return L @ ρ @ dagger(L) - 0.5*(dagger(L)@L@ρ + ρ@dagger(L)@L)

@dataclass
class UTFParams:
    omega: float = 1.0     # unitary drive frequency (maps to α proxy)
    gamma: float = 0.6     # dephasing rate (β proxy)
    lam: float = 0.10      # chaos sensitivity (λ)
    eta: float = 0.10      # commutator coupling
    dt: float = 0.01
    steps: int = 5000
    seed: int | None = 0
    noise_sigma: float = 0.0  # stochastic modulation magnitude (DF coupling noise)

class CoupledUTFSimulator:
    """
    Minimal, self-contained integrator for 2x2 density matrix under ℒ_UTF.
    """
    def __init__(self, params: UTFParams):
        self.p = params
        self.rng = np.random.default_rng(params.seed)

    def _H_t(self, t, x):
        """Time-dependent Hamiltonian with weak chaos modulation via x(t)∈[0,1]."""
        # base drive + small σy perturbation scaled by lam and noise
        ω = self.p.omega
        ε = 0.15 * self.p.lam * (x - 0.5)  # centered modulation
        return 0.5*ω*σx + ε*σy

    def _logistic_step(self, x, r):
        return np.clip(r*x*(1.0 - x), 0.0, 1.0)

    def _L_T(self, ρ, H):
        # unitary von Neumann part
        return -1j*(H@ρ - ρ@H)

    def _L_D(self, ρ):
        # pure dephasing channel with Lindblad L = sqrt(gamma)*σz
        L = np.sqrt(max(self.p.gamma, 0.0)) * σz
        return lindblad(ρ, L)

    def _L_F(self, ρ, xdot):
        # couple classical rate into an anti-Hermitian kicker ~ ẋ σy
        # small to keep toy bounded
        k = 0.1 * self.p.lam * xdot
        K = 1j * k * σy
        return K@ρ - ρ@K

    def _commutator_term(self, ρ, Ldρ, Lfρ):
        # η [ℒ_D, ℒ_F] ρ  ≈ η (ℒ_D(ℒ_F(ρ)) - ℒ_F(ℒ_D(ρ)))
        return self.p.eta * ( self._L_D(Lfρ) - self._L_F(Ldρ, xdot=0.0) )

    def run(self, ρ0: np.ndarray | None = None, r: float = 3.8):
        p = self.p
        if ρ0 is None:
            # start in +x eigenstate: |+⟩⟨+|
            plus = (1/np.sqrt(2)) * np.array([[1],[1]], dtype=complex)
            ρ = plus @ dagger(plus)
        else:
            ρ = ρ0.astype(complex)

        # init logistic, warmup
        x0 = 0.5 + 1e-6
        x1 = 0.5
        for _ in range(100):
            x0 = self._logistic_step(x0, r)
            x1 = self._logistic_step(x1, r)

        # measure “energy” w.r.t H_base (constant) as proxy
        H_base = 0.5*p.omega*σx
        E_trace = []
        drift_trace = []

        x = x0
        for n in range(p.steps):
            # chaos update + stochastic perturbation
            x_prev = x
            x = self._logistic_step(x, r)
            if p.noise_sigma > 0:
                x = np.clip(x + self.rng.normal(0, p.noise_sigma), 0.0, 1.0)
            xdot = (x - x_prev) / p.dt

            # generators
            Ht = self._H_t(n*p.dt, x)
            LT = self._L_T(ρ, Ht)
            LD = self._L_D(ρ)
            LF = self._L_F(ρ, xdot)

            Lcomm = self._commutator_term(ρ, LD, LF)

            # Euler step (small dt; toy level)
            dρ = (LT + LD + LF + Lcomm) * p.dt
            ρ = ρ + dρ

            # re-Hermitize and renormalize to mitigate numeric drift
            ρ = 0.5*(ρ + dagger(ρ))
            ρ = ρ / np.trace(ρ).real

            E = np.real(np.trace(ρ @ H_base))
            E_trace.append(E)

            if n > 10:
                μ = np.mean(E_trace[max(0, n-200):n])
                drift_trace.append(abs(E - μ))

        E_arr = np.array(E_trace)
        drift_arr = np.array(drift_trace) if drift_trace else np.array([0.0])
        stats = {
            "E_mean": float(E_arr.mean()),
            "E_std": float(E_arr.std()),
            "drift_mean": float(drift_arr.mean()),
            "drift_max": float(drift_arr.max()) if drift_arr.size else 0.0,
        }
        return E_arr, stats

def tau_crit(lam_max: float) -> float:
    """Analytical tolerance bound (toy): τ_crit ≈ 1/(2 λ_max)."""
    lam_max = max(lam_max, 1e-8)
    return 1.0/(2.0*lam_max)
