from google import genai
import json

class AINarrativeGenerator:
    def __init__(self, api_key: str = None, use_ollama: bool = False):
        self.api_key = api_key
        self.use_ollama = use_ollama
        if not self.use_ollama and self.api_key:
            self.client = genai.Client(api_key=self.api_key)
        
    def generate_action_plan(self, tax_data, optimization_results) -> str:
        prompt = (
            "You are an expert Indian CA. Explain this tax optimization plan in simple terms, "
            "make it easy to understand for a typical working professional. Emphasize exactly what they "
            "need to do before March 31. Do not hallucinate numbers."
            f"\n\nContext Data: {json.dumps(tax_data, default=str)}"
            f"\n\nOptimization Results: {json.dumps(optimization_results, default=str)}"
        )
        
        if self.use_ollama:
            return self._call_ollama(prompt)
        elif self.api_key:
            response = self.client.models.generate_content(
                model='gemini-2.5-flash',
                contents=prompt
            )
            return response.text
        return "Please connect Gemini API or enable Ollama 'privacy mode' to generate AI narratives."
        
    def _call_ollama(self, prompt: str) -> str:
        import requests
        try:
            r = requests.post("http://localhost:11434/api/generate", json={
                "model": "llama3.1",
                "prompt": prompt,
                "stream": False
            }, timeout=30)
            if r.status_code == 200:
                return r.json().get("response", "No response from Ollama")
            return f"Error from Ollama: {r.status_code}"
        except Exception as e:
            return f"Failed to connect to local Ollama instance. Is it running? Error: {e}"

class WhatIfSimulator:
    def __init__(self, tax_engine, deduction_hunter, optimizer):
        self.engine = tax_engine
        self.hunter = deduction_hunter
        self.optimizer = optimizer
        
    def simulate_hike(self, current_gross: float, hike_percent: float):
        new_gross = current_gross * (1 + (hike_percent / 100))
        tax_res = self.engine.calculate_tax(new_gross, deductions=0) # without deductions
        return {
            "scenario": f"+{hike_percent}% Salary Hike",
            "new_gross": new_gross,
            "new_base_tax": tax_res["total_tax"]
        }
