from typing import Dict, Any

class PersonalCA:
    """
    Simulates a real human CA looking for structural changes to CTC and asset allocation 
    rather than just filling forms.
    """
    
    @staticmethod
    def calculate_hra_exemption(basic_salary: float, hra_received: float, rent_paid: float, is_metro: bool = True) -> float:
        """
        Rule of 3 for HRA Exemption: Minimum of:
        1. Actual HRA received
        2. 50% of Basic (Metro) or 40% (Non-Metro)
        3. Rent paid - 10% of Basic
        """
        if rent_paid <= 0 or hra_received <= 0:
            return 0.0
            
        limit_1 = hra_received
        limit_2 = (0.50 if is_metro else 0.40) * basic_salary
        limit_3 = rent_paid - (0.10 * basic_salary)
        
        return max(0.0, min(limit_1, limit_2, limit_3))

    @staticmethod
    def find_regime_breakeven(engine_old, engine_new, gross_income: float) -> Dict[str, Any]:
        """
        Finds the exact Rs of deductions needed for Old Regime to equal New Regime.
        """
        tax_new = engine_new.calculate_tax(gross_income, deductions=0)["total_tax"]
        
        # Binary search for the deduction amount that makes tax_old roughly equal to tax_new
        low = 0.0
        high = gross_income
        breakeven_deduction = 0.0
        tax_old = 0.0
        
        for _ in range(50): # 50 iterations is plenty for exact penny precision
            mid = (low + high) / 2.0
            tax_old = engine_old.calculate_tax(gross_income, deductions=mid)["total_tax"]
            
            if tax_old > tax_new:
                # Need more deductions to lower old tax
                low = mid
            else:
                high = mid
                
        # If at max deduction old tax is still higher, then new is inherently better
        if engine_old.calculate_tax(gross_income, deductions=gross_income)["total_tax"] > tax_new:
            return {"possible": False, "msg": "New Regime is mathematically superior regardless of deductions."}
            
        return {
            "possible": True,
            "breakeven_deductions_required": round(high, 2),
            "new_regime_base_tax": round(tax_new, 2)
        }

    @staticmethod
    def restructure_corporate_nps(basic_salary: float, marginal_tax_rate: float = 0.30) -> Dict[str, Any]:
        """
        Section 80CCD(2): Recommends shifting up to 10% of Basic Salary from Special Allowance to Employer NPS.
        Tax free in BOTH regimes.
        """
        harvestable_amount = 0.10 * basic_salary
        tax_saved = harvestable_amount * marginal_tax_rate
        return {
            "max_nps_shift": harvestable_amount,
            "tax_saved_via_shift": tax_saved,
            "recommendation": f"Ask HR to restructure Rs {harvestable_amount:,.2f} of your Special Allowance into Corporate NPS. This shields it completely from your {marginal_tax_rate*100}% bracket."
        }

    @staticmethod
    def capital_gains_harvesting(ltcg_gains: float) -> Dict[str, float]:
        """
        FY25 Budget allows Rs 1.25L of Long Term Capital Gains (LTCG) tax-free annually. 
        Recommends booking exact amount if available to step-up the purchase price.
        """
        harvestable = min(125000.0, ltcg_gains)
        tax_saved = harvestable * 0.125 # 12.5% LTCG rate
        return {
            "book_gains_now": harvestable,
            "tax_liability_erased": tax_saved
        }
