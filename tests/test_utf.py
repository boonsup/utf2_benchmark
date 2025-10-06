# tests/test_utf.py
# UTF-2.0 Pytest Validation Suite
# Author: Boonsup Waikham | 2025-10-06
# ---------------------------------------
# Run with:
#     pytest -v tests/test_utf.py
# ---------------------------------------

import numpy as np
import pytest
from src.utf.operators import Transmutor, Transducer, Transfuser, UTFSimulation

# --- Fixtures ---------------------------------------------------------------

@pytest.fixture
def utf_sim():
    """Fixture: initialize a UTF simulation instance."""
    return UTFSimulation(timesteps=500, dt=0.01)

# --- α Tests: Transmutor ----------------------------------------------------

def test_alpha_computation():
    """Verify α = E_out / (Δm c^2) yields expected range."""
    T = Transmutor(mass_defect=1e-6)
    alpha = T.compute_alpha(energy_out=9e10)  # 9e10 J for 1e-6 kg mass defect
    assert np.isclose(alpha, 1.0, rtol=1e-3), "α should be ≈ 1 for E=mc²"
    dynamic = T.simulate(np.linspace(0, 10, 100))
    assert 0.0009 < np.mean(dynamic) < 0.0011, "α dynamic mean out of range"

# --- β Tests: Transducer ----------------------------------------------------

def test_beta_computation():
    """Verify β = E_out / E_in behaves correctly."""
    D = Transducer(E_in=10)
    beta = D.compute_beta(E_out=6)
    assert np.isclose(beta, 0.6, atol=1e-3), "β computation mismatch"
    dynamic = D.simulate(np.linspace(0, 10, 100))
    assert 0.57 < np.mean(dynamic) < 0.63, "β dynamic mean out of range"

# --- λ Tests: Transfuser ----------------------------------------------------

def test_lambda_behavior():
    """Verify λ scales with β."""
    F = Transfuser(lambda0=0.1)
    beta_values = np.array([0.3, 0.6, 0.9])
    lambda_values = [F.compute_lambda(b) for b in beta_values]
    assert lambda_values[0] < lambda_values[1] < lambda_values[2], \
        "λ should increase with β"
    amp = F.amplify(np.linspace(0, 5, 50), 0.1)
    assert np.all(amp >= 0) and np.all(amp <= 1), "Amplification not normalized"

# --- Coupled Simulation Tests ----------------------------------------------

def test_utf_simulation_runs(utf_sim):
    """Verify UTF simulation executes and produces consistent data."""
    results = utf_sim.run()
    for key in ["time", "alpha", "beta", "lambda", "E_total"]:
        assert key in results, f"Missing key in UTF results: {key}"
        assert len(results[key]) == utf_sim.timesteps, "Incorrect array length"

def test_energy_conservation(utf_sim):
    """Check normalized total energy remains bounded [0, 1]."""
    results = utf_sim.run()
    E_total = results["E_total"]
    assert np.all(E_total >= 0) and np.all(E_total <= 1), \
        "Energy not normalized within [0,1]"
    assert np.isclose(np.max(E_total), 1.0, atol=1e-6), \
        "Energy normalization peak must be 1"

# --- Regression Stability ---------------------------------------------------

def test_regression_stability(utf_sim):
    """Ensure α, β, λ means stay within stable expected envelopes."""
    results = utf_sim.run()
    α_mean = np.mean(results["alpha"])
    β_mean = np.mean(results["beta"])
    λ_mean = np.mean(results["lambda"])
    assert 0.0008 < α_mean < 0.0012, "α mean drifted outside range"
    assert 0.55 < β_mean < 0.65, "β mean drifted outside range"
    assert 0.09 < λ_mean < 0.11, "λ mean drifted outside range"


from utf.falsification import (
    test_T_energy_nonconservation,
    test_D_decoherence_violation,
    test_F_false_chaos_amplification,
    test_DF_coupling_variation,
)

def test_falsification_suite():
    assert test_T_energy_nonconservation.falsify_T_operator()
    assert test_D_decoherence_violation.falsify_D_operator()
    assert test_F_false_chaos_amplification.falsify_F_operator()
    assert test_DF_coupling_variation.falsify_DF_operator()
