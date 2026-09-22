"""
models/resonator.py
Linear models for the optical resonator cavity.
"""
import numpy as np
from core.config import CavityConfig
from core.utils import db_to_linear

class RingResonator:
    """
    Physical Add-Drop Ring Resonator model.
    Models the drop port transmission which interacts with the FBG reflection.
    """
    def __init__(self, config: CavityConfig):
        self.config = config
        
    def transmission(self, wavelengths: np.ndarray) -> np.ndarray:
        """Calculates power transmission of the drop port."""
        # Phase accumulation
        phi = (2 * np.pi * self.config.n_eff * self.config.length) / wavelengths
        
        # Amplitude transmission factor (a) based on loss
        # config.loss_db is round-trip power loss. 
        # a is round-trip amplitude factor: a = sqrt(power_transmission)
        power_trans = db_to_linear(-self.config.loss_db)
        a = np.sqrt(power_trans)
        
        # t is amplitude transmission of the coupler: t = sqrt(1 - kappa)
        t = np.sqrt(1.0 - self.config.coupling)
        
        numerator = ((1 - t**2)**2) * a
        denominator = (1 - t**2 * a)**2 + 4 * (t**2) * a * np.sin(phi / 2)**2
        
        return numerator / denominator
        
    def get_fwhm(self, lambda_res: float) -> float:
        """Analytical estimation of resonator linewidth (FWHM) in meters."""
        a = np.sqrt(db_to_linear(-self.config.loss_db))
        t = np.sqrt(1.0 - self.config.coupling)
        FSR = lambda_res**2 / (self.config.n_eff * self.config.length)
        finesse = (np.pi * t * np.sqrt(a)) / (1 - t**2 * a)
        return FSR / finesse