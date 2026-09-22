"""
models/losses.py
Optical loss budget calculations for the optical link.
"""
from dataclasses import dataclass
from typing import Dict
from core.utils import db_to_linear

@dataclass
class LossBudgetConfig:
    isolator_loss_db: float = 0.5
    circulator_pass_loss_db: float = 0.7
    connector_loss_db: float = 0.2
    num_connectors: int = 4
    coupler_insertion_loss_db: float = 0.3
    fiber_length_m: float = 100.0
    fiber_attenuation_db_per_km: float = 0.2
    detector_coupling_loss_db: float = 0.5

class OpticalLossBudget:
    def __init__(self, config: LossBudgetConfig):
        self.config = config

    def calculate_total_loss_db(self) -> float:
        """Calculates total optical loss along the signal path in dB."""
        fiber_loss = (self.config.fiber_length_m / 1000.0) * self.config.fiber_attenuation_db_per_km
        connector_total = self.config.num_connectors * self.config.connector_loss_db
        total_db = (
            self.config.isolator_loss_db
            + 2 * self.config.circulator_pass_loss_db  # Pass-through twice (FBG reflection)
            + connector_total
            + self.config.coupler_insertion_loss_db
            + fiber_loss
            + self.config.detector_coupling_loss_db
        )
        return total_db

    def apply_loss(self, input_power_watts: float) -> float:
        """Applies loss budget to an input optical power [W]."""
        total_loss_db = self.calculate_total_loss_db()
        linear_trans = db_to_linear(-total_loss_db)
        return input_power_watts * linear_trans

    def get_breakdown(self) -> Dict[str, float]:
        """Returns itemized optical power loss in dB."""
        return {
            "Isolator": self.config.isolator_loss_db,
            "Circulator (2-pass)": 2 * self.config.circulator_pass_loss_db,
            "Connectors": self.config.num_connectors * self.config.connector_loss_db,
            "Couplers": self.config.coupler_insertion_loss_db,
            "Fiber Propagation": (self.config.fiber_length_m / 1000.0) * self.config.fiber_attenuation_db_per_km,
            "Detector Coupling": self.config.detector_coupling_loss_db,
            "Total (dB)": self.calculate_total_loss_db()
        }