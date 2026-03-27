"use client";

import { PieChart, Pie, Cell, BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer } from 'recharts';
import { motion } from 'framer-motion';
import { TrendingUp, ShieldCheck, Banknote } from 'lucide-react';

export default function Dashboard({ data }: { data: any }) {
    if (!data || !data.current_taxes || !data.optimization_plan) {
        return (
            <div className="p-8 text-center bg-red-900/50 border border-red-500 rounded-2xl">
                <h3 className="text-xl font-bold text-red-400 mb-2">Diagnostic Error</h3>
                <p className="text-red-200">The AI engine returned an incomplete dataset. Please recalculate your scenario.</p>
            </div>
        );
    }

    const current_taxes = data.current_taxes || { old_regime: 0, new_regime: 0 };
    const optimization_plan = data.optimization_plan || {};
    const ai_advice = data.ai_advice || "No insights generated.";
    const ca_insights = data.ca_insights || {};

    // Speedometer data
    const taxSaved = optimization_plan.yearly_tax_savings;
    const oldTax = current_taxes.old_regime;
    const speedometerValue = oldTax > 0 ? ((taxSaved / oldTax) * 100).toFixed(1) : 0;
    
    const speedData = [
        { name: 'Saved', value: taxSaved },
        { name: 'Remaining Tax', value: Math.max(0, current_taxes.new_regime - taxSaved) }
    ];
    const COLORS = ['#10b981', '#ef4444']; // Emerald, Red

    // Money left on the table (80C / 80D / etc. Utilization)
    const utilizationData = Object.entries(optimization_plan)
        .filter(([key]) => key !== "yearly_tax_savings")
        .map(([section, amount]) => {
            const is80C = section.includes('80C');
            const is80D = section.includes('80D');
            const is80CCD = section.includes('80CCD(1B)');
            const fullLimit = is80C ? 150000 : is80D ? 25000 : is80CCD ? 50000 : 0;
            const numericAmount = typeof amount === 'number' ? amount : 0;
            return {
                name: section,
                Invested: numericAmount,
                LeftOnTable: Math.max(0, fullLimit - numericAmount)
            };
        }).filter(item => item.name !== "yearly_tax_savings");

    return (
        <div className="space-y-8 animate-in fade-in slide-in-from-bottom-8 duration-1000">
            <h2 className="text-4xl font-black bg-gradient-to-r from-teal-400 to-emerald-400 bg-clip-text text-transparent">
                Your TurboTax-style CA Report
            </h2>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
                {/* Gamified Speedometer Card */}
                <motion.div whileHover={{ scale: 1.02 }} className="bg-slate-800/50 border border-slate-700 p-6 rounded-3xl relative overflow-hidden shadow-2xl">
                    <h3 className="text-xl font-bold flex items-center gap-2 mb-4">
                        <TrendingUp className="text-teal-400" /> Tax Elimination Speedometer
                    </h3>
                    <div className="h-[250px] w-full mt-4">
                        <ResponsiveContainer width="100%" height="100%">
                            <PieChart>
                                <Pie
                                    data={speedData}
                                    cx="50%"
                                    cy="100%"
                                    startAngle={180}
                                    endAngle={0}
                                    innerRadius={80}
                                    outerRadius={120}
                                    paddingAngle={2}
                                    dataKey="value"
                                    stroke="none"
                                >
                                    {speedData.map((entry, index) => (
                                        <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                                    ))}
                                </Pie>
                                <Tooltip formatter={(val: number) => `₹${val.toLocaleString()}`} />
                            </PieChart>
                        </ResponsiveContainer>
                    </div>
                    <div className="absolute bottom-6 left-0 w-full text-center">
                        <p className="text-4xl font-black text-emerald-400">{speedometerValue}%</p>
                        <p className="text-slate-400 text-sm font-medium tracking-widest uppercase">of Liability Erased</p>
                    </div>
                </motion.div>

                {/* Money Left on the Table Card */}
                <motion.div whileHover={{ scale: 1.02 }} className="bg-slate-800/50 border border-slate-700 p-6 rounded-3xl shadow-2xl">
                    <h3 className="text-xl font-bold flex items-center gap-2 mb-6">
                        <Banknote className="text-emerald-400" /> Money Left on the Table
                    </h3>
                    <div className="h-[250px] w-full">
                        <ResponsiveContainer width="100%" height="100%">
                            <BarChart data={utilizationData} layout="vertical" margin={{ top: 0, right: 0, left: 10, bottom: 0 }}>
                                <XAxis type="number" hide />
                                <YAxis dataKey="name" type="category" axisLine={false} tickLine={false} tick={{fill: '#94a3b8'}} />
                                <Tooltip formatter={(val: number) => `₹${val.toLocaleString()}`} cursor={{fill: 'transparent'}} />
                                <Bar dataKey="Invested" stackId="a" fill="#10b981" radius={[4, 0, 0, 4]} />
                                <Bar dataKey="LeftOnTable" stackId="a" fill="#ef4444" radius={[0, 4, 4, 0]} />
                            </BarChart>
                        </ResponsiveContainer>
                    </div>
                </motion.div>
            </div>

            {/* AI Action Plan & CA Insights */}
            <div className="bg-slate-800/50 border border-slate-700 p-8 rounded-3xl shadow-2xl mt-8">
                <h3 className="text-2xl font-bold flex items-center gap-3 mb-6">
                    <ShieldCheck className="text-teal-400 w-8 h-8" /> 
                    AI Personal CA Action Plan
                </h3>
                
                <div className="prose prose-invert max-w-none text-slate-300">
                    <div dangerouslySetInnerHTML={{ __html: ai_advice.replace(/\n/g, '<br/>') }} />
                </div>

                <div className="mt-8 border-t border-slate-700 pt-8 grid grid-cols-1 md:grid-cols-2 gap-6">
                    <div className="bg-slate-900/50 p-6 rounded-2xl border border-teal-500/20">
                        <h4 className="font-bold text-teal-400 mb-2">Rule-of-3 HRA Optimization</h4>
                        <p className="text-3xl font-black mb-1">₹{(data.hra_exemption || 0).toLocaleString()}</p>
                        <p className="text-sm text-slate-400">Total Tax-Free HRA calculated vs New Regime Threshold.</p>
                    </div>
                    
                    <div className="bg-slate-900/50 p-6 rounded-2xl border border-emerald-500/20">
                        <h4 className="font-bold text-emerald-400 mb-2">Corporate NPS Restructuring</h4>
                        <p className="text-xl font-bold mb-1">{ca_insights?.nps_shield?.recommendation || "N/A"}</p>
                    </div>
                </div>
            </div>
        </div>
    );
}
