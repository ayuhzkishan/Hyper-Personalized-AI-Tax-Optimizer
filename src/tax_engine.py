"""
Provides deterministic Indian Income Tax rules and calculations.
Designed to be maintained locally rather than depending on slow-to-update PyPI packages.
"""

from dataclasses import dataclass
from typing import Dict, List, Tuple

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

    def _calculate_surcharge(self, taxable_income: float, base_tax: float) -> float:
        """Calculates surcharge on base tax."""
        if taxable_income > 50000000:  # > 5 Cr
            rate = 0.25 if self.regime == "new" else 0.37
            surcharge = base_tax * rate
            # Add marginal relief logic if needed, simplify for now
            return surcharge
        elif taxable_income > 20000000: # > 2 Cr
            return base_tax * 0.25
        elif taxable_income > 10000000: # > 1 Cr
            return base_tax * 0.15
        elif taxable_income > 5000000:  # > 50L
            return base_tax * 0.10
        return 0.0

    def calculate_tax(self, gross_income: float, deductions: float) -> Dict[str, float]:
        """Calculates exact tax breakdown for a given gross income and valid deductions."""
        
        # 1. Apply Standard Deduction & other itemized deductions
        taxable_income = max(0.0, gross_income - self.config.standard_deduction - deductions)

        # 2. Base tax per slabs
        base_tax = 0.0
        previous_limit = 0.0
        
        for limit, rate in self.config.slabs:
            if taxable_income > previous_limit:
                taxable_amount_in_slab = min(taxable_income, limit) - previous_limit
                base_tax += taxable_amount_in_slab * rate
                previous_limit = limit
            else:
                break

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

        # 4. Surcharge
        surcharge = self._calculate_surcharge(taxable_income, base_tax_after_rebate)

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
            "cess": cess,
            "total_tax": total_tax
        }
