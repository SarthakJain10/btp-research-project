"""
tests/test_algorithms.py
Validation of DSP architectures.
"""
import numpy as np
from processing.conventional import ConventionalInterrogator
from processing.bistable import BistableInterrogator

def test_centroid_accuracy():
    wavelengths = np.linspace(1549e-9, 1551e-9, 1000)
    true_peak = 1550.25e-9
    
    # Create perfect Gaussian
    spectrum = np.exp(-((wavelengths - true_peak)**2) / (0.1e-9)**2)
    
    est_peak = ConventionalInterrogator.centroid(wavelengths, spectrum)
    assert np.isclose(est_peak, true_peak, atol=1e-12)

def test_bistable_edge_detection():
    wavelengths = np.linspace(1549e-9, 1551e-9, 1000)
    signal = np.zeros_like(wavelengths)
    
    # Create a synthetic step-function at index 500 (1550.0 nm)
    signal[500:] = 1.0 
    
    # Add minor noise
    np.random.seed(42)
    signal += np.random.normal(0, 0.05, len(signal))
    
    w_up = BistableInterrogator.detect_switch_wavelength(wavelengths, signal, 'up')
    
    # Should detect the jump at index 500
    assert np.isclose(w_up, wavelengths[500], atol=1e-11)