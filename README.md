Energy Trading Risk Management (ETRM) Toolkit

> **[Clique aqui para ver o Dashboard Interativo (Live Demo)](https://pvbrandao.github.io/energy-risk-lab/Demo_Risk_Calculation.html)**

About this Project: This repository demonstrates a quantitative framework for managing energy portfolios in the Brazilian Market (Free Energy Market - ACL). It includes implementations of key risk metrics widely used in the industry, developed in Python.

Key Features:

- Mark-to-Market (MtM): Calculation of liquid portfolio value against forward curves.

- Parametric VaR (Value at Risk): Implementation of the Delta-Normal approach using covariance matrices (s.T @ Σ @ s) to estimate potential losses with a 95% confidence interval.

- Profit at Risk (PaR): customized metrics for illiquid energy assets using Monte Carlo simulation concepts.

Tech Stack:

- Python (Pandas, NumPy, SciPy)
- Financial Modeling (Quantitative Risk)

How to Run: Check the notebooks/Demo_Risk_Calculation.ipynb to see the risk engine in action with simulated data.

Author: Paula Brandão (Senior Portfolio & Risk Analyst)
