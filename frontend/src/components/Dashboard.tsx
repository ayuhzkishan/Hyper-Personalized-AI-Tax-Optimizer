"use client";

import { PieChart, Pie, Cell, BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer } from 'recharts';
import { motion } from 'framer-motion';
import { TrendingUp, ShieldCheck, Banknote, Landmark } from 'lucide-react';

export default function Dashboard({ data }: { data: any }) {
    if (!data || !data.current_taxes || !data.optimization_plan) {
        return (
            <div className="p-8 text-center bg-red-50 border border-red-200 rounded-2xl">
                <h3 className="text-xl font-bold text-red-800 mb-2">Diagnostic Error</h3>
                <p className="text-red-600">The AI engine returned an incomplete dataset. Please recalculate your scenario.</p>
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
    // Wealth Green and a muted red
    const COLORS = ['#0F3D3E', '#ef4444'];

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
            <h2 className="text-4xl md:text-5xl font-serif text-wealth-900 leading-tight mb-2">
                Your Financial Architecture
            </h2>
            <p className="text-gray-500 mb-10 max-w-2xl">Based on your precise inputs, our localized solver has found mathematically absolute optimizations for your capital allocation.</p>

            {/* Explicit Regime Comparison Requirement */}
            <div className="bg-white border border-gray-200 rounded-3xl p-6 shadow-sm flex flex-col md:flex-row items-center justify-between gap-6">
                <div className="flex-1 w-full p-8 bg-bone rounded-2xl text-center border border-gray-100 relative overflow-hidden">
                    <h3 className="text-gray-500 font-bold tracking-widest uppercase text-xs mb-2 flex items-center justify-center gap-2"><Landmark className="w-4 h-4"/> Old Regime Baseline</h3>
                    <p className="text-4xl font-sans font-medium text-gray-800">₹{current_taxes.old_regime.toLocaleString()}</p>
                </div>
                
                <div className="flex shrink-0 w-12 h-12 bg-white border border-gray-100 shadow-sm rounded-full items-center justify-center font-bold text-wealth-900 text-sm italic font-serif z-10">
                    VS
                </div>

                <div className="flex-1 w-full p-8 bg-wealth-900 rounded-2xl text-center shadow-xl relative overflow-hidden transform md:scale-105">
                    <h3 className="text-lime font-bold tracking-widest uppercase text-xs mb-2 flex items-center justify-center gap-2"><TrendingUp className="w-4 h-4"/> Optimized New Regime</h3>
                    <p className="text-4xl font-sans font-medium text-white">₹{current_taxes.new_regime.toLocaleString()}</p>
                    <div className="absolute -right-10 -bottom-10 w-32 h-32 bg-white opacity-5 rounded-full blur-2xl"></div>
                </div>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
                {/* Gamified Speedometer Card */}
                <motion.div whileHover={{ y: -5 }} className="bg-white border border-gray-100 p-8 rounded-3xl relative overflow-hidden shadow-sm hover:shadow-md transition-all">
                    <h3 className="text-lg font-serif font-semibold text-wealth-900 flex items-center gap-2 mb-2">
                        Liability Eradication
                    </h3>
                    <p className="text-sm text-gray-500 mb-6">Percentage of total tax legally sidestepped.</p>
                    
                    <div className="h-[220px] w-full mt-4">
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
                                <Tooltip formatter={(val: number) => `₹${val.toLocaleString()}`} contentStyle={{borderRadius: '8px', border: 'none', boxShadow: '0 4px 6px -1px rgb(0 0 0 / 0.1)'}} />
                            </PieChart>
                        </ResponsiveContainer>
                    </div>
                    <div className="absolute bottom-6 left-0 w-full text-center">
                        <p className="text-4xl font-medium text-wealth-900">{speedometerValue}%</p>
                    </div>
                </motion.div>

                {/* Money Left on the Table Card */}
                <motion.div whileHover={{ y: -5 }} className="bg-white border border-gray-100 p-8 rounded-3xl shadow-sm hover:shadow-md transition-all">
                    <h3 className="text-lg font-serif font-semibold text-wealth-900 flex items-center gap-2 mb-2">
                        Capital Deployment Gaps
                    </h3>
                    <p className="text-sm text-gray-500 mb-8">Unutilized Section limits causing capital drift.</p>
                    
                    <div className="h-[220px] w-full">
                        <ResponsiveContainer width="100%" height="100%">
                            <BarChart data={utilizationData} layout="vertical" margin={{ top: 0, right: 0, left: 10, bottom: 0 }}>
                                <XAxis type="number" hide />
                                <YAxis dataKey="name" type="category" axisLine={false} tickLine={false} tick={{fill: '#6b7280', fontSize: 12}} />
                                <Tooltip formatter={(val: number) => `₹${val.toLocaleString()}`} cursor={{fill: 'transparent'}} contentStyle={{borderRadius: '8px', border: 'none', boxShadow: '0 4px 6px -1px rgb(0 0 0 / 0.1)'}} />
                                <Bar dataKey="Invested" stackId="a" fill="#0F3D3E" radius={[4, 0, 0, 4]} />
                                <Bar dataKey="LeftOnTable" stackId="a" fill="#ef4444" opacity={0.8} radius={[0, 4, 4, 0]} />
                            </BarChart>
                        </ResponsiveContainer>
                    </div>
                </motion.div>
            </div>

            {/* AI Action Plan & CA Insights */}
            <div className="bg-white border border-gray-100 p-8 md:p-12 rounded-3xl shadow-sm mt-8 relative overflow-hidden">
                <div className="absolute top-0 left-0 w-2 h-full bg-gold"></div>
                <h3 className="text-2xl font-serif font-semibold text-wealth-900 flex items-center gap-3 mb-6">
                    <ShieldCheck className="text-gold w-6 h-6" /> 
                    Executive Strategy Output
                </h3>
                
                <div className="prose prose-gray max-w-none text-gray-700 leading-relaxed font-serif">
                    <div dangerouslySetInnerHTML={{ __html: ai_advice.replace(/\n/g, '<br/>') }} />
                </div>

                <div className="mt-10 border-t border-gray-100 pt-10 grid grid-cols-1 md:grid-cols-2 gap-8">
                    <div className="bg-bone p-6 rounded-2xl border border-gray-200">
                        <h4 className="font-bold text-xs uppercase tracking-widest text-gray-500 mb-2">HRA Topology Optimization</h4>
                        <p className="text-3xl font-medium text-wealth-900 mb-1">₹{(data.hra_exemption || 0).toLocaleString()}</p>
                        <p className="text-sm text-gray-500">Maximum tax-free threshold computed via absolute minimum of Rule-of-3 criteria.</p>
                    </div>
                    
                    <div className="bg-bone p-6 rounded-2xl border border-gray-200">
                        <h4 className="font-bold text-xs uppercase tracking-widest text-gray-500 mb-2">Corporate NPS Restructuring</h4>
                        <p className="text-lg font-medium text-wealth-900 leading-snug">{ca_insights?.nps_shield?.recommendation || "System assessed: No restructuring needed."}</p>
                    </div>
                </div>
            </div>
        </div>
    );
}
