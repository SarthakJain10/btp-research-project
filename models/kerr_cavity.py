"""
models/kerr_cavity.py
Nonlinear optical cavity solver based on dispersive Kerr bistability.
"""
import numpy as np
from core.config import CavityConfig
from core.utils import db_to_linear

class KerrCavity:
    def __init__(self, config: CavityConfig, lambda_res: float):
        self.config = config
        self.lambda_res = lambda_res
        
        # Calculate cavity physical constants
        self.a = np.sqrt(db_to_linear(-self.config.loss_db))
        self.t = np.sqrt(1.0 - self.config.coupling)
        
        # alpha_rt is the half-width half-max in phase space
        # Assuming symmetric couplers kappa_1 = kappa_2 = coupling
        self.alpha_rt = 1.0 - (self.a * self.t**2)
        
    def _get_normalized_detuning(self, lambda_in: float) -> float:
        """Calculates normalized linear detuning delta_n."""
        # Phase detuning from nearest resonance
        phi_0 = 2 * np.pi * self.config.n_eff * self.config.length * (1.0 / lambda_in - 1.0 / self.lambda_res)
        return phi_0 / self.alpha_rt
        
    def _get_normalized_input(self, p_in_watts: float) -> np.ndarray:
        """Calculates normalized input power y."""
        return (self.config.coupling * self.config.gamma * self.config.length / (self.alpha_rt**3)) * p_in_watts

    def solve_steady_state(self, p_in_watts: float, lambda_in: float, current_state: float = None) -> float:
        """
        Finds the steady-state circulating power [W].
        If current_state is provided, models hysteresis by selecting the root closest to the current state.
        """
        delta_n = self._get_normalized_detuning(lambda_in)
        y = self._get_normalized_input(p_in_watts)
        
        # Polynomial coefficients for x^3 + 2*delta_n*x^2 + (delta_n^2 + 1)*x - y = 0
        coeffs = [1.0, 2.0 * delta_n, delta_n**2 + 1.0, -y]
        
        # Find roots
        roots = np.roots(coeffs)
        
        # Filter strictly real roots (numerical tolerance for imaginary part)
        real_roots = np.real(roots[np.abs(np.imag(roots)) < 1e-10])
        
        if len(real_roots) == 0:
            raise ValueError("No physical steady-state solution found. Check parameters.")
            
        # Convert normalized x back to physical circulating power P_c
        p_circulating_roots = real_roots * self.alpha_rt / (self.config.gamma * self.config.length)
        
        # Discard unphysical negative powers due to extreme numerical edge cases
        p_circulating_roots = p_circulating_roots[p_circulating_roots >= -1e-12]
        p_circulating_roots = np.maximum(p_circulating_roots, 0.0)
        
        if len(p_circulating_roots) == 1:
            return p_circulating_roots[0]
            
        # If bistable (3 roots), pick based on hysteresis
        p_circulating_roots.sort()
        if current_state is None:
            # Default to lower branch if no history is known
            return p_circulating_roots[0]
            
        # Find the root closest to the current state (tracking the branch)
        idx = np.argmin(np.abs(p_circulating_roots - current_state))
        
        # WARNING: The middle root (idx=1) is physically unstable. 
        # If the solver accidentally tracks to the middle root, it must "snap" to the nearest stable branch.
        if idx == 1:
            if current_state > p_circulating_roots[1]:
                return p_circulating_roots[2] # Snap up
            else:
                return p_circulating_roots[0] # Snap down
                
        return p_circulating_roots[idx]

    def get_output_power(self, p_circulating: float) -> float:
        """Calculates drop-port output power from circulating power."""
        return p_circulating * self.config.coupling