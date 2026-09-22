"""
core/config.py
Structured parameter definitions using dataclasses. 
Ensures all parameters are tracked and reproducible.
"""
from dataclasses import dataclass
import numpy as np

@dataclass
class FBGConfig:
    lambda_b: float = 1550e-9  # Nominal Bragg wavelength [m]
    length: float = 10e-3      # Grating length [m]
    delta_n: float = 1e-4      # Index modulation amplitude
    n_eff: float = 1.447       # Effective refractive index
    alpha: float = 0.0         # Loss coefficient [1/m]

@dataclass
class CavityConfig:
    length: float = 5.0        # Cavity length (e.g. fiber loop) [m]
    loss_db: float = 0.5       # Round trip linear loss [dB]
    coupling: float = 0.1      # Power coupling coefficient (kappa)
    gamma: float = 10.0        # Nonlinear parameter [1/(W*km)] -> carefully handle units later!
    n_eff: float = 1.447       # Effective index

@dataclass
class LaserConfig:
    power_w: float = 0.1             # Nominal continuous wave power [W]
    lambda_0: float = 1550e-9
    linewidth_hz: float = 100e3      # Laser linewidth [Hz]
    rin_db_hz: float = -140.0        # Relative Intensity Noise [dB/Hz]
    wavelength_drift_m: float = 1e-12 # Slow systematic drift [m]

@dataclass
class SimConfig:
    num_samples: int = 2000
    random_seed: int = 42
    wavelength_start: float = 1549.5e-9
    wavelength_end: float = 1550.5e-9