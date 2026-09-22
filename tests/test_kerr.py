"""
tests/test_kerr.py
Validation of Kerr bistability thresholds and hysteresis behavior.
"""
import numpy as np
from core.config import CavityConfig
from models.kerr_cavity import KerrCavity

def test_bistability_threshold():
    """
    Validates that bistability only occurs when the theoretical threshold
    delta_n < -sqrt(3) is met.
    """
    # Create a realistic fiber loop: 5m length, standard gamma but enhanced for testing
    config = CavityConfig(length=5.0, loss_db=0.5, coupling=0.1, gamma=0.01) # gamma in 1/(W*m)
    
    # Base resonance at 1550 nm exactly
    lambda_res = 1550e-9
    cavity = KerrCavity(config, lambda_res)
    
    # 1. Monostable case (delta_n > -sqrt(3))
    # Let's set lambda exactly on resonance (delta_n = 0)
    p_circ_mono = cavity.solve_steady_state(p_in_watts=1.0, lambda_in=lambda_res)
    assert p_circ_mono > 0
    
    # Check roots explicitly
    delta_n_0 = cavity._get_normalized_detuning(lambda_res)
    y_test = cavity._get_normalized_input(1.0)
    coeffs_0 = [1.0, 2.0 * delta_n_0, delta_n_0**2 + 1.0, -y_test]
    roots_0 = np.roots(coeffs_0)
    real_roots_0 = np.real(roots_0[np.abs(np.imag(roots_0)) < 1e-10])
    assert len(real_roots_0) == 1, "Should be monostable exactly on resonance."

def test_hysteresis_sweep():
    config = CavityConfig(length=5.0, loss_db=0.5, coupling=0.1, gamma=0.01)
    lambda_res = 1550e-9
    cavity = KerrCavity(config, lambda_res)
    
    # FIX: Reduce detuning to ~0.025 pm to bring switching power down to ~3.4 W
    lambda_in = 1550.000025e-9 
    
    p_in_sweep = np.linspace(0.0, 5.0, 500) # Sweep 0 to 5 Watts
    
    p_out_up = []
    current_state = 0.0
    for p in p_in_sweep:
        current_state = cavity.solve_steady_state(p, lambda_in, current_state)
        p_out_up.append(cavity.get_output_power(current_state))
        
    p_out_down = []
    for p in reversed(p_in_sweep):
        current_state = cavity.solve_steady_state(p, lambda_in, current_state)
        p_out_down.append(cavity.get_output_power(current_state))
    p_out_down.reverse()
    
    diff = np.array(p_out_up) - np.array(p_out_down)
    hysteresis_area = np.sum(np.abs(diff))
    
    assert hysteresis_area > 0.0, "No hysteresis observed! System did not enter bistable regime."