# src/data_gen.py

import pandas as pd
import numpy as np
from datetime import timedelta

class PortfolioGenerator:
    """
    Generates dummy portfolio data for demonstration purposes.
    Simulates a Trading Book with Long and Short positions.
    """
    
    @staticmethod
    def generate_energy_balance(start_date, months=24):
        """Generates a dummy energy balance (Trading Book)."""
        dates = pd.date_range(start=start_date, periods=months, freq='MS')
        
        data = []
        # Scenario: Long in NE (Northeast), Short in SE (Southeast)
        for d in dates:
            # Long Position (Solar Generation) in NE
            data.append({
                'Date': d,
                'Submarket': 'NE',
                'Source': 'Solar',
                'Portfolio': 'Trading',
                'MW_Avg': np.random.uniform(50, 60) # Long Position
            })
            # Short Position (Sales Contract) in SE
            data.append({
                'Date': d,
                'Submarket': 'SE',
                'Source': 'Contract',
                'Portfolio': 'Trading',
                'MW_Avg': np.random.uniform(-30, -40) # Short Position
            })
            
        return pd.DataFrame(data)

class MarketDataGenerator:
    """
    Generates dummy market data (prices, risk matrices, curves).
    """
    
    @staticmethod
    def generate_risk_matrix(vertices):
        """
        Generates a positive-definite covariance matrix for the given vertices.
        Args:
            vertices (list): List of vertex names ['M1', 'M2', 'Y1'...]
        """
        n = len(vertices)
        # Create a random matrix
        A = np.random.rand(n, n)
        # Make A symmetric and positive-definite (A * A.T)
        cov_matrix = np.dot(A, A.transpose())
        
        # Scale to resemble energy price volatility (approx. 20-50 BRL variance)
        cov_matrix = cov_matrix * 10 
        
        df = pd.DataFrame(cov_matrix, index=vertices, columns=vertices)
        return df

    @staticmethod
    def generate_forward_curves(start_date, months=24):
        """Generates forward price curves for NE and SE submarkets."""
        dates = pd.date_range(start=start_date, periods=months, freq='MS')
        
        # Prices with seasonality and trend
        base_price = 100
        trend = np.linspace(0, 20, months)
        seasonality = np.sin(np.linspace(0, 3.14*4, months)) * 30
        
        price_ne = base_price + trend + seasonality + np.random.normal(0, 5, months)
        price_se = price_ne * 1.1 + np.random.normal(0, 2, months) # South slightly more expensive
        
        df = pd.DataFrame({
            'NE': price_ne,
            'SE': price_se
        }, index=dates).T # Transpose so Submarket is the Index
        
        return df

    @staticmethod
    def generate_discount_curve(start_date, months=24):
        """Generates discount factors based on a fixed interest rate."""
        dates = pd.date_range(start=start_date, periods=months, freq='MS')
        rate_aa = 0.10 # 10% p.a.
        rate_am = (1 + rate_aa)**(1/12) - 1
        
        factors = [1 / ((1 + rate_am)**i) for i in range(months)]
        
        return pd.Series(factors, index=dates)