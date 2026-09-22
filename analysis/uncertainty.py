"""
analysis/uncertainty.py
Measurement uncertainty budget calculator adhering to GUM (ISO/IEC Guide 98-3).
"""
from dataclasses import dataclass, field
from typing import List
import numpy as np

@dataclass
class UncertaintyComponent:
    name: str
    standard_uncertainty: float  # u(x_i) in physical units
    sensitivity_coeff: float     # c_i = df/dx_i
    unit: str
    category: str = "Type B"      # "Type A" (statistical) or "Type B" (systematic/eval)

@dataclass
class UncertaintyBudget:
    target_name: str
    target_unit: str
    components: List[UncertaintyComponent] = field(default_factory=list)
    
    def add_component(self, name: str, u_x: float, c_i: float, unit: str, category: str = "Type B"):
        self.components.append(UncertaintyComponent(name, u_x, c_i, unit, category))
        
    def calculate_budget(self, coverage_factor: float = 2.0) -> dict:
        """Calculates combined standard uncertainty and expanded uncertainty."""
        comp_contributions = []
        total_var = 0.0
        
        for comp in self.components:
            contrib_var = (comp.sensitivity_coeff * comp.standard_uncertainty)**2
            total_var += contrib_var
            comp_contributions.append({
                'name': comp.name,
                'u_x': comp.standard_uncertainty,
                'c_i': comp.sensitivity_coeff,
                'variance_contrib': contrib_var,
                'percent_contribution': 0.0  # Filled below
            })
            
        u_combined = np.sqrt(total_var)
        u_expanded = coverage_factor * u_combined
        
        # Calculate percentage contributions
        for item in comp_contributions:
            item['percent_contribution'] = (item['variance_contrib'] / total_var * 100.0) if total_var > 0 else 0.0
            
        return {
            'target': self.target_name,
            'combined_standard_uncertainty': u_combined,
            'coverage_factor_k': coverage_factor,
            'expanded_uncertainty': u_expanded,
            'components': comp_contributions
        }