"""
simulation/monte_carlo.py
Executes repeated statistical trials to evaluate RMSE and robust operating conditions.
"""
import numpy as np
from core.config import FBGConfig, CavityConfig, LaserConfig, SimConfig
from models.photodetector import PhotodetectorConfig
from simulation.orchestrator import VirtualInterrogator

class MonteCarloStudy:
    def __init__(self, trials: int = 100):
        self.trials = trials
        
    def run_noise_study(self, strain_target: float = 10.0):
        """
        Evaluates measurement precision for a given strain under random noise.
        strain_target in microstrain.
        """
        conv_errors = []
        bistable_errors = []
        missed_switches = 0
        
        for t in range(self.trials):
            # Re-seed configurations for independent noise per trial
            sim_cfg = SimConfig(num_samples=1000, random_seed=42+t, 
                                wavelength_start=1549.9e-9, wavelength_end=1550.1e-9)
            
            # Using slightly elevated laser power to guarantee we hit the bistable threshold 
            # based on our physics fix from Iteration 4
            laser_cfg = LaserConfig(power_w=3.5, lambda_0=1550e-9) 
            
            interrogator = VirtualInterrogator(
                FBGConfig(), CavityConfig(), laser_cfg, PhotodetectorConfig(), sim_cfg
            )
            
            results = interrogator.run_sweep(strain_ue=strain_target)
            true_wl = results['true_lambda_b']
            
            # Record Conventional Error
            if not np.isnan(results['est_conv']):
                conv_errors.append(results['est_conv'] - true_wl)
                
            # Record Bistable Error
            if np.isnan(results['est_switch']):
                missed_switches += 1
            else:
                # The switch happens at an offset from the true peak (due to detuning requirement)
                # In a real system, this constant offset is calibrated out.
                # We record the variance of the switch point as the primary metric for precision.
                bistable_errors.append(results['est_switch'])
                
        # Statistical processing
        conv_rmse = np.std(conv_errors) if conv_errors else np.nan
        bistable_precision = np.std(bistable_errors) if bistable_errors else np.nan
        
        return {
            'trials': self.trials,
            'missed_bistable_switches': missed_switches,
            'conv_rmse_pm': conv_rmse * 1e12,
            'bistable_precision_pm': bistable_precision * 1e12
        }