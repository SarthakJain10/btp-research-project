"""
scripts/run_monte_carlo.py
Executes the statistical Monte Carlo comparison between conventional 
and bistable FBG interrogation architectures.
"""
from simulation.monte_carlo import MonteCarloStudy

def main():
    print("=======================================================")
    print("   FBG Interrogation Digital Twin: Monte Carlo Study   ")
    print("=======================================================\n")
    
    study = MonteCarloStudy(trials=50)
    print("Running 50 noise trials with 10 uE applied strain target...")
    results = study.run_noise_study(strain_target=10.0)
    
    print("\n--- Monte Carlo Statistical Summary ---")
    print(f"Total Trials              : {results['trials']}")
    print(f"Missed Bistable Switches : {results['missed_bistable_switches']}")
    print(f"Conventional RMSE        : {results['conv_rmse_pm']:.4f} pm")
    print(f"Bistable Precision (Std) : {results['bistable_precision_pm']:.4f} pm")
    print("=======================================================")

if __name__ == "__main__":
    main()