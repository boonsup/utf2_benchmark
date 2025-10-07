# -*- coding: utf-8 -*-
import numpy as np
import sys, os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.utf.models.coupled_superop import UTFParams, CoupledUTFSimulator, tau_crit

def test_tau_crit_monotone():
    assert tau_crit(0.2) < tau_crit(0.1)

def test_bounded_without_noise():
    p = UTFParams(lam=0.10, eta=0.10, noise_sigma=0.0, steps=2000, dt=0.01, seed=1)
    sim = CoupledUTFSimulator(p)
    E, stats = sim.run(r=3.80)
    assert stats["drift_mean"] < tau_crit(p.lam)

def test_robust_under_small_noise():
    p = UTFParams(lam=0.10, eta=0.10, noise_sigma=1e-3, steps=2000, dt=0.01, seed=2)
    sim = CoupledUTFSimulator(p)
    E, stats = sim.run(r=3.80)
    assert stats["drift_mean"] < 1.5 * tau_crit(p.lam)  # allow slight relaxation

def test_energy_trace_is_real_finite():
    p = UTFParams()
    sim = CoupledUTFSimulator(p)
    E, _ = sim.run()
    assert np.isfinite(E).all()
    assert np.isreal(E).all()
