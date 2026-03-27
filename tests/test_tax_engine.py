import pytest
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from src.tax_engine import TaxEngine

def test_fy25_new_regime_below_12L():
    engine = TaxEngine(fy="2025-26", regime="new")
    # Gross 12L, no other deductions, standard deduction is 75k
    # taxable: 11,25,000. Tax is 0 due to 87A
    res = engine.calculate_tax(1200000, 0)
    assert res["taxable_income"] == 1125000
    assert res["total_tax"] == 0
    assert res["rebate_87a"] > 0

def test_fy25_new_regime_marginal_relief():
    engine = TaxEngine(fy="2025-26", regime="new")
    # Exact scenario: taxable income = 12,10,000
    # Gross income = 12,10,000 + 75000 = 12,85,000
    res = engine.calculate_tax(1285000, 0)
    assert res["taxable_income"] == 1210000
    # Base tax on 12,10,000 = 61,500
    # Income excess = 10,000
    # Marginal relief = 51,500
    # base tax after rebate = 10,000
    # Cess = 400
    # Total tax = 10,400
    assert res["base_tax"] == 61500
    assert res["marginal_relief_87a"] == 51500
    assert res["cess"] == 400
    assert res["total_tax"] == 10400

def test_fy25_new_regime_above_marginal():
    engine = TaxEngine(fy="2025-26", regime="new")
    # Taxable 13,00,000
    # Base tax = (4L*0) + (4L*5%) + (4L*10%) + (1L*15%) = 0 + 20k + 40k + 15k = 75,000
    res = engine.calculate_tax(1375000, 0)
    assert res["taxable_income"] == 1300000
    assert res["base_tax"] == 75000
    assert res["marginal_relief_87a"] == 0
    assert res["total_tax"] == 78000 # +4% cess
