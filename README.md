# Sub-Picometer Fiber Bragg Grating Interrogation via Kerr-Effect Optical Bistability: A Digital Twin Architecture

## Overview

This repository contains a physics-driven **digital twin** and numerical simulation framework designed to evaluate a novel nonlinear Fiber Bragg Grating (FBG) interrogation architecture.

Traditional FBG interrogators rely on linear spectrum centroid tracking or edge filtering to measure Bragg wavelength shifts ($\Delta \lambda_B$). These methods are fundamentally bounded by photodetector noise, laser Relative Intensity Noise (RIN), and spectral sampling step sizes, typically limiting operational resolution to $\approx 1.0\text{ pm}$.

This project models an alternative approach: routing the reflected FBG spectrum into a high-finesse ring cavity exhibiting **Kerr dispersive optical bistability**. Minute changes in the reflected Bragg wavelength adjust the laser-cavity detuning, triggering sharp transmission jumps between bistable states. This sharp transition suppresses amplitude noise and enables sub-picometer measurement precision (**$0.08\text{ pm}$** in 500-trial Monte Carlo simulations).

---

## Technical & Mathematical Foundations

### 1. Physical FBG Reflection Model (Coupled-Mode Theory)

The spectral profile of a uniform FBG with length $L_f$, core effective index $n_{\text{eff}}$, and index modulation $\Delta n$ is calculated using two-mode Coupled-Mode Theory (CMT):

$$r(\lambda) = \frac{-i \kappa \sinh(\gamma L_f)}{\gamma \cosh(\gamma L_f) + i \delta \sinh(\gamma L_f)}$$

Where:

* **AC Coupling Coefficient:** $\kappa = \frac{\pi \Delta n}{\lambda_B}$
* **Detuning Parameter:** $\delta = 2\pi n_{\text{eff}} \left( \frac{1}{\lambda} - \frac{1}{\lambda_B} \right)$
* **Dispersion Parameter:** $\gamma = \sqrt{\kappa^2 - \delta^2}$
* **Power Reflectivity:** $R(\lambda) = \vert{}r(\lambda)\vert{}^2$

The resonance shift due to strain $\varepsilon$ and temperature variation $\Delta T$ follows:

$$\Delta \lambda_B = \lambda_B \left[ (1 - p_e)\varepsilon + (\alpha_T + \xi)\Delta T \right]$$

Where $p_e \approx 0.22$ is the photoelastic coefficient, $\alpha_T \approx 0.55 \times 10^{-6}\text{ K}^{-1}$ is thermal expansion, and $\xi \approx 8.6 \times 10^{-6}\text{ K}^{-1}$ is the thermo-optic coefficient.

---

### 2. Nonlinear Kerr Cavity (Lugiato-Lefever Bistability)

The cavity consists of a high-finesse ring resonator with Kerr nonlinear coefficient $\gamma_k$. Under continuous-wave (CW) excitation, the dimensionless steady-state relation between normalized input power $y$ and internal circulating power $x$ is given by:

$$y = x \left[ 1 + (\delta_n + x)^2 \right]$$

Where:

* **Normalized Circulating Power:** $x = \frac{\gamma_k L_{\text{cav}}}{\alpha_{\text{rt}}} P_c$
* **Normalized Linear Detuning:** $\delta_n = \frac{\phi_0}{\alpha_{\text{rt}}}$
* **Normalized Input Power:** $y = \frac{\kappa_c \gamma_k L_{\text{cav}}}{\alpha_{\text{rt}}^3} P_{\text{in}}$
* $\alpha_{\text{rt}}$ is the round-trip loss factor, $\kappa_c$ is coupler power transmittance, and $\phi_0$ is linear detuning.

#### Stability Criteria

Bistability (an S-shaped curve with three real roots) requires:

$$\delta_n < -\sqrt{3} \approx -1.732$$

The turning points (fold bifurcations) occur where $\frac{dy}{dx} = 0$:

$$3x^2 + 4\delta_n x + (1 + \delta_n^2) = 0 \implies x_{\pm} = \frac{-2\delta_n \pm \sqrt{\delta_n^2 - 3}}{3}$$

The branch between $x_-$ and $x_+$ is physically unstable ($\frac{dy}{dx} < 0$).

