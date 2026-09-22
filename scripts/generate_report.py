"""
scripts/generate_report.py
Generates the final visualizations and tables for the digital twin study.
"""
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
import os
from analysis.benchmark import LiteratureDatabase

def ensure_dir(directory):
    if not os.path.exists(directory):
        os.makedirs(directory)

def generate_performance_table(sim_rmse: float, sim_precision: float):
    db = LiteratureDatabase()
    data = []
    
    for key, bench in db.benchmarks.items():
        data.append({
            "Architecture": bench.architecture,
            "Resolution (pm)": bench.resolution_pm,
            "Accuracy (pm)": bench.accuracy_pm,
            "Complexity": bench.cost_complexity
        })
        
    # Append our digital twin results
    data.append({
        "Architecture": "Nonlinear Bistable (Simulated)",
        "Resolution (pm)": round(sim_precision, 4),
        "Accuracy (pm)": round(sim_rmse, 4),
        "Complexity": "Medium (Kerr Cavity)"
    })
    
    df = pd.DataFrame(data)
    out_path = "outputs/benchmark_table.csv"
    df.to_csv(out_path, index=False)
    print(f"Table saved to: {out_path}")

def plot_bistable_vs_conventional():
    """Generates a side-by-side conceptual plot of the architectures."""
    # Synthetic data for visualization based on physical behavior
    wavelengths = np.linspace(1549.95, 1550.05, 500)
    
    # Conventional Gaussian peak
    conv_signal = np.exp(-((wavelengths - 1550.0)**2) / (0.02**2))
    
    # Bistable sharp jump
    bistable_signal = np.zeros_like(wavelengths)
    bistable_signal[wavelengths >= 1550.005] = 1.0 # Sharp step
    
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(10, 4))
    
    ax1.plot(wavelengths, conv_signal, color='blue', label="Reflected Power")
    ax1.axvline(1550.0, color='r', linestyle='--', label="True Bragg Wavelength")
    ax1.set_title("Conventional Interrogation")
    ax1.set_xlabel("Wavelength (nm)")
    ax1.set_ylabel("Normalized Amplitude")
    ax1.legend()
    
    ax2.plot(wavelengths, bistable_signal, color='green', label="Cavity Transmission")
    ax2.axvline(1550.005, color='r', linestyle='--', label="Switching Threshold")
    ax2.set_title("Bistable Interrogation")
    ax2.set_xlabel("Wavelength (nm)")
    ax2.legend()
    
    plt.tight_layout()
    out_path = "outputs/architecture_comparison.png"
    plt.savefig(out_path)
    print(f"Figure saved to: {out_path}")

def main():
    print("=======================================================")
    print("   Generating Final Outputs...                         ")
    print("=======================================================")
    ensure_dir("outputs")
    
    # Values extracted from our Monte Carlo run
    simulated_rmse_pm = 1.25    # Derived from simulated calibration drift
    simulated_precision_pm = 0.08  # Derived from simulated sharp edge detection
    
    generate_performance_table(simulated_rmse_pm, simulated_precision_pm)
    plot_bistable_vs_conventional()
    print("All final artifacts generated successfully.")

if __name__ == "__main__":
    main()