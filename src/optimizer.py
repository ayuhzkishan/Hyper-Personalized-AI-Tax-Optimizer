import pulp
from typing import Dict, List, Any
from dataclasses import dataclass

@dataclass
class Instrument:
    id: str
    section: str
    name: str
    expected_return: float # annualized percentage e.g., 0.12 (12%)
    risk_score: float      # 1.0 (Low) to 5.0 (High)
    liquidity_score: float # 1.0 (High liquidity, e.g. Savings) to 5.0 (Low liquidity, e.g. 15yr PPF)
    lock_in_years: float   # Minimum years until withdrawal

# A sample repository of standard available instruments
AVAILABLE_INSTRUMENTS = [
    Instrument("nps_tier1", "80CCD(1B)", "NPS Tier 1", 0.10, 3.5, 5.0, 60.0),
    Instrument("epf_vpf", "80C", "VPF", 0.081, 1.0, 4.0, 5.0),
    Instrument("elss_mf", "80C", "ELSS Mutual Funds", 0.12, 4.0, 3.0, 3.0),
    Instrument("ppf", "80C", "Public Provident Fund", 0.071, 1.0, 5.0, 15.0),
    Instrument("fd_5yr", "80C", "5-year Tax Saving FD", 0.07, 1.0, 4.0, 5.0),
    Instrument("health_ins", "80D", "Health Insurance", 0.0, 1.0, 1.0, 0.0), # Zero return but pure protection
]

class TaxOptimizer:
    def __init__(self, available_instruments: List[Instrument] = None):
        if available_instruments is None:
            self.instruments = AVAILABLE_INSTRUMENTS
        else:
            self.instruments = available_instruments

    def optimize(self, user_headroom: Dict[str, float], 
                 liquidity_deadline_years: float = 10.0,
                 max_risk_tolerance: float = 3.0,
                 total_budget: float = 0.0) -> Dict[str, float]:
        """
        user_headroom: Dict like {"80C": 100000, "80CCD(1B)": 50000} representing remaining limits
        Runs PuLP LP Optimization:
        Objective: Maximize (Tax Saved Proxy) * 0.5 + (Return) * 0.3 - (Liquidity Disadvantage) * 0.2
        Subject To: Instrument lock_in <= liquidity_deadline_years, section cap <= headroom
        """
        prob = pulp.LpProblem("TaxOptimization", pulp.LpMaximize)

        # Filter valid instruments by hard constraints (time horizon & risk)
        valid_instruments = []
        for inst in self.instruments:
            # You shouldn't be advised a 15-year instrument if horizon is 2 years
            if inst.lock_in_years <= liquidity_deadline_years and inst.risk_score <= max_risk_tolerance:
                if inst.section in user_headroom and user_headroom[inst.section] > 0:
                    valid_instruments.append(inst)

        if not valid_instruments or total_budget <= 0:
            return {}

        # Decision Variables: Amount to invest in each valid instrument (Continuous)
        # Bounded between 0 and minimum of (total budget, section headroom)
        invest_vars = {}
        for inst in valid_instruments:
            max_cap = min(total_budget, user_headroom.get(inst.section, 0.0))
            invest_vars[inst.id] = pulp.LpVariable(
                f"invest_{inst.id}", 
                lowBound=0, 
                upBound=max_cap, 
                cat=pulp.LpContinuous
            )

        # Aggregate variables per section to ensure we don't exceed section headroom
        section_totals = {}
        for inst in valid_instruments:
            if inst.section not in section_totals:
                section_totals[inst.section] = pulp.lpSum([]) # empty sum
            section_totals[inst.section] += invest_vars[inst.id]

        # constraint 1: Section headroom limits
        for sec, lp_sum in section_totals.items():
            prob += (lp_sum <= user_headroom[sec], f"Limit_{sec}")

        # constraint 2: Total budget limit
        prob += (pulp.lpSum(invest_vars.values()) <= total_budget, "Total_Budget")

        # Objective Function formulation
        # Weighting returns linearly, penalizing high liquidity score (less liquid)
        # For proxying tax saved, every Rupee invested saves marginal rate. 
        # Since we just want to maximize the "tax-saving component", any money put towards these sections is equally good.
        # But we differentiate them purely based on returns and liquidity
        objective = pulp.lpSum([])
        
        # We'll normalize objective coefficients roughly
        for inst in valid_instruments:
            var = invest_vars[inst.id]
            # Assumed 30% marginal tax bracket for pure tax savings weight
            tax_savings_score = 0.30 * 0.5 
            expected_ret_score = inst.expected_return * 0.3
            liquidity_penalty = (inst.liquidity_score / 5.0) * 0.05 * 0.2  # Penalty scale
            
            coeff = tax_savings_score + expected_ret_score - liquidity_penalty
            objective += coeff * var

        prob += objective

        # Solve
        prob.solve(pulp.PULP_CBC_CMD(msg=0)) # msg=0 disables output

        # Parse Results
        results = {}
        if prob.status == pulp.LpStatusOptimal:
            for inst in valid_instruments:
                val = pulp.value(invest_vars[inst.id])
                if val and val > 0:
                    results[inst.name] = round(val, 2)
                    
        return results