```
Normalized Circulating Power (x)
      |         Stable Upper Branch
      |         /------------------
      |        / 
      |       / <--- Switch-Up Point (x_)
      |      / :
      |     /  : Unstable Branch (dy/dx < 0)
      |    /   :
      |   /--->+ <--- Switch-Down Point (x+)
      |  /
      | / Stable Lower Branch
      +---------------------------------- Normalized Input Power (y)

```

---

### 3. Noise Models & Hardware Degradation

* **Laser Source:**
* Relative Intensity Noise (RIN): $\sigma_{\text{RIN}}^2 = 10^{\text{RIN}/10} \cdot P_0^2 \cdot \Delta f$
* Linewidth Frequency Jitter: Gaussian phase noise scaled by laser linewidth $\Delta \nu$.


* **Photodetector System:**
* Photocurrent: $I_{\text{ph}} = R \cdot P_{\text{opt}}$ ($R \approx 0.85\text{ A/W}$)
* Shot Noise: $\sigma_{\text{shot}}^2 = 2 q I_{\text{ph}} B$
* Transimpedance Thermal Noise: $\sigma_{\text{thermal}}^2 = \frac{4 k_B T}{R_f} B$
* Digitization: $N$-bit ADC with quantization step $\text{LSB} = \frac{V_{\text{max}}}{2^N - 1}$ and hard clipping at $V_{\text{max}}$.



---

### 4. ISO-GUM Uncertainty Model

Combined standard uncertainty $u_c(\lambda)$ follows the ISO/IEC Guide 98-3 (GUM) law of propagation:

$$u_c^2(\lambda) = \sum_{i=1}^{N} c_i^2 u^2(x_i)$$

Where $c_i = \frac{\partial f}{\partial x_i}$ is the sensitivity coefficient of parameter $x_i$. Expanded uncertainty $U$ at $95\%$ confidence level corresponds to coverage factor $k = 2$: $U = 2 \cdot u_c(\lambda)$.

---

## Directory Layout

```text
fbg_bistable_interrogator/
├── core/                   # Physical constants, dataclasses, and shared utilities
│   ├── __init__.py
│   ├── constants.py        # Fundamental physical constants (c, h, e, k_B)
│   ├── config.py           # Dataclasses for FBG, Laser, Cavity, PD, Sim configs
│   └── utils.py            # Mathematical helper functions
├── models/                 # Physics models
│   ├── __init__.py
│   ├── fbg.py              # Coupled-Mode Theory implementation
│   ├── resonator.py        # Linear ring resonator transfer functions
│   ├── kerr_cavity.py      # Lugiato-Lefever cubic solver & hysteresis engine
│   ├── losses.py           # Optical loss budget calculations
│   ├── laser.py            # Laser signal generation with RIN and linewidth noise
│   └── photodetector.py    # Transimpedance, shot/thermal noise, and ADC quantization
├── processing/             # Signal processing algorithms
│   ├── __init__.py
│   ├── conventional.py     # Maximum peak, centroid, and Lorentzian curve fitting
│   └── bistable.py         # Discrete gradient edge detection for switching events
├── simulation/             # System orchestration & Monte Carlo execution
│   ├── __init__.py
│   ├── orchestrator.py     # Wires hardware models into a unified experimental sweep
│   └── monte_carlo.py      # Multi-trial statistical noise evaluator
├── analysis/               # Analytical & benchmarking tools
│   ├── __init__.py
│   ├── sensitivity.py      # Local parameter sensitivity engine (S_x)
│   ├── uncertainty.py      # ISO-GUM standard uncertainty budget calculator
│   └── benchmark.py        # Published literature comparison database
├── tests/                  # Pytest verification suite (15 unit tests)
│   ├── test_physics.py
│   ├── test_kerr.py
│   ├── test_hardware.py
│   ├── test_algorithms.py
│   └── test_analysis.py
├── scripts/                # Execution & visualization scripts
│   ├── run_monte_carlo.py  # Standalone CLI statistical study runner
│   └── generate_all_outputs.py # Exports Figures 1-20 and Tables 1-8
├── outputs/                # Generated PNG figures and CSV tables
├── requirements.txt        # Package dependencies
└── README.md               # System documentation

```

---

## Installation & Environment Setup

### Prerequisites

* Python 3.11 or higher
* `pip` package manager

### 1. Clone Repository & Create Virtual Environment

```bash
git clone https://github.com/SarthakJain10/btp-research-project
cd fbg-bistable-interrogator

python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

```

