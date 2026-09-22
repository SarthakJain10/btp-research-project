"""
core/utils.py
Utility functions for unit conversions and standard optical math.
"""
import numpy as np

def db_to_linear(db_value: float) -> float:
    """Converts optical loss/gain from dB to a linear power ratio."""
    return 10.0 ** (db_value / 10.0)

def linear_to_db(linear_value: float) -> float:
    """Converts linear power ratio to dB."""
    if np.any(linear_value <= 0):
        raise ValueError("Linear ratio must be > 0 to convert to dB.")
    return 10.0 * np.log10(linear_value)

def dbm_to_watt(dbm_value: float) -> float:
    """Converts optical power from dBm to Watts."""
    return (10.0 ** (dbm_value / 10.0)) / 1000.0

def watt_to_dbm(watt_value: float) -> float:
    """Converts optical power from Watts to dBm."""
    if np.any(watt_value <= 0):
        raise ValueError("Power must be > 0 to convert to dBm.")
    return 10.0 * np.log10(watt_value * 1000.0)

def freq_to_wavelength(freq_hz: float) -> float:
    """Converts frequency [Hz] to wavelength [m]."""
    from .constants import C_LIGHT
    return C_LIGHT / freq_hz

def wavelength_to_freq(wavelength_m: float) -> float:
    """Converts wavelength [m] to frequency [Hz]."""
    from .constants import C_LIGHT
    return C_LIGHT / wavelength_m