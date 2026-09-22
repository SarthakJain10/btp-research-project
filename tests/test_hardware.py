"""
tests/test_hardware.py
Unit tests verifying hardware losses, laser output, and detector noise scaling.
"""
import numpy as np
from core.config import LaserConfig
from models.losses import LossBudgetConfig, OpticalLossBudget
from models.laser import LaserSource
from models.photodetector import PhotodetectorConfig, PhotodetectorSystem

def test_loss_budget_attenuation():
    loss_cfg = LossBudgetConfig(isolator_loss_db=1.0, num_connectors=2, connector_loss_db=0.5)
    budget = OpticalLossBudget(loss_cfg)
    p_in = 1.0  # 1 Watt
    p_out = budget.apply_loss(p_in)
    
    assert p_out < p_in, "Output power must be attenuated."
    assert budget.calculate_total_loss_db() > 0.0

def test_laser_noise_generation():
    laser_cfg = LaserConfig(power_w=0.01, linewidth_hz=100e3, rin_db_hz=-130.0)
    laser = LaserSource(laser_cfg)
    t = np.linspace(0, 1e-4, 1000)
    p_t, wl_t = laser.generate_signal(t)
    
    assert len(p_t) == 1000
    assert np.all(p_t >= 0.0), "Optical power cannot be negative."
    assert np.std(wl_t) > 0.0, "Frequency/phase noise must produce non-zero wavelength variance."

def test_photodetector_shot_noise_scaling():
    pd_cfg = PhotodetectorConfig(adc_bits=16)
    pd = PhotodetectorSystem(pd_cfg)
    
    p_low = np.ones(10000) * 1e-6   # 1 uW (V_out ~ 0.0085 V)
    # FIX: Lower p_high to 100 uW to prevent the 2.5V ADC from hard-clipping
    p_high = np.ones(10000) * 1e-4  # 100 uW (V_out ~ 0.85 V, safely under 2.5V)
    
    v_low = pd.process_optical_power(p_low)
    v_high = pd.process_optical_power(p_high)
    
    assert np.std(v_high) > np.std(v_low), "Shot noise variance must scale with optical power."