### 2. Install Dependencies

```bash
pip install -r requirements.txt

```

---

## Running the Verification Suite

Verify physical models, hardware constraints, and DSP logic against unit tests:

```bash
pytest tests/ -v

```

### Key Guardrails Enforced by Test Suite

* **Physical Energy Conservation:** FBG reflectivity $R(\lambda) \le 1.0$.
* **Bistability Threshold Verification:** Asserts hysteresis loop area $> 0$ only when $\delta_n < -\sqrt{3}$ and power exceeds switching threshold.
* **ADC Saturation Protection:** Guarantees photodetector transimpedance voltage remains below ADC $V_{\text{max}}$ to prevent flatlining.
* **Statistical Convergence:** Validates GUM variance propagation against analytical solutions.

---

## Executing Simulations & Output Generation

### 1. Run Monte Carlo Statistical Study

Executes repeated noise trials across conventional centroid tracking vs. bistable switching:

```bash
python scripts/run_monte_carlo.py

```

```text
=======================================================
   FBG Interrogation Digital Twin: Monte Carlo Study   
=======================================================

--- Monte Carlo Statistical Summary ---
Total Trials              : 50
Missed Bistable Switches : 0
Conventional RMSE        : 1.2514 pm
Bistable Precision (Std) : 0.0812 pm
=======================================================

```

### 2. Generate Full Artifact Suite (Figures 1–20 & Tables 1–8)

To run the automated suite that executes physical parameter sweeps, populates `outputs/` with all 20 publication figures and 8 structured CSV tables:

```bash
python scripts/generate_all_outputs.py

```

#### Generated Tables (`outputs/table*.csv`)

* `table1_physical_parameters.csv`: Full component parameters and literature citations.
* `table2_simulation_parameters.csv`: Numerical step sizes, sampling grid, and seed settings.
* `table3_loss_budget.csv`: Component optical insertion loss breakdown.
* `table4_noise_sources.csv`: Noise parameters (RIN, shot noise, thermal noise, quantization).
* `table5_uncertainty_budget.csv`: ISO-GUM uncertainty budget breakdown.
* `table6_monte_carlo_results.csv`: RMSE, precision, and min detectable shift metrics.
* `table7_literature_comparison.csv`: Architectural comparison (OSAs, Edge Filters, Swept Lasers).
* `table8_recommended_operating_region.csv`: Optimal parameters and failure boundaries.

#### Key Figures Exported (`outputs/fig*.png`)

* **Figure 1 (`fig1_architecture.png`):** System schematic block diagram.
* **Figure 2 (`fig2_fbg_spectrum.png`):** CMT reflection spectrum under $0\text{ }\mu\varepsilon$ and $+120\text{ }\mu\varepsilon$.
* **Figure 5 (`fig5_kerr_bistability_curve.png`):** Intracavity power S-curve showing switching points.
* **Figure 9 (`fig9_bistable_noisy_switching.png`):** Photodetector edge detection under noise.
* **Figure 17 (`fig17_feasible_heatmap.png`):** 2D feasible operating map ($P_{\text{in}}$ vs. $\delta_n$).
* **Figure 19 (`fig19_precision_comparison.png`):** Monte Carlo error distribution histograms.

---

## Summary Performance Comparison

| Metric | Conventional Swept Centroid | Bistable Kerr Interrogator | Improvement / Trade-off |
| --- | --- | --- | --- |
| **Precision ($\sigma$)** | $1.25\text{ pm}$ | **$0.08\text{ pm}$** | **$15.6 \times$ Precision Improvement** |
| **Minimum Detectable Shift** | $3.75\text{ pm}$ | **$0.24\text{ pm}$** | Sub-picometer sensitivity |
| **Optical Power Req.** | $< 1.0\text{ mW}$ | $\approx 3.5\text{ W}$ | High power required for fiber cavities |
| **Thermal Stability Req.** | $\pm 0.1\text{ K}$ | **$\le \pm 0.01\text{ K}$** | Strict temperature stabilization needed |
| **Primary Noise Limiter** | Photodetector Noise / RIN | Interrogator Thermal Drift | Shifted from amplitude to thermal noise |

---

## License & Attribution

Distributed under the **MIT License**. See `LICENSE` for details.

Developed as a multidisciplinary digital twin project combining **Fiber Optics**, **Nonlinear Cavity Dynamics**, and **DSP Signal Processing**.