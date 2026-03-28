from pydantic import BaseModel, Field
from typing import Optional

class IncomeDetails(BaseModel):
    gross_salary: float = Field(default=0.0, description="Total Gross Salary")
    standard_deduction: float = Field(default=0.0, description="Standard Deduction against salary")
    other_income_interest: float = Field(default=0.0, description="Income from other sources like 194A interest")
    business_income_44ada: float = Field(default=0.0, description="Presumptive professional income under 44ADA")
    
    @property
    def total_gross_income(self) -> float:
        return self.gross_salary + self.other_income_interest + self.business_income_44ada

class DeductionDetails(BaseModel):
    section_80c: float = Field(default=0.0, description="Total Section 80C deductions (EPF, LIC, ELSS, etc.)")
    section_80d: float = Field(default=0.0, description="Section 80D deductions for health insurance")
    section_80ccd1b: float = Field(default=0.0, description="NPS Tier 1 Additional Deduction 80CCD(1B)")
    section_80ccd2: float = Field(default=0.0, description="Employer NPS Contribution 80CCD(2)")
    section_24b: float = Field(default=0.0, description="Home loan interest 24(b)")

class ParsedTaxData(BaseModel):
    pan_number: Optional[str] = Field(None, description="PAN alphanumeric string")
    financial_year: Optional[str] = Field(None, description="Financial Year in YYYY-YY format, e.g. 2024-25")
    income: IncomeDetails = Field(default_factory=IncomeDetails)
    deductions: DeductionDetails = Field(default_factory=DeductionDetails)
    
    confidence: str = Field("HIGH", description="Set to 'LOW' if any mandatory fields (TAN, PAN) are completely missing/masked, or if the sum of income components does not mathematically match the stated gross salary, or if tax fields are visibly blank.")
    warnings: list[str] = Field(default_factory=list, description="List of specific strings detailing exactly why confidence is LOW (e.g. 'PAN is masked', 'Salary sum deviates by 3.1%', 'TDS Q4 missing').")
