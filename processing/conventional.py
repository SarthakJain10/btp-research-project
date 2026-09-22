"""
processing/conventional.py
Baseline FBG interrogation algorithms applied to noisy spectra.
"""
import numpy as np
from scipy.optimize import curve_fit

class ConventionalInterrogator:
    @staticmethod
    def maximum_peak(wavelengths: np.ndarray, spectrum: np.ndarray) -> float:
        """Naive peak detection."""
        return wavelengths[np.argmax(spectrum)]

    @staticmethod
    def centroid(wavelengths: np.ndarray, spectrum: np.ndarray, threshold_db: float = 3.0) -> float:
        """
        Center-of-mass centroid detection.
        Only considers the spectrum above (peak - threshold_db).
        """
        max_val = np.max(spectrum)
        # Assuming spectrum is linear power (volts/counts proportional to power)
        # Convert threshold_db to a linear threshold fraction
        linear_fraction = 10.0 ** (-threshold_db / 10.0)
        threshold_val = max_val * linear_fraction
        
        mask = spectrum >= threshold_val
        if not np.any(mask):
            return ConventionalInterrogator.maximum_peak(wavelengths, spectrum)
            
        w_masked = wavelengths[mask]
        s_masked = spectrum[mask]
        
        return np.sum(w_masked * s_masked) / np.sum(s_masked)

    @staticmethod
    def lorentzian_fit(wavelengths: np.ndarray, spectrum: np.ndarray) -> float:
        """Least-squares fit to a Lorentzian profile for sub-picometer resolution."""
        def _lorentzian(x, x0, a, gamma, offset):
            return a * (gamma**2) / ((x - x0)**2 + gamma**2) + offset
            
        peak_idx = np.argmax(spectrum)
        x0_guess = wavelengths[peak_idx]
        a_guess = spectrum[peak_idx] - np.min(spectrum)
        
        try:
            # Fit only around the peak to avoid side-lobe interference
            mask = np.abs(wavelengths - x0_guess) < 1e-9
            popt, _ = curve_fit(
                _lorentzian, 
                wavelengths[mask], 
                spectrum[mask], 
                p0=[x0_guess, a_guess, 0.1e-9, np.min(spectrum)],
                maxfev=2000
            )
            return popt[0]
        except Exception:
            return x0_guess # Fallback to naive peak if fit fails