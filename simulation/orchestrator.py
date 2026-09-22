"""
simulation/orchestrator.py
Wires the physical models together into a complete virtual interrogator.
"""
import numpy as np
from core.config import FBGConfig, CavityConfig, LaserConfig, SimConfig
from models.fbg import FBGPhysical
from models.kerr_cavity import KerrCavity
from models.losses import OpticalLossBudget, LossBudgetConfig
from models.laser import LaserSource
from models.photodetector import PhotodetectorSystem, PhotodetectorConfig
from processing.conventional import ConventionalInterrogator
from processing.bistable import BistableInterrogator

class VirtualInterrogator:
    def __init__(self, fbg_cfg: FBGConfig, cav_cfg: CavityConfig, 
                 laser_cfg: LaserConfig, pd_cfg: PhotodetectorConfig, sim_cfg: SimConfig):
        self.sim_cfg = sim_cfg
        self.fbg = FBGPhysical(fbg_cfg)
        
        # Assume the cavity is designed to resonate near the FBG base wavelength
        self.cavity = KerrCavity(cav_cfg, lambda_res=fbg_cfg.lambda_b)
        self.loss_budget = OpticalLossBudget(LossBudgetConfig())
        self.laser = LaserSource(laser_cfg, seed=sim_cfg.random_seed)
        self.pd = PhotodetectorSystem(pd_cfg, seed=sim_cfg.random_seed+1)
        
    def run_sweep(self, strain_ue: float = 0.0, temp_c: float = 0.0):
        """
        Simulates a full wavelength sweep up and down, returning the digitized arrays 
        and the estimated Bragg wavelengths using both architectures.
        """
        # Apply physical environment to FBG
        true_lambda_b = self.fbg.apply_environment(strain=strain_ue, delta_t=temp_c)
        
        # Create sweep arrays
        wl_sweep_up = np.linspace(self.sim_cfg.wavelength_start, self.sim_cfg.wavelength_end, self.sim_cfg.num_samples)
        wl_sweep_down = np.flip(wl_sweep_up)
        
        # Generate laser noise (treating the wavelength array as a proxy for time steps)
        # We assume a 10 Hz sweep rate for the noise bandwidth calculation (dt = 0.1s / num_samples)
        time_array = np.linspace(0, 0.1, self.sim_cfg.num_samples)
        p_laser_up, wl_noisy_up = self.laser.generate_signal(time_array)
        p_laser_down, wl_noisy_down = self.laser.generate_signal(time_array)
        
        # --- PATH A: Conventional FBG Interrogation (Direct Reflection) ---
        # Reflected power = Laser * Loss * FBG_Reflectivity
        r_fbg_up = self.fbg.reflectivity(wl_noisy_up)
        p_ref_up = self.loss_budget.apply_loss(p_laser_up) * r_fbg_up
        v_conv_up = self.pd.process_optical_power(p_ref_up)
        
        est_lambda_conv = ConventionalInterrogator.centroid(wl_noisy_up, v_conv_up)
        
        # --- PATH B: Bistable FBG Interrogation (FBG + Kerr Cavity) ---
        v_bistable_up = np.zeros(self.sim_cfg.num_samples)
        current_state = 0.0
        for i in range(self.sim_cfg.num_samples):
            # Input to cavity is the reflected FBG power
            p_cav_in = p_ref_up[i]
            current_state = self.cavity.solve_steady_state(p_cav_in, wl_noisy_up[i], current_state)
            p_cav_out = self.cavity.get_output_power(current_state)
            # Detector only sees the cavity output minus detector coupling loss
            v_bistable_up[i] = self.pd.process_optical_power(np.array([p_cav_out]))[0]
            
        est_switch_up = BistableInterrogator.detect_switch_wavelength(wl_noisy_up, v_bistable_up, 'up')
        
        return {
            'true_lambda_b': true_lambda_b,
            'wl_up': wl_noisy_up,
            'v_conv_up': v_conv_up,
            'v_bistable_up': v_bistable_up,
            'est_conv': est_lambda_conv,
            'est_switch': est_switch_up
        }