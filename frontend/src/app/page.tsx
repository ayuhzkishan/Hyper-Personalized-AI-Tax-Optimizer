"use client";

import { useState } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { UploadCloud, ChevronRight, BrainCircuit, ArrowRight, ShieldCheck, LineChart, Sparkles } from "lucide-react";
import Dashboard from "../components/Dashboard";

export default function Home() {
  const [step, setStep] = useState(0);
  const [loading, setLoading] = useState(false);
  const [errorMsg, setErrorMsg] = useState("");
  
  // Form States
  const [geminiKey, setGeminiKey] = useState("");
  const [gross, setGross] = useState<number | ''>('');
  const [rent, setRent] = useState<number | ''>('');
  const [hraReceived, setHra] = useState<number | ''>('');
  const [isMetro, setIsMetro] = useState(true);
  const [liquidity, setLiquidity] = useState(3);
  const [riskTol, setRiskTol] = useState(3.0);
  
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
                gross_salary: Number(gross) || 0,
                rent_paid: Number(rent) || 0,
                hra_received: Number(hraReceived) || 0,
                is_metro: isMetro,
                liquidity_yrs: liquidity,
                risk_tol: riskTol
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

  const handleFileUpload = async (e: React.ChangeEvent<HTMLInputElement>) => {
      const file = e.target.files?.[0];
      if (!file) return;
      
      setLoading(true);
      setErrorMsg("");
      const formData = new FormData();
      formData.append("file", file);
      if (geminiKey) formData.append("gemini_key", geminiKey);

      try {
          const res = await fetch("http://localhost:8000/api/extract_pdf", {
              method: "POST",
              body: formData
          });
          const data = await res.json();
          if (data.success) {
              setGross(data.gross_salary);
          } else {
              setErrorMsg(data.message || data.error || "Failed to parse PDF");
          }
      } catch (err: any) {
          setErrorMsg("Failed to connect to extraction API");
      }
      setLoading(false);
  };

  return (
    <main className="min-h-screen bg-paper text-charcoal selection:bg-lime selection:text-wealth-900 font-sans">
      
      {/* Premium Minimal Navbar */}
      <nav className="border-b border-gray-200 bg-white/80 backdrop-blur-md sticky top-0 z-50">
        <div className="max-w-6xl mx-auto px-6 py-4 flex justify-between items-center">
            <div className="flex items-center gap-2">
                <div className="w-8 h-8 bg-wealth-900 rounded-sm flex items-center justify-center">
                    <Sparkles className="text-gold w-4 h-4" />
                </div>
                <span className="font-serif font-bold text-xl tracking-tight text-wealth-900">TaxOptimizer</span>
            </div>
            {step > 0 && (
                 <button onClick={() => setStep(0)} className="text-sm font-medium text-gray-500 hover:text-wealth-900 transition-colors">
                    Exit Workflow
                 </button>
            )}
        </div>
      </nav>

      <div className="max-w-6xl mx-auto px-6 py-12 md:py-20">
        <AnimatePresence mode="wait">
            
            {/* STEP 0: Landing Page */}
            {step === 0 && (
                <motion.div 
                    initial={{ opacity: 0, y: 20 }}
                    animate={{ opacity: 1, y: 0 }}
                    exit={{ opacity: 0, y: -20 }}
                    key="step0"
                    className="max-w-3xl mx-auto text-center mt-12 md:mt-24"
                >
                    <div className="inline-flex items-center gap-2 px-3 py-1 bg-lime/20 text-wealth-900 rounded-full text-xs font-semibold tracking-wide uppercase mb-8">
                        <ShieldCheck className="w-4 h-4" /> SECURE & PRIVATE AI
                    </div>
                    <h1 className="text-5xl md:text-7xl font-serif font-medium text-wealth-900 leading-tight mb-6">
                        Optimize your exact<br/>tax reality.
                    </h1>
                    <p className="text-lg md:text-xl text-gray-600 font-light mb-12 max-w-2xl mx-auto leading-relaxed">
                        An AI-powered personal finance mentor that actively hunts deductions, models regimes, and restructures your salary with absolute mathematical precision.
                    </p>
                    <button 
                        onClick={() => setStep(1)}
                        className="bg-wealth-900 text-white px-8 py-4 rounded-lg font-medium text-lg hover:bg-wealth-800 transition-all flex items-center gap-3 mx-auto shadow-xl shadow-wealth-900/20"
                    >
                        Start Your Strategy <ArrowRight className="w-5 h-5" />
                    </button>
                    
                    <div className="mt-24 grid grid-cols-1 md:grid-cols-3 gap-8 py-12 border-t border-gray-200 text-left">
                        <div>
                            <LineChart className="w-6 h-6 text-gold mb-4" />
                            <h3 className="font-serif font-semibold text-xl mb-2">Data-Driven Growth</h3>
                            <p className="text-sm text-gray-500">PuLP optimizer mathematically guarantees the absolute maximum rupees retained in your portfolio.</p>
                        </div>
                        <div>
                            <BrainCircuit className="w-6 h-6 text-wealth-700 mb-4" />
                            <h3 className="font-serif font-semibold text-xl mb-2">AI Execution</h3>
                            <p className="text-sm text-gray-500">Drag and drop Form 16s. Our Gemini Vision pipeline accurately identifies raw tax primitives instantly.</p>
                        </div>
                        <div>
                            <ShieldCheck className="w-6 h-6 text-lime mb-4" />
                            <h3 className="font-serif font-semibold text-xl mb-2">Privacy First</h3>
                            <p className="text-sm text-gray-500">All data explicitly runs through localized rule engines to keep your financial life perfectly private.</p>
                        </div>
                    </div>
                </motion.div>
            )}

            {/* STEP 1: Configuration */}
            {step === 1 && (
                <motion.div 
                    initial={{ opacity: 0, x: 20 }}
                    animate={{ opacity: 1, x: 0 }}
                    exit={{ opacity: 0, x: -20 }}
                    key="step1"
                    className="max-w-xl mx-auto"
                >
                    <div className="bg-white p-8 md:p-10 rounded-2xl shadow-sm border border-gray-100">
                        <h2 className="text-3xl font-serif text-wealth-900 mb-2">Engine Configuration</h2>
                        <p className="text-gray-500 mb-8 text-sm">Strictly configure your AI backend environment.</p>
                        
                        <div>
                            <label className="block text-sm font-semibold text-wealth-900 mb-3 uppercase tracking-wider">Gemini Cloud API Key (Optional)</label>
                            <input 
                                type="password"
                                value={geminiKey}
                                onChange={e => setGeminiKey(e.target.value)}
                                placeholder="Paste API Key..."
                                className="w-full bg-bone border border-gray-200 rounded-lg p-4 focus:ring-2 focus:ring-wealth-900 focus:outline-none transition-all placeholder:text-gray-400" 
                            />
                            <p className="text-xs text-gray-400 mt-2">Required for advanced AI Narrative generation and Vision-based Form 16 extraction.</p>
                        </div>
                        <button 
                            onClick={() => setStep(2)}
                            className="mt-10 w-full bg-wealth-900 text-white rounded-lg p-4 font-medium flex items-center justify-center gap-2 hover:bg-wealth-800 transition-colors shadow-md"
                        >
                            Continue to Profile <ChevronRight className="w-5 h-5 text-lime" />
                        </button>
                    </div>
                </motion.div>
            )}
            
            {/* STEP 2: Profile */}
            {step === 2 && (
                <motion.div 
                    initial={{ opacity: 0, x: 20 }}
                    animate={{ opacity: 1, x: 0 }}
                    exit={{ opacity: 0, x: -20 }}
                    key="step2"
                    className="max-w-3xl mx-auto"
                >
                    <div className="bg-white p-8 md:p-12 rounded-2xl shadow-sm border border-gray-100">
                        <h2 className="text-3xl font-serif text-wealth-900 mb-2">Financial Architecture</h2>
                        <p className="text-gray-500 mb-8 text-sm max-w-lg">We need a structural overview of your income to mathematically model exactly where the framework can extract tax efficiency.</p>
                        
                        {errorMsg && (
                            <div className="mb-8 p-4 bg-red-50 border-l-4 border-red-500 text-red-900 text-sm">
                                <span className="font-bold">Error Event: </span> {errorMsg}
                            </div>
                        )}
                        
                        {/* Drag and Drop Form 16 */}
                        <div className="border border-dashed border-gray-300 bg-bone rounded-xl p-8 text-center hover:border-wealth-700 hover:bg-gray-50 transition-all cursor-pointer relative mb-10 group">
                            <input type="file" onChange={handleFileUpload} accept=".pdf" className="absolute inset-0 w-full h-full opacity-0 cursor-pointer" />
                            <div className="w-12 h-12 bg-white rounded-full shadow-sm flex items-center justify-center mx-auto mb-4 group-hover:scale-110 transition-transform">
                                <UploadCloud className="w-6 h-6 text-wealth-700" />
                            </div>
                            <h3 className="font-medium text-wealth-900 mb-1">Upload Form 16 / Salary Slip</h3>
                            <p className="text-gray-500 text-sm">Automated localized NLP Extraction pipeline</p>
                            {loading && <p className="text-wealth-700 mt-4 text-sm font-semibold animate-pulse">Running extraction tensor...</p>}
                        </div>

                        <div className="flex items-center gap-4 mb-10 opacity-50">
                            <div className="flex-1 h-px bg-gray-200"></div>
                            <span className="text-gray-500 text-xs font-bold tracking-widest uppercase">Manual Fallback</span>
                            <div className="flex-1 h-px bg-gray-200"></div>
                        </div>
                        
                        <div className="grid grid-cols-1 md:grid-cols-2 gap-8 mb-10">
                            <div>
                                <label className="block text-xs font-bold text-gray-500 uppercase tracking-wider mb-2">Gross Salary Configuration (₹)</label>
                                <input type="number" placeholder="e.g. 1500000" value={gross} onChange={e => setGross(e.target.value === '' ? '' : Number(e.target.value))} className="w-full bg-bone border border-gray-200 rounded-lg p-3 text-wealth-900 font-medium text-lg focus:ring-1 focus:ring-wealth-900 outline-none transition-all" />
                            </div>
                            <div>
                                <label className="block text-xs font-bold text-gray-500 uppercase tracking-wider mb-2">HRA Component (₹)</label>
                                <input type="number" placeholder="e.g. 300000" value={hraReceived} onChange={e => setHra(e.target.value === '' ? '' : Number(e.target.value))} className="w-full bg-bone border border-gray-200 rounded-lg p-3 text-wealth-900 font-medium text-lg focus:ring-1 focus:ring-wealth-900 outline-none transition-all" />
                            </div>
                            <div>
                                <label className="block text-xs font-bold text-gray-500 uppercase tracking-wider mb-2">Actual Rent Disbursed (₹)</label>
                                <input type="number" placeholder="e.g. 400000" value={rent} onChange={e => setRent(e.target.value === '' ? '' : Number(e.target.value))} className="w-full bg-bone border border-gray-200 rounded-lg p-3 text-wealth-900 font-medium text-lg focus:ring-1 focus:ring-wealth-900 outline-none transition-all" />
                            </div>
                            <div>
                                <label className="block text-xs font-bold text-gray-500 uppercase tracking-wider mb-2">Metro Classification</label>
                                <div className="flex gap-3 mt-1">
                                    <button onClick={() => setIsMetro(true)} className={`flex-1 p-3 rounded-lg border font-medium transition-all ${isMetro ? 'bg-wealth-900 border-wealth-900 text-white' : 'bg-bone border-gray-200 text-gray-600 hover:bg-gray-100'}`}>Yes</button>
                                    <button onClick={() => setIsMetro(false)} className={`flex-1 p-3 rounded-lg border font-medium transition-all ${!isMetro ? 'bg-wealth-900 border-wealth-900 text-white' : 'bg-bone border-gray-200 text-gray-600 hover:bg-gray-100'}`}>No</button>
                                </div>
                            </div>
                        </div>
                        
                        <div className="bg-bone p-6 rounded-xl border border-gray-100 mb-10">
                            <h3 className="font-serif font-bold text-wealth-900 mb-6 flex items-center gap-2">
                                <Sparkles className="w-4 h-4 text-gold" /> Investment Strategy Protocol
                            </h3>
                            <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
                                <div>
                                    <label className="block text-xs font-bold text-gray-500 uppercase tracking-wider mb-3">Liquidity Needs</label>
                                    <div className="flex gap-2">
                                        <button onClick={() => setLiquidity(3)} className={`flex-1 py-2 px-1 rounded-md border text-sm font-medium transition-all ${liquidity === 3 ? 'bg-wealth-900 border-wealth-900 text-white' : 'bg-white border-gray-200 text-gray-600'}`}>Medium (3Y)</button>
                                        <button onClick={() => setLiquidity(15)} className={`flex-1 py-2 px-1 rounded-md border text-sm font-medium transition-all ${liquidity === 15 ? 'bg-wealth-900 border-wealth-900 text-white' : 'bg-white border-gray-200 text-gray-600'}`}>Long (15Y+)</button>
                                    </div>
                                </div>
                                <div>
                                    <div className="flex justify-between items-end mb-3">
                                        <label className="block text-xs font-bold text-gray-500 uppercase tracking-wider">Risk Profile</label>
                                        <span className="text-wealth-900 font-bold text-sm bg-lime/30 px-2 py-0.5 rounded">{riskTol} / 5</span>
                                    </div>
                                    <input type="range" min="1" max="5" step="0.5" value={riskTol} onChange={e => setRiskTol(Number(e.target.value))} className="w-full accent-wealth-900" />
                                    <div className="flex justify-between text-[10px] text-gray-400 mt-2 font-bold uppercase tracking-wider">
                                        <span>Debt / Safe</span>
                                        <span>Equity / Aggr</span>
                                    </div>
                                </div>
                            </div>
                        </div>
                        
                        <div className="flex justify-between items-center pt-6 border-t border-gray-100">
                            <button onClick={() => setStep(1)} className="text-gray-500 font-medium hover:text-wealth-900 transition-colors">Go Back</button>
                            <button 
                                onClick={handleOptimize}
                                className="bg-wealth-900 text-white rounded-lg px-8 py-4 font-medium hover:bg-wealth-800 transition-all flex items-center gap-2 shadow-lg shadow-wealth-900/10"
                            >
                                Execute Protocol <ArrowRight className="w-4 h-4" />
                            </button>
                        </div>
                    </div>
                </motion.div>
            )}
            
            {/* STEP 3: Loading */}
            {step === 3 && (
                <motion.div 
                    initial={{ opacity: 0, scale: 0.95 }}
                    animate={{ opacity: 1, scale: 1 }}
                    key="step3"
                    className="text-center py-32 max-w-lg mx-auto"
                >
                    <div className="w-20 h-20 bg-lime/20 rounded-2xl flex items-center justify-center mx-auto mb-8 animate-pulse">
                        <BrainCircuit className="w-10 h-10 text-wealth-900" />
                    </div>
                    <h2 className="text-3xl font-serif text-wealth-900 mb-4">Simulating Reality...</h2>
                    <p className="text-gray-500 leading-relaxed">The PuLP engine is routing through India's tax slab topologies. Resolving Section 87A and HRA sub-thresholds in real-time.</p>
                </motion.div>
            )}

            {/* STEP 4: Dashboard */}
            {step === 4 && result && (
                <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} key="step4" className="max-w-5xl mx-auto">
                     <Dashboard data={result} />
                     <div className="text-center mt-16">
                        <button onClick={() => setStep(2)} className="text-wealth-900 font-medium border border-gray-300 bg-white px-8 py-3 rounded-lg hover:bg-gray-50 transition-colors shadow-sm">
                            Configure New Scenario
                        </button>
                     </div>
                </motion.div>
            )}
        </AnimatePresence>
      </div>
    </main>
  );
}
