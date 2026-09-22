"""
tests/test_utils.py
Unit tests for utility functions.
Run using: pytest tests/
"""
import numpy as np
from core.utils import db_to_linear, linear_to_db, dbm_to_watt, watt_to_dbm, freq_to_wavelength, wavelength_to_freq
from core.constants import C_LIGHT

def test_db_linear_conversion():
    assert np.isclose(db_to_linear(3.0), 1.99526, rtol=1e-4)
    assert np.isclose(linear_to_db(2.0), 3.0103, rtol=1e-4)

def test_power_conversion():
    assert np.isclose(dbm_to_watt(0.0), 1e-3)
    assert np.isclose(watt_to_dbm(1.0), 30.0)

def test_wavelength_freq_conversion():
    freq = 193.1e12  # ~1550 nm in Hz
    wl = freq_to_wavelength(freq)
    assert np.isclose(wl, C_LIGHT / freq)
    assert np.isclose(wavelength_to_freq(wl), freq)