# Risk-Stratified Screening (RSS) Simulation Study

This repository contains the source code and simulation framework for the study:

**"Risk-Stratified Screening: A Simulation Study of Scheduling Templates on Daily Mammography Recalls"** *Published in the Journal of the American College of Radiology (JACR). https://doi.org/10.1016/j.jacr.2024.12.010*

## Overview

We developed a **Discrete Event Simulation (DES)** of a high-volume breast imaging center to evaluate how risk-stratified screening (RSS) impacts clinic workflow. The simulation explores the integration of AI-triaged same-day diagnostic workups and compares traditional scheduling to RSS templates informed by patient cancer risk scores (Tyrer-Cuzick and deep learning models).

### Key Findings

* **Variance Reduction:** RSS scheduling significantly reduces the daily variability of diagnostic recalls.
* **Throughput:** RSS can modestly improve patient capacity within normal clinic hours.
* **Wait Times:** Improvements in workflow were achieved with minimal changes to patient wait times.

### Workflows
![1-s2 0-S1546144024010068-gr3_lrg](https://github.com/user-attachments/assets/746b7f1b-f6d6-4034-9957-a4e93be1163e)

---

## Citation

If you use this code or our findings in your research, please cite:

> Lin Y, Hoyt AC, Manuel VG, et al. Risk-Stratified Screening: A Simulation Study of Scheduling Templates on Daily Mammography Recalls. **J Am Coll Radiol.** 2025;22(3):297-306. doi:10.1016/j.jacr.2024.12.010

---

## Repository Contents

* **Simulation Core:** DES logic modeling breast imaging center operations.
* **Scheduling Templates:** Definitions for risk categories (RSS 1-3) and template structures.
* **Analysis Scripts:** Tools to reproduce figures, throughput metrics, and variance testing.
* **Data Tools:** Scripts to generate screener pools based on risk distributions.

---

## Getting Started

### 1. Installation

Clone the repository and install the required dependencies:

```bash
pip install -r requirements.txt

```

### 2. Phase 1: Run Baseline Simulations (Non-RSS)

First, generate the control data by running the simulation without smart scheduling logic.

* **Baseline Workflow (Traditional):**
```bash
python run_simulation.py --is_1ss no

```


* **Same-Day Workflow (One-Stop Shop):**
```bash
python run_simulation.py --is_1ss yes

```



### 3. Phase 2: Create Screener Pools

The "Smart" scheduling logic requires a pre-generated pool of screeners to draw from for risk-stratification.

* **For Baseline Workflow:**
```bash
python create_screener_pool.py --workflow no_1ss

```


* **For Same-Day (1SS) Workflow:**
```bash
python create_screener_pool.py --workflow 1ss

```



### 4. Phase 3: Run RSS Simulations (Smart Scheduling)

Run the simulations again using the `--smart` flag to apply the Risk-Stratified templates.

* **Baseline + RSS:**
```bash
python run_simulation.py --is_1ss no --smart

```


* **Same-Day (1SS) + RSS:**
```bash
python run_simulation.py --is_1ss yes --smart

```


### 5. Examplme Output

<img width="728" height="220" alt="Capture" src="https://github.com/user-attachments/assets/66078a9b-9dd0-4661-96b8-a702beb803a1" />


---

## Contact

For questions regarding the simulation logic or data structures, please open an issue in this repository or contact the lead author.



