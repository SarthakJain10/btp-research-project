"""
models/laser.py
Optical laser source with RIN, linewidth phase noise, and drift models.
"""
import numpy as np
from core.config import LaserConfig
from core.constants import C_LIGHT

class LaserSource:
    def __init__(self, config: LaserConfig, seed: int = 42):
        self.config = config
        self.rng = np.random.default_rng(seed)

    def generate_signal(self, time_array: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
        """
        Generates noisy laser output over time.
        
        Returns:
            power_t: Optical power array [W]
            wavelength_t: Laser output wavelength array [m]
        """
        num_samples = len(time_array)
        dt = time_array[1] - time_array[0] if num_samples > 1 else 1e-6
        
        # 1. Deterministic Drifts
        power_drift = self.config.power_w * (1.0 + 0.001 * time_array)  # 0.1%/s drift
        wl_drift = self.config.lambda_0 + self.config.wavelength_drift_m * time_array
        
        # 2. Relative Intensity Noise (RIN)
        rin_linear = 10.0 ** (self.config.rin_db_hz / 10.0)
        # Bandwidth equivalent to Nyquist frequency 1/(2*dt)
        bandwidth = 1.0 / (2.0 * dt)
        sigma_p = self.config.power_w * np.sqrt(rin_linear * bandwidth)
        power_noise = self.rng.normal(0.0, sigma_p, num_samples)
        power_t = np.maximum(power_drift + power_noise, 0.0)
        
        # 3. Frequency / Phase Noise (Linewidth)
        sigma_freq = np.sqrt(self.config.linewidth_hz / (2.0 * np.pi * dt))
        freq_inst = self.rng.normal(0.0, sigma_freq, num_samples)
        # Convert frequency fluctuations to wavelength fluctuations: d_lambda = - (lambda^2 / c) * d_freq
        wl_noise = - (self.config.lambda_0**2 / C_LIGHT) * freq_inst
        wavelength_t = wl_drift + wl_noise
        
        return power_t, wavelength_t