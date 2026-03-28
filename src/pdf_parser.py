import pdfplumber
import re
import json
from typing import Optional
from google import genai
from pydantic import ValidationError
from .models import ParsedTaxData, IncomeDetails

class PDFParser:
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key
        if self.api_key:
            self.genai_client = genai.Client(api_key=self.api_key)
        else:
            self.genai_client = None

    def parse(self, file_path: str) -> ParsedTaxData:
        # Pass 1: Try Mock Form16x (Structured standard tool for Part A & B)
        data = self._pass1_form16x(file_path)
        if self._validate_checksum(data):
            return data
            
        # Pass 2: pdfplumber + regex fallback for salary slips
        data = self._pass2_regex(file_path)
        if self._validate_checksum(data):
            return data
            
        # Pass 3: Gemini LLM Fallback (Strict JSON Schema field-extraction agent)
        if not self.genai_client:
            raise ValueError(
                "Pass 1 and 2 failed, and no Gemini API key provided for Pass 3 fallback. "
                "The format of the document is unrecognized."
            )
        
        data = self._pass3_llm(file_path)
        if data:
            if data.confidence != "HIGH" and data.income.total_gross_income <= 0:
                raise ValueError("Failed to parse PDF accurately across all 3 passes. Gross salary could not be identified.")
            return data
            
        raise ValueError("Failed to parse PDF accurately across all 3 passes. Parsing returned None.")

    def _pass1_form16x(self, file_path: str) -> Optional[ParsedTaxData]:
        # Form16x mock implementation
        # In a real environment, you'd use form16x directly:
        # parsed = form16x.parse(file_path)
        # return ParsedTaxData(...)
        return None

    def _pass2_regex(self, file_path: str) -> Optional[ParsedTaxData]:
        try:
            text = ""
            with pdfplumber.open(file_path) as pdf:
                for page in pdf.pages:
                    extract = page.extract_text()
                    if extract:
                        text += extract + "\n"
            
            # Gross Salary extraction (Basic Regex for Salary Slips)
            gross_match = re.search(r'(?i)gross salary[\s:]*([\d,]+)', text)
            if gross_match:
                val = float(gross_match.group(1).replace(',', ''))
                # Just mock other values as 0 for Pass 2 test
                return ParsedTaxData(income=IncomeDetails(gross_salary=val))
        except Exception:
            pass
        return None
        
    def _pass3_llm(self, file_path: str) -> Optional[ParsedTaxData]:
        try:
            text = ""
            with pdfplumber.open(file_path) as pdf:
                for page in pdf.pages:
                    extract = page.extract_text()
                    if extract:
                        text += extract + "\n"
                
            response = self.genai_client.models.generate_content(
                model='gemini-2.5-flash',
                contents=f"Extract exact tax details from this document and output JSON. CRITICAL: If mandatory fields like TAN are missing, PAN is masked, salary components do not mathematically sum to the gross payload (e.g. 3.1% gaps), TDS metrics are missing, or it contains structured Freelance 44ADA / Gig Worker data loosely aligned to Form 16, YOU MUST explicitly set `confidence` to 'LOW' and detail the exact deviations in the `warnings` array.\n\nDocument Text:\n{text}",
                config={
                    'response_mime_type': 'application/json',
                    'response_schema': ParsedTaxData,
                },
            )
            
            # Usually response.text is the JSON string
            json_str = response.text
            parsed_dict = json.loads(json_str)
            return ParsedTaxData(**parsed_dict)
        except Exception as e:
            print(f"LLM parsing failed: {e}")
            return None
        
    def _validate_checksum(self, data: Optional[ParsedTaxData], tolerance: float = 0.02) -> bool:
        if not data:
            return False
            
        # Example validation: extracted gross salary must be greater than 0 to be valid
        # A true production system would check: Sum of specific components == Gross Salary
        if data.income.gross_salary <= 0:
            return False
            
        return True
