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
            "gross_salary": parsed_data.income.gross_salary,
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
        
        tax_old = engine_old.calculate_tax(req.gross_salary, deductions=hra_exemption)["total_tax"]
        tax_new = engine_new.calculate_tax(req.gross_salary, deductions=0)["total_tax"]
        
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
        
        # Narrative
        ai = AINarrativeGenerator(req.gemini_key, req.use_ollama)
        advice = ai.generate_action_plan(
            {"gross": req.gross_salary, "headroom": headroom, "hra_exemption": hra_exemption},
            results
        )
        
        return {
            "success": True,
            "current_taxes": {
                "old_regime": tax_old,
                "new_regime": tax_new
            },
            "hra_exemption": hra_exemption,
            "optimization_plan": results,
            "ai_advice": advice,
            "ca_insights": {
                "breakeven": breakeven,
                "nps_shield": nps_shield
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
