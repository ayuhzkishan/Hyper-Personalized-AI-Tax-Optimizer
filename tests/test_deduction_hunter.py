import pytest
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from src.deduction_hunter import DeductionHunter
from src.tax_engine import TaxEngine

def test_deduction_hunter_headroom():
    hunter = DeductionHunter()
    hunter.add_existing_deduction("80C", 50000, "EPF from Form 16")
    
    # Check 80C headroom should be 1,50,000 - 50,000 = 1,00,000
    headroom = hunter.get_headroom("80C")
    assert headroom == 100000.0

    # Ensure over-utilization sets headroom to 0
    hunter.add_existing_deduction("80C", 110000, "LIC Premium")
    assert hunter.get_headroom("80C") == 0.0

def test_audit_trail_generation():
    hunter = DeductionHunter()
    hunter.add_existing_deduction("80C", 30000, "EPF")
    hunter.add_existing_deduction("80C", 20000, "PPF")
    
    audit = hunter.generate_audit_trail("80C")
    assert audit.total_capacity == 150000
    assert audit.utilized_amount == 50000
    assert audit.remaining_capacity == 100000
    assert len(audit.entries) == 2
    assert audit.entries[0].source == "EPF"
    assert "ELSS Mutual Funds" in audit.eligible_instruments

def test_tax_impact_evaluation():
    hunter = DeductionHunter()
    engine = TaxEngine(fy="2025-26", regime="old") # Deductions valid in old regime
    
    # Base income 12,00,000. Tax under old regime:
    # 2.5L to 5L = 12.5k
    # 5L to 10L = 1L
    # 10L to 11.5L = 30k
    # Total tax = 1.425L
    # (Without deduction, taxable income is 11.5L due to 50k standard deduction)
    
    proposed = {"80C": 100000}
    
    # Compute what happens saving 1,00,000 under 80C
    # Taxable income goes from 11.5L to 10.5L
    # Tax saved = 30% of 1L = 30,000 (roughly, plus cess)
    
    impact = hunter.evaluate_tax_impact(engine, 1200000.0, proposed_investments=proposed)
    assert impact > 0
    # Difference should be precisely 30,000 + 4% cess = 31,200
    assert abs(impact - 31200.0) < 1.0

