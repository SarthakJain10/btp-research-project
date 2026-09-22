"""
analysis/sensitivity.py
Local sensitivity analysis and parameter perturbation sweeps.
"""
from dataclasses import dataclass
from typing import Callable, Dict
import numpy as np

@dataclass
class SensitivityResult:
    parameter_name: str
    nominal_val: float
    perturbed_val: float
    output_nominal: float
    output_perturbed: float
    relative_sensitivity: float

class SensitivityAnalyzer:
    """Calculates local sensitivity indices Sx = (delta_y / y0) / (delta_x / x0)."""
    
    @staticmethod
    def compute_local_sensitivity(
        eval_func: Callable[[float], float],
        nominal_param: float,
        perturbation_fraction: float = 0.05,
        param_name: str = "parameter"
    ) -> SensitivityResult:
        """
        Perturbs a single parameter by perturbation_fraction (default +5%) 
        and computes the normalized sensitivity index.
        """
        y0 = eval_func(nominal_param)
        x_perturbed = nominal_param * (1.0 + perturbation_fraction)
        y_perturbed = eval_func(x_perturbed)
        
        dy_rel = (y_perturbed - y0) / y0 if y0 != 0 else (y_perturbed - y0)
        dx_rel = perturbation_fraction
        
        s_x = dy_rel / dx_rel
        
        return SensitivityResult(
            parameter_name=param_name,
            nominal_val=nominal_param,
            perturbed_val=x_perturbed,
            output_nominal=y0,
            output_perturbed=y_perturbed,
            relative_sensitivity=s_x
        )