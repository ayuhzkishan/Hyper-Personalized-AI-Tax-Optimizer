from fastapi import FastAPI, File, UploadFile, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, Dict, Any
import shutil
import os

from src.pdf_parser import PDFParser
from src.tax_engine import TaxEngine
from src.deduction_hunter import DeductionHunter
from src.optimizer import TaxOptimizer
from src.ai_narrative import AINarrativeGenerator, WhatIfSimulator
from src.personal_ca import PersonalCA

app = FastAPI(title="Hyper-Personalized AI Tax Optimizer API")

# Enable CORS for React frontend (defaulting to localhost:3000)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class OptimizeRequest(BaseModel):
    gemini_key: Optional[str] = None
    use_ollama: bool = False
    fy: str = "2025-26"
    gross_salary: float
    rent_paid: float = 0.0
    hra_received: float = 0.0
    is_metro: bool = True
    liquidity_yrs: int = 3
    risk_tol: float = 3.0
    budget: float = 150000.0
    age: int = 30
    is_salary_pension: bool = True
    other_deductions: float = 0.0

@app.post("/api/extract_pdf")
async def extract_pdf(file: UploadFile = File(...), gemini_key: Optional[str] = Form(None)):
    temp_path = f"temp_{file.filename}"
    try:
        with open(temp_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
            
        parser = PDFParser(api_key=gemini_key)
        parsed_data = parser.parse(temp_path)
        
        return {
            "success": True, 
            "gross_salary": parsed_data.income.total_gross_income,
            "confidence": getattr(parsed_data, 'confidence', 'HIGH'),
            "warnings": getattr(parsed_data, 'warnings', []),
            "is_business": parsed_data.income.business_income_44ada > 0,
            "message": "Extracted successfully via AI."
        }
    except Exception as e:
        return {"success": False, "error": str(e), "message": "Failed to parse PDF"}
    finally:
        if os.path.exists(temp_path):
            os.remove(temp_path)

@app.post("/api/optimize")
async def run_optimization(req: OptimizeRequest):
    try:
        # Evaluate HRA
        hra_exemption = PersonalCA.calculate_hra_exemption(
            req.gross_salary * 0.5, # Assuming 50% basic for simple default
            req.hra_received,
            req.rent_paid,
            req.is_metro
        )
        
        # Calculate Engines
        engine_old = TaxEngine(fy=req.fy, regime="old")
        engine_new = TaxEngine(fy=req.fy, regime="new")
        
        # Calculate Engines (Old gets fixed deductions, New gets 0 Chapter VI-A deductions)
        total_fixed_deductions = hra_exemption + req.other_deductions
        
        tax_old = engine_old.calculate_tax(req.gross_salary, deductions=total_fixed_deductions, is_salary_pension=req.is_salary_pension, age=req.age)["total_tax"]
        tax_new = engine_new.calculate_tax(req.gross_salary, deductions=0, is_salary_pension=req.is_salary_pension, age=req.age)["total_tax"]
        
        # Optimize Deductions
        hunter = DeductionHunter()
        headroom = {
            "80C": hunter.get_headroom("80C"),
            "80CCD(1B)": hunter.get_headroom("80CCD(1B)"),
            "80D": hunter.get_headroom("80D")
        }
        
        opt = TaxOptimizer()
        results = opt.optimize(headroom, req.liquidity_yrs, req.risk_tol, req.budget)
        
        # CA Breakeven & Structuring
        breakeven = PersonalCA.find_regime_breakeven(engine_old, engine_new, req.gross_salary)
        nps_shield = PersonalCA.restructure_corporate_nps(req.gross_salary * 0.5)
        
        # Absolute Dual-Regime Optimization Math
        nps_old_benefit = nps_shield.get("tax_benefit_old_regime", 0)
        nps_new_benefit = nps_shield.get("tax_benefit_new_regime", 0)
        pulp_savings = results.get("yearly_tax_savings", 0)
        
        optimized_old = max(0, tax_old - pulp_savings - nps_old_benefit)
        optimized_new = max(0, tax_new - nps_new_benefit)
        
        regime_comparison = {
            "old": {
                "unoptimized": tax_old,
                "optimized": optimized_old,
                "potential_save": max(0, tax_old - optimized_old)
            },
            "new": {
                "unoptimized": tax_new,
                "optimized": optimized_new,
                "potential_save": max(0, tax_new - optimized_new)
            },
            "recommended": "Old" if optimized_old < optimized_new else "New"
        }

        # Narrative
        ai = AINarrativeGenerator(req.gemini_key, req.use_ollama)
        advice = ai.generate_action_plan(
            {"gross": req.gross_salary, "headroom": headroom, "hra_exemption": hra_exemption},
            results,
            regime_comparison
        )
        
        return {
            "success": True,
            "current_taxes": {
                "old_regime": tax_old,
                "new_regime": tax_new
            },
            "regime_comparison": regime_comparison,
            "hra_exemption": hra_exemption,
            "optimization_plan": results,
            "ai_advice": advice,
            "ca_insights": {
                "breakeven": breakeven,
                "nps_shield": nps_shield
            }
        }
    except Exception as e:
        error_msg = str(e)
        if "API key not valid" in error_msg or "API_KEY_INVALID" in error_msg:
            raise HTTPException(status_code=401, detail="Authentication Error: The provided Google Gemini API key is invalid.")
        elif "quota" in error_msg.lower() or "429" in error_msg:
            raise HTTPException(status_code=429, detail="Rate Limit Exceeded: The provided Google Gemini API quota has been exhausted.")
        raise HTTPException(status_code=500, detail=f"AI Engine Error: {error_msg.split('.')[0] if '.' in error_msg else error_msg}")
