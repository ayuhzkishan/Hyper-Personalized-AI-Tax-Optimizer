from dataclasses import dataclass, field
from typing import Dict, List, Optional
from .tax_engine import TaxEngine

@dataclass
class DeductionEntry:
    amount: float
    source: str  # e.g., "Form 16 - EPF", "Manual - LIC Premium"

@dataclass
class SectionLimit:
    max_limit: float
    description: str
    allowed_in_new_regime: bool = False

@dataclass
class AuditTrailNode:
    section: str
    total_capacity: float
    utilized_amount: float
    remaining_capacity: float
    entries: List[DeductionEntry]
    exact_tax_saved: Optional[float] = None
    eligible_instruments: List[str] = field(default_factory=list)

SECTION_RULES = {
    "80C": SectionLimit(150000, "Life Insurance, PPF, ELSS, EPF, etc.", allowed_in_new_regime=False),
    "80CCD(1B)": SectionLimit(50000, "NPS Tier 1 Additional Deduction", allowed_in_new_regime=False),
    "80CCD(2)": SectionLimit(float('inf'), "Employer NPS Contribution (14% of Basic for Govt, 10% logic otherwise)", allowed_in_new_regime=True),
    "80D": SectionLimit(75000, "Health Insurance Premium", allowed_in_new_regime=False), # Simplification, max limit depends on age/parents
    "24(b)": SectionLimit(200000, "Home Loan Interest for Self-Occupied", allowed_in_new_regime=False),
}

INSTRUMENTS_MAPPING = {
    "80C": ["ELSS Mutual Funds", "PPF", "5-year FD", "Life Insurance"],
    "80CCD(1B)": ["NPS Tier 1"],
    "80D": ["Health Insurance Premium"]
}

class DeductionHunter:
    def __init__(self):
        self.current_utilization: Dict[str, List[DeductionEntry]] = {sec: [] for sec in SECTION_RULES}
        
    def add_existing_deduction(self, section: str, amount: float, source: str):
        if section not in self.current_utilization:
            self.current_utilization[section] = []
        self.current_utilization[section].append(DeductionEntry(amount=amount, source=source))

    def _get_total_utilized(self, section: str) -> float:
        if section not in self.current_utilization:
            return 0.0
        return sum(e.amount for e in self.current_utilization[section])

    def get_headroom(self, section: str) -> float:
        if section not in SECTION_RULES:
            return 0.0
        limit = SECTION_RULES[section].max_limit
        utilized = self._get_total_utilized(section)
        return max(0.0, limit - utilized)
        
    def get_total_deductions_for_regime(self, regime: str) -> float:
        total = 0.0
        for sec, rule in SECTION_RULES.items():
            if regime == "new" and not rule.allowed_in_new_regime:
                continue
            utilized = self._get_total_utilized(sec)
            total += min(utilized, rule.max_limit)
        return total

    def generate_audit_trail(self, section: str, proposed_amount: float = 0.0) -> AuditTrailNode:
        if section not in SECTION_RULES:
            raise ValueError(f"Unknown section: {section}")
            
        rule = SECTION_RULES[section]
        utilized = self._get_total_utilized(section)
        capacity = max(0.0, rule.max_limit - utilized)
        
        return AuditTrailNode(
            section=section,
            total_capacity=rule.max_limit,
            utilized_amount=utilized,
            remaining_capacity=capacity,
            entries=self.current_utilization[section],
            eligible_instruments=INSTRUMENTS_MAPPING.get(section, [])
        )

    def evaluate_tax_impact(self, engine: TaxEngine, gross_income: float, proposed_investments: Dict[str, float] = None) -> float:
        """
        Computes how much tax is saved by the proposed investments.
        Only valid if regime allows it, usually runs against old regime.
        """
        if proposed_investments is None:
            proposed_investments = {}

        # Tax without proposed
        deductions_without = self.get_total_deductions_for_regime(engine.regime)
        tax_without = engine.calculate_tax(gross_income, deductions_without)

        # Apply proposed temporary items
        original_utilization = {sec: self._get_total_utilized(sec) for sec in proposed_investments}
        for sec, amt in proposed_investments.items():
            self.add_existing_deduction(sec, amt, source="Proposed Simulation")
            
        # Tax with proposed
        deductions_with = self.get_total_deductions_for_regime(engine.regime)
        tax_with = engine.calculate_tax(gross_income, deductions_with)
        
        # Rollback
        for sec, amt in proposed_investments.items():
            self.current_utilization[sec].pop()
            
        return tax_without["total_tax"] - tax_with["total_tax"]
