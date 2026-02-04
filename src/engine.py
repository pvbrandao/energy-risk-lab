# src/engine.py

import pandas as pd
import numpy as np
from scipy.stats import norm
import logging

# Basic logging configuration to demonstrate best practices
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class RiskEngine:
    """
    Calculation engine for Energy Portfolio Risk and Valuation.
    Performs Mark-to-Market (MtM) and Parametric Value at Risk (VaR) calculations.
    """

    def __init__(self, confidence_interval: float = 0.95):
        self.confidence_interval = confidence_interval
        self.z_score = norm.ppf(confidence_interval)

    def _map_date_to_vertex(self, date: pd.Timestamp, base_date: pd.Timestamp) -> str:
        """
        Helper method to map dates to market vertices (M1..M12, Y1..).
        Used to align portfolio exposure with the risk matrix.
        """
        diff = (date.year - base_date.year) * 12 + (date.month - base_date.month)
        
        if diff < 0: 
            return 'Past'
        if diff < 12:
            return f'M{diff + 1}'
        else:
            year_idx = (diff // 12)
            return f'Y{year_idx}'

    def calculate_mtm(self, energy_balance: pd.DataFrame, forward_curves: pd.DataFrame, discount_curve: pd.Series):
        """
        Calculates the Mark-to-Market (MtM) of the portfolio.
        
        Args:
            energy_balance (pd.DataFrame): Energy balance (Long/Short positions). 
                                         Expected cols: ['Date', 'Submarket', 'MW_Avg']
            forward_curves (pd.DataFrame): Forward prices per submarket.
            discount_curve (pd.Series): Discount factors indexed by Date.
            
        Returns:
            tuple: (mtm_matrix, total_mtm_value)
        """
        logger.info("Starting MtM calculation...")
        
        # 1. Pivot balance to align with price curves
        # Assumes input curves are indexed by Date
        balance_grouped = energy_balance.groupby(['Date', 'Submarket'])['MW_Avg'].sum().unstack(level=0)
        
        # 2. Align Indices (Submarkets) and Columns (Dates)
        common_dates = balance_grouped.columns.intersection(forward_curves.columns)
        common_subs = balance_grouped.index.intersection(forward_curves.index)
        
        balance_aligned = balance_grouped.loc[common_subs, common_dates]
        prices_aligned = forward_curves.loc[common_subs, common_dates]
        discounts_aligned = discount_curve.reindex(common_dates).fillna(1.0)
        
        # 3. Financial Calculation: Volume * (Forward Price) * Discount Factor
        # Note: 720 hours assumed as a flat average for demonstration purposes
        hours_in_month = 720 
        
        notional = balance_aligned * prices_aligned * hours_in_month
        mtm = notional * discounts_aligned
        
        total_mtm = mtm.sum().sum()
        logger.info(f"MtM calculation finished. Total Value: BRL {total_mtm:,.2f}")
        
        return mtm, total_mtm

    def calculate_parametric_var(self, energy_balance: pd.DataFrame, risk_matrix: pd.DataFrame, base_date: pd.Timestamp):
        """
        Calculates Parametric Value at Risk (VaR) using the Delta-Normal approach.
        Formula: sqrt(s.T @ Sigma @ s) * Z
        
        Args:
            energy_balance (pd.DataFrame): Net exposure in MW avg.
            risk_matrix (pd.DataFrame): Price covariance matrix (BRL/MWh).
            base_date (pd.Timestamp): Reference date for vertex mapping.
            
        Returns:
            tuple: (var_value, exposure_financial_vector)
        """
        logger.info("Starting Parametric VaR calculation...")
        
        # 1. Map exposure dates to Risk Vertices (M1, M2, Y1...)
        df = energy_balance.copy()
        df['Vertex'] = df['Date'].apply(lambda x: self._map_date_to_vertex(x, base_date))
        
        # 2. Aggregate net exposure by Vertex
        # Filter only vertices that exist in the risk matrix
        valid_vertices = risk_matrix.index.tolist()
        exposure_vector = df[df['Vertex'].isin(valid_vertices)].groupby('Vertex')['MW_Avg'].sum()
        
        # Reindex to ensure vector matches matrix order (fill missing vertices with 0)
        s = exposure_vector.reindex(risk_matrix.index).fillna(0)
        
        # 3. Matrix Calculation
        # Portfolio Variance = s.T * CovarianceMatrix * s
        # Converting MW avg to Financial Exposure (BRL) before applying the Price Covariance Matrix
        
        hours_factor = 720 
        s_financial = s * hours_factor 
        
        portfolio_variance = s_financial.T @ risk_matrix @ s_financial
        portfolio_std = np.sqrt(portfolio_variance)
        
        var_value = portfolio_std * self.z_score
        
        logger.info(f"VaR calculated: BRL {var_value:,.2f} (Confidence: {self.confidence_interval*100}%)")
        
        return var_value, s_financial