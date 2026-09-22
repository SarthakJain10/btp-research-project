"""
processing/bistable.py
Switching-event detection algorithms for nonlinear interrogation.
"""
import numpy as np

class BistableInterrogator:
    @staticmethod
    def detect_switch_wavelength(wavelengths: np.ndarray, output_signal: np.ndarray, 
                                 direction: str = 'up') -> float:
        """
        Detects the exact wavelength where the Kerr cavity switches branches.
        Operates by finding the maximum discrete derivative (edge detection).
        
        direction: 'up' detects the low-to-high jump, 'down' detects high-to-low.
        """
        # Calculate instantaneous derivative (dy/dx)
        # Using np.gradient to handle non-uniform wavelength steps if they exist
        derivative = np.gradient(output_signal, wavelengths)
        
        if direction == 'up':
            # Looking for the sharpest positive spike
            switch_idx = np.argmax(derivative)
        elif direction == 'down':
            # Looking for the sharpest negative spike
            switch_idx = np.argmin(derivative)
        else:
            raise ValueError("Direction must be 'up' or 'down'")
            
        # Optional: Add a confidence check. If the max derivative isn't significantly 
        # larger than the background noise, the switch might have failed/been missed.
        median_deriv = np.median(np.abs(derivative))
        if np.abs(derivative[switch_idx]) < 5.0 * median_deriv:
            # Switch event is indistinguishable from noise (Missed-switch probability)
            return np.nan 
            
        return wavelengths[switch_idx]

    @staticmethod
    def calculate_hysteresis_width(w_up: float, w_down: float) -> float:
        """Returns the hysteresis width in meters."""
        return np.abs(w_up - w_down)