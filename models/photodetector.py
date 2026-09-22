"""
models/photodetector.py
Photodiode, Transimpedance Amplifier (TIA), and ADC digitization twin.
"""
from dataclasses import dataclass
import numpy as np
from core.constants import Q_ELEM, K_BOLTZMANN

@dataclass
class PhotodetectorConfig:
    responsivity: float = 0.85          # [A/W] at 1550 nm
    dark_current: float = 1.0e-9        # [A]
    bandwidth_hz: float = 50.0e6        # [Hz] (50 MHz)
    transimpedance_gain: float = 10.0e3 # R_f [Ohms] (10 kOhm)
    temperature_k: float = 298.15       # Room temp [K]
    amp_noise_density: float = 2.0e-12  # TIA noise density [A/sqrt(Hz)]
    adc_bits: int = 14                  # 14-bit ADC
    v_min: float = 0.0                  # ADC Min Voltage [V]
    v_max: float = 2.5                  # ADC Max Voltage [V]

class PhotodetectorSystem:
    def __init__(self, config: PhotodetectorConfig, seed: int = 42):
        self.config = config
        self.rng = np.random.default_rng(seed)

    def process_optical_power(self, p_opt: np.ndarray) -> np.ndarray:
        """
        Converts optical power into digitized ADC voltage values, accounting for 
        photocurrent, shot noise, thermal noise, amplifier noise, and quantization.
        """
        # 1. Primary Photocurrent Generation
        i_ph = self.config.responsivity * np.maximum(p_opt, 0.0)
        
        # 2. Calculate Noise Variances
        b_hz = self.config.bandwidth_hz
        
        # Shot noise: sigma^2 = 2 * q * (I_ph + I_dark) * B
        var_shot = 2.0 * Q_ELEM * (i_ph + self.config.dark_current) * b_hz
        
        # Thermal noise: sigma^2 = (4 * k_B * T / R_f) * B
        var_thermal = (4.0 * K_BOLTZMANN * self.config.temperature_k / self.config.transimpedance_gain) * b_hz
        
        # Amplifier input-referred noise: sigma^2 = i_amp^2 * B
        var_amp = (self.config.amp_noise_density ** 2) * b_hz
        
        # Total Noise Current Standard Deviation per sample
        sigma_total_i = np.sqrt(var_shot + var_thermal + var_amp)
        
        # Sample random Gaussian noise
        i_noise = self.rng.normal(0.0, sigma_total_i, size=p_opt.shape)
        
        # Total Current
        i_total = np.maximum(i_ph + i_noise, 0.0)
        
        # 3. Transimpedance Amplification (Current to Voltage)
        v_analog = i_total * self.config.transimpedance_gain
        
        # 4. Analog-to-Digital Conversion (ADC)
        n_levels = 2**self.config.adc_bits - 1
        v_step = (self.config.v_max - self.config.v_min) / n_levels
        
        v_clamped = np.clip(v_analog, self.config.v_min, self.config.v_max)
        adc_counts = np.round((v_clamped - self.config.v_min) / v_step)
        v_digitized = self.config.v_min + adc_counts * v_step
        
        return v_digitized