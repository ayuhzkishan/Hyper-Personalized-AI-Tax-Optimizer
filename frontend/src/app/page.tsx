"use client";

import { useState } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { UploadCloud, ChevronRight, BrainCircuit } from "lucide-react";
import Dashboard from "../components/Dashboard";

export default function Home() {
  const [step, setStep] = useState(1);
  const [loading, setLoading] = useState(false);
  const [errorMsg, setErrorMsg] = useState("");
  
  // Form States
  const [geminiKey, setGeminiKey] = useState("");
  const [gross, setGross] = useState(1200000);
  const [rent, setRent] = useState(300000);
  const [hraReceived, setHra] = useState(200000);
  const [isMetro, setIsMetro] = useState(true);
  
  // Result State
  const [result, setResult] = useState<any>(null);

  const handleOptimize = async () => {
    setLoading(true);
    setErrorMsg("");
    setStep(3); // Move to loading screen
    
    try {
        const res = await fetch("http://localhost:8000/api/optimize", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({
                gemini_key: geminiKey || null,
                gross_salary: gross,
                rent_paid: rent,
                hra_received: hraReceived,
                is_metro: isMetro
            })
        });
        
        const data = await res.json();
        
        if (!data.success) {
            setErrorMsg(data.message || data.error || "The AI engine failed to optimize this scenario.");
            setStep(2);
            return;
        }
        
        setResult(data);
        setStep(4); // Move to Dashboard
    } catch (err: any) {
        console.error(err);
        setErrorMsg(err.message || "Failed to connect to the backend API.");
        setStep(2);
    } finally {
        setLoading(false);
    }
  }

  return (
    <main className="min-h-screen bg-gradient-to-br from-slate-950 via-slate-900 to-slate-950 text-white p-8 font-sans">
      <div className="max-w-5xl mx-auto">
        <header className="mb-12 text-center">
            <h1 className="text-5xl font-extrabold bg-gradient-to-r from-teal-400 to-emerald-400 bg-clip-text text-transparent mb-4">
            Hyper-Personalized CA
            </h1>
            <p className="text-slate-400 text-lg">Maximize wealth with AI-driven audit trails and mathematical precision.</p>
        </header>

        <div className="bg-white/5 backdrop-blur-2xl border border-white/10 p-8 md:p-12 rounded-3xl shadow-2xl relative overflow-hidden">
            <div className="absolute top-0 left-0 w-full h-1 bg-gradient-to-r from-teal-500 to-emerald-500" />
            
            <AnimatePresence mode="wait">
                {step === 1 && (
                    <motion.div 
                        initial={{ opacity: 0, x: 20 }}
                        animate={{ opacity: 1, x: 0 }}
                        exit={{ opacity: 0, x: -20 }}
                        key="step1"
                    >
                        <h2 className="text-3xl font-bold mb-6">Step 1: AI Configuration</h2>
                        <div className="grid gap-6">
                            <div>
                                <label className="block text-sm font-medium mb-2 text-slate-300">Gemini Cloud API Key (Optional)</label>
                                <input 
                                    type="password"
                                    value={geminiKey}
                                    onChange={e => setGeminiKey(e.target.value)}
                                    placeholder="AI Action Plan Generator Key"
                                    className="w-full bg-slate-800/50 border border-slate-700 rounded-xl p-4 focus:ring-2 focus:ring-teal-500 outline-none text-white" 
                                />
                            </div>
                            <button 
                                onClick={() => setStep(2)}
                                className="mt-8 bg-gradient-to-r from-teal-500 to-emerald-500 text-white rounded-xl p-4 font-bold flex items-center justify-center gap-2 hover:opacity-90 transition-opacity"
                            >
                                Continue to Profile <ChevronRight className="w-5 h-5" />
                            </button>
                        </div>
                    </motion.div>
                )}
                
                {step === 2 && (
                    <motion.div 
                        initial={{ opacity: 0, x: 20 }}
                        animate={{ opacity: 1, x: 0 }}
                        exit={{ opacity: 0, x: -20 }}
                        key="step2"
                    >
                        <h2 className="text-3xl font-bold mb-6">Step 2: Financial Profile</h2>
                        
                        {errorMsg && (
                            <div className="mb-6 p-4 bg-red-900/50 border border-red-500 rounded-xl text-red-200">
                                <span className="font-bold flex items-center gap-2">⚠️ Error Occurred:</span>
                                {errorMsg}
                            </div>
                        )}
                        
                        <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-8">
                            <div>
                                <label className="block text-sm text-slate-400 mb-2">Gross Salary (₹)</label>
                                <input type="number" value={gross} onChange={e => setGross(Number(e.target.value))} className="w-full bg-slate-800/50 border border-slate-700 rounded-xl p-4 text-white font-bold text-xl" />
                            </div>
                            <div>
                                <label className="block text-sm text-slate-400 mb-2">HRA Received (₹)</label>
                                <input type="number" value={hraReceived} onChange={e => setHra(Number(e.target.value))} className="w-full bg-slate-800/50 border border-slate-700 rounded-xl p-4 text-white font-bold text-xl" />
                            </div>
                            <div>
                                <label className="block text-sm text-slate-400 mb-2">Actual Rent Paid (₹)</label>
                                <input type="number" value={rent} onChange={e => setRent(Number(e.target.value))} className="w-full bg-slate-800/50 border border-slate-700 rounded-xl p-4 text-white font-bold text-xl" />
                            </div>
                            <div>
                                <label className="block text-sm text-slate-400 mb-2">Live in Metro?</label>
                                <div className="flex gap-4">
                                    <button onClick={() => setIsMetro(true)} className={`flex-1 p-4 rounded-xl border font-bold transition-all ${isMetro ? 'bg-teal-500/20 border-teal-500 text-teal-300' : 'bg-slate-800/50 border-slate-700 text-slate-400'}`}>Yes</button>
                                    <button onClick={() => setIsMetro(false)} className={`flex-1 p-4 rounded-xl border font-bold transition-all ${!isMetro ? 'bg-teal-500/20 border-teal-500 text-teal-300' : 'bg-slate-800/50 border-slate-700 text-slate-400'}`}>No</button>
                                </div>
                            </div>
                        </div>
                        
                        <div className="mt-8 flex justify-between">
                            <button onClick={() => setStep(1)} className="text-slate-400 hover:text-white transition-colors">Back</button>
                            <button 
                                onClick={handleOptimize}
                                className="bg-gradient-to-r from-teal-500 to-emerald-500 text-white rounded-xl px-8 py-4 font-bold hover:opacity-90 transition-opacity flex items-center gap-2 shadow-[0_0_20px_rgba(20,184,166,0.4)]"
                            >
                                <BrainCircuit /> Calculate Maximum Savings
                            </button>
                        </div>
                    </motion.div>
                )}
                
                {step === 3 && (
                    <motion.div 
                        initial={{ opacity: 0, scale: 0.95 }}
                        animate={{ opacity: 1, scale: 1 }}
                        key="step3"
                        className="text-center py-20"
                    >
                        <BrainCircuit className="w-24 h-24 mx-auto mb-8 text-teal-400 animate-pulse" />
                        <h2 className="text-4xl font-bold mb-4 bg-gradient-to-r from-teal-400 to-emerald-400 bg-clip-text text-transparent">Simulating Tax Code Millions of Times...</h2>
                        <p className="text-slate-400 text-xl max-w-lg mx-auto">The PuLP engine is finding the absolute mathematical optimum for your exact salary breakdown.</p>
                    </motion.div>
                )}

                {step === 4 && result && (
                    <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }}>
                         <Dashboard data={result} />
                         <button onClick={() => setStep(2)} className="mt-12 text-teal-400 hover:text-teal-300 font-bold mx-auto border border-teal-500/30 px-6 py-2 rounded-full border-dashed">
                            Recalculate Scenario
                         </button>
                    </motion.div>
                )}
            </AnimatePresence>
        </div>
      </div>
    </main>
  );
}
