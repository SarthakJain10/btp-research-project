"""
models/fbg.py
Fiber Bragg Grating physical models.
"""
import numpy as np
from core.config import FBGConfig
from core.constants import STRAIN_OPTIC_COEFF_SILICA, THERMAL_EXPANSION_SILICA, THERMO_OPTIC_COEFF_SILICA

class FBGModel:
    def __init__(self, config: FBGConfig):
        self.config = config
        self.base_lambda_b = config.lambda_b
        self.current_lambda_b = config.lambda_b
        
    def apply_environment(self, strain: float = 0.0, delta_t: float = 0.0):
        """
        Calculates physical wavelength shift due to strain and temperature.
        strain: defined in microstrain (uE) converted to absolute.
        delta_t: temperature change in Kelvin/Celsius.
        """
        strain_term = (1.0 - STRAIN_OPTIC_COEFF_SILICA) * strain
        temp_term = (THERMAL_EXPANSION_SILICA + THERMO_OPTIC_COEFF_SILICA) * delta_t
        shift = self.base_lambda_b * (strain_term + temp_term)
        self.current_lambda_b = self.base_lambda_b + shift
        return self.current_lambda_b

class FBGLorentzian(FBGModel):
    """Simplified Lorentzian FBG model for baseline comparisons."""
    def __init__(self, config: FBGConfig, fwhm: float = 0.2e-9, r_max: float = 0.9):
        super().__init__(config)
        self.fwhm = fwhm
        self.r_max = r_max
        
    def reflectivity(self, wavelengths: np.ndarray) -> np.ndarray:
        half_width = self.fwhm / 2.0
        return self.r_max * (half_width**2) / ((wavelengths - self.current_lambda_b)**2 + half_width**2)

class FBGPhysical(FBGModel):
    """Rigorous Coupled-Mode Theory FBG model."""
    def reflectivity(self, wavelengths: np.ndarray) -> np.ndarray:
        # Convert to complex to handle gamma mathematically when delta > kappa
        delta = 2 * np.pi * self.config.n_eff * (1.0 / wavelengths - 1.0 / self.current_lambda_b)
        kappa = np.pi * self.config.delta_n / self.current_lambda_b
        
        # gamma can be purely imaginary outside the bandgap
        gamma = np.sqrt(kappa**2 - delta**2 + 0j)
        
        numerator = -1j * kappa * np.sinh(gamma * self.config.length)
        denominator = gamma * np.cosh(gamma * self.config.length) + 1j * delta * np.sinh(gamma * self.config.length)
        
        r = numerator / denominator
        return np.abs(r)**2