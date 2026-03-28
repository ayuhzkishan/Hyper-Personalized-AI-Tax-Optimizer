"""
Provides deterministic Indian Income Tax rules and calculations.
Designed to be maintained locally rather than depending on slow-to-update PyPI packages.
"""

from dataclasses import dataclass
from typing import Dict, List, Tuple, Any

@dataclass
class TaxConfig:
    slabs: List[Tuple[int, float]]  # (upper_bound, rate) e.g., (400000, 0.0)
    rebate_87a_limit: int
    standard_deduction: int
    cess_rate: float = 0.04

# Configuration mapping (FY -> Regime -> TaxConfig)
TAX_RULES: Dict[str, Dict[str, TaxConfig]] = {
    "2024-25": {
        "new": TaxConfig(
            slabs=[
                (300000, 0.0),
                (700000, 0.05),
                (1000000, 0.10),
                (1200000, 0.15),
                (1500000, 0.20),
                (float('inf'), 0.30)
            ],
            rebate_87a_limit=700000,
            standard_deduction=50000
        ),
        "old": TaxConfig(
            slabs=[
                (250000, 0.0),
                (500000, 0.05),
                (1000000, 0.20),
                (float('inf'), 0.30)
            ],
            rebate_87a_limit=500000,
            standard_deduction=50000
        )
    },
    "2025-26": {
        "new": TaxConfig(
            # Budget 2025 new slabs (assumed for FY25-26 based on the 12L nil-tax mention)
            slabs=[
                (400000, 0.0),
                (800000, 0.05),
                (1200000, 0.10),
                (1600000, 0.15),
                (2000000, 0.20),
                (2400000, 0.25),
                (float('inf'), 0.30)
            ],
            rebate_87a_limit=1200000,
            standard_deduction=75000
        ),
        "old": TaxConfig(
            slabs=[
                (250000, 0.0),
                (500000, 0.05),
                (1000000, 0.20),
                (float('inf'), 0.30)
            ],
            rebate_87a_limit=500000,
            standard_deduction=50000
        )
    }
}

class TaxEngine:
    def __init__(self, fy: str = "2025-26", regime: str = "new"):
        if fy not in TAX_RULES or regime not in TAX_RULES[fy]:
            raise ValueError(f"Invalid FY ({fy}) or regime ({regime}) specified.")
        self.fy = fy
        self.regime = regime
        self.config = TAX_RULES[self.fy][self.regime]

    def _get_adjusted_slabs(self, age: int) -> List[Tuple[int, float]]:
        if self.regime == "new" or age < 60:
            return self.config.slabs
        
        # Modify Old Regime 1st slab for Senior/Super Senior
        slabs = list(self.config.slabs)
        if age >= 80:
            slabs[0] = (500000, 0.0)
        elif age >= 60:
            slabs[0] = (300000, 0.0)
        return slabs

    def _compute_base_tax(self, income: float, age: int) -> float:
        base_tax = 0.0
        previous_limit = 0.0
        for limit, rate in self._get_adjusted_slabs(age):
            if income > previous_limit:
                tax_amt = min(income, limit) - previous_limit
                base_tax += tax_amt * rate
                previous_limit = limit
            else:
                break
        return base_tax

    def _calculate_surcharge(self, taxable_income: float, base_tax: float, age: int) -> Tuple[float, float]:
        """Calculates surcharge on base tax and any marginal relief."""
        threshold = 0
        rate = 0.0
        surcharge_rate_at_threshold = 0.0
        
        if taxable_income > 50000000:  # > 5 Cr
            threshold, rate = 50000000, (0.25 if self.regime == "new" else 0.37)
            surcharge_rate_at_threshold = 0.25
        elif taxable_income > 20000000: # > 2 Cr
            threshold, rate = 20000000, 0.25
            surcharge_rate_at_threshold = 0.15
        elif taxable_income > 10000000: # > 1 Cr
            threshold, rate = 10000000, 0.15
            surcharge_rate_at_threshold = 0.10
        elif taxable_income > 5000000:  # > 50L
            threshold, rate = 5000000, 0.10
            surcharge_rate_at_threshold = 0.0
        else:
            return 0.0, 0.0
            
        surcharge = base_tax * rate
        marginal_relief = 0.0
        
        # Surcharge Marginal Relief Calculation
        if threshold > 0:
            tax_at_threshold = self._compute_base_tax(threshold, age)
            surcharge_at_threshold = tax_at_threshold * surcharge_rate_at_threshold
            
            tax_payable_now = base_tax + surcharge
            max_tax_payable = tax_at_threshold + surcharge_at_threshold + (taxable_income - threshold)
            
            if tax_payable_now > max_tax_payable:
                marginal_relief = tax_payable_now - max_tax_payable
                surcharge = surcharge - marginal_relief
                
        return surcharge, marginal_relief

    def calculate_tax(self, gross_income: float, deductions: float, is_salary_pension: bool = True, age: int = 30) -> Dict[str, Any]:
        """Calculates exact tax breakdown for a given gross income, valid deductions, income type, and age."""
        
        # Regime Warning flag (Nice-to-have functionality)
        invalid_deductions_warning = False
        if self.regime == "new" and deductions > 0:
            invalid_deductions_warning = True # Most Chapter VI-A are invalid, assuming caller has filtered or it's 80CCD(2).
            
        # 1. Apply Standard Deduction & other itemized deductions
        std_deduction = self.config.standard_deduction if is_salary_pension else 0
        taxable_income = max(0.0, gross_income - std_deduction - deductions)

        # 2. Base tax per slabs
        base_tax = self._compute_base_tax(taxable_income, age)

        # 3. 87A Rebate & Marginal Relief
        rebate_87a = 0.0
        marginal_relief = 0.0
        
        if taxable_income <= self.config.rebate_87a_limit:
            rebate_87a = base_tax
            base_tax_after_rebate = 0.0
        else:
            # Marginal relief for 87A exactly at the edge
            # If tax jump is greater than income jump
            income_excess = taxable_income - self.config.rebate_87a_limit
            if base_tax > income_excess and self.regime == "new":
                marginal_relief = base_tax - income_excess
                base_tax_after_rebate = income_excess
            else:
                base_tax_after_rebate = base_tax

        # 4. Surcharge & Surcharge Marginal Relief
        surcharge, surcharge_margin_relief = self._calculate_surcharge(taxable_income, base_tax_after_rebate, age)

        # 5. Cess
        cess = (base_tax_after_rebate + surcharge) * self.config.cess_rate

        # 6. Total
        total_tax = base_tax_after_rebate + surcharge + cess

        return {
            "gross_income": gross_income,
            "deductions_applied": deductions,
            "taxable_income": taxable_income,
            "base_tax": base_tax,
            "rebate_87a": rebate_87a,
            "marginal_relief_87a": marginal_relief,
            "surcharge": surcharge,
            "surcharge_marginal_relief": surcharge_margin_relief,
            "cess": cess,
            "total_tax": total_tax,
            "regime_warning": invalid_deductions_warning
        }
