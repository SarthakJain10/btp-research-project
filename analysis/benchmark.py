"""
analysis/benchmark.py
Comparative baseline metrics from published literature on FBG interrogation.
"""
from dataclasses import dataclass
from typing import Dict

@dataclass
class InterrogatorBenchmark:
    architecture: str
    resolution_pm: float
    accuracy_pm: float
    bandwidth_hz: float
    cost_complexity: str
    reference: str

class LiteratureDatabase:
    def __init__(self):
        self.benchmarks: Dict[str, InterrogatorBenchmark] = {
            "conventional_osa": InterrogatorBenchmark(
                architecture="Optical Spectrum Analyzer (OSA)",
                resolution_pm=10.0,
                accuracy_pm=5.0,
                bandwidth_hz=1.0,
                cost_complexity="High",
                reference="Typical commercial benchtop limits"
            ),
            "edge_filter": InterrogatorBenchmark(
                architecture="Matched Edge Filter",
                resolution_pm=0.5,
                accuracy_pm=2.0,
                bandwidth_hz=10000.0,
                cost_complexity="Low",
                reference="Rao, 1997, Meas. Sci. Technol."
            ),
            "swept_laser": InterrogatorBenchmark(
                architecture="Swept Tunable Laser (Centroid)",
                resolution_pm=1.0,
                accuracy_pm=1.0,
                bandwidth_hz=1000.0,
                cost_complexity="Medium",
                reference="Kersey et al., 1997, JLT"
            )
        }

    def compare(self, custom_name: str, custom_res: float, custom_acc: float) -> dict:
        """Compares custom simulated metrics against literature standard."""
        comparisons = {}
        for key, bench in self.benchmarks.items():
            res_improvement = bench.resolution_pm / custom_res
            comparisons[key] = {
                'architecture': bench.architecture,
                'resolution_improvement_factor': res_improvement,
                'beats_accuracy': custom_acc < bench.accuracy_pm
            }
        return comparisons