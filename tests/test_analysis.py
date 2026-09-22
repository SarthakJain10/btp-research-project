"""
tests/test_analysis.py
Unit tests for sensitivity analysis and GUM uncertainty budget logic.
"""
import numpy as np
from analysis.sensitivity import SensitivityAnalyzer
from analysis.uncertainty import UncertaintyBudget

def test_local_sensitivity_linear():
    # Linear function y = 2 * x -> dy/dx = 2. Relative sensitivity S_x should be 1.0
    func = lambda x: 2.0 * x
    res = SensitivityAnalyzer.compute_local_sensitivity(func, nominal_param=10.0, perturbation_fraction=0.1)
    
    assert np.isclose(res.relative_sensitivity, 1.0, rtol=1e-5)

def test_gum_uncertainty_budget():
    budget = UncertaintyBudget(target_name="Bragg Wavelength Shift", target_unit="m")
    
    # Laser drift: 0.5 pm standard uncertainty, sensitivity = 1.0
    budget.add_component("Laser Drift", u_x=0.5e-12, c_i=1.0, unit="m")
    # Temperature drift: 0.1 K standard uncertainty, sensitivity = 10 pm/K
    budget.add_component("Thermal Drift", u_x=0.1, c_i=10e-12, unit="K")
    
    res = budget.calculate_budget(coverage_factor=2.0)
    
    # Combined var = (0.5e-12)^2 + (1.0e-12)^2 = 1.25e-24 -> u_c = 1.118 pm
    expected_uc = np.sqrt((0.5e-12)**2 + (1.0e-12)**2)
    assert np.isclose(res['combined_standard_uncertainty'], expected_uc, rtol=1e-4)
    assert np.isclose(res['expanded_uncertainty'], 2.0 * expected_uc, rtol=1e-4)