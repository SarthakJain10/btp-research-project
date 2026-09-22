"""
tests/test_models.py
Validation of FBG and Resonator physical limits.
"""
import numpy as np
from core.config import FBGConfig, CavityConfig
from models.fbg import FBGLorentzian, FBGPhysical
from models.resonator import RingResonator

def test_fbg_reflectivity_bounds():
    config = FBGConfig(lambda_b=1550e-9, length=10e-3, delta_n=1e-4)
    wavelengths = np.linspace(1548e-9, 1552e-9, 1000)
    
    fbg = FBGPhysical(config)
    R = fbg.reflectivity(wavelengths)
    
    assert np.all(R >= 0.0), "Reflectivity must be >= 0"
    assert np.all(R <= 1.000001), "Reflectivity cannot exceed 1.0"
    # Max reflectivity should be at Bragg wavelength
    idx_max = np.argmax(R)
    assert np.isclose(wavelengths[idx_max], 1550e-9, atol=1e-11)

def test_environmental_shift():
    config = FBGConfig(lambda_b=1550e-9)
    fbg = FBGPhysical(config)
    
    # +10 degrees C shift -> expecting approx 90-100 pm shift
    new_lambda = fbg.apply_environment(delta_t=10.0)
    shift = new_lambda - 1550e-9
    assert 80e-12 < shift < 150e-12, "Temperature shift is out of physical bounds"

def test_resonator_transmission():
    config = CavityConfig(length=0.1, loss_db=0.5, coupling=0.1)
    ring = RingResonator(config)
    wavelengths = np.linspace(1549e-9, 1551e-9, 5000)
    
    T = ring.transmission(wavelengths)
    
    assert np.all(T >= 0.0)
    assert np.all(T <= 1.0)
    assert np.max(T) > 0.0, "Resonator should have non-zero transmission peaks"