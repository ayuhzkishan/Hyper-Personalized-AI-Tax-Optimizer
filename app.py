import streamlit as st
import pandas as pd
import plotly.express as px
from src.pdf_parser import PDFParser
from src.tax_engine import TaxEngine
from src.deduction_hunter import DeductionHunter
from src.optimizer import TaxOptimizer
from src.ai_narrative import AINarrativeGenerator, WhatIfSimulator
from src.personal_ca import PersonalCA

st.set_page_config(page_title="Hyper-Personalized Tax Optimizer", layout="wide", page_icon="💡")

st.markdown("""
<style>
    .stApp {
        background: radial-gradient(circle at top left, #1e1e2f, #0d0d14);
        color: #f1f1f1;
        font-family: 'Inter', sans-serif;
    }
    .main-header {
        font-size: 2.5rem;
        font-weight: 800;
        background: -webkit-linear-gradient(45deg, #FF6B6B, #4ECDC4);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 0px;
    }
    div[data-testid="stMetricValue"] {
        font-size: 2rem;
        color: #4ECDC4;
    }
    .glass-card {
        background: rgba(255, 255, 255, 0.05);
        backdrop-filter: blur(10px);
        -webkit-backdrop-filter: blur(10px);
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 12px;
        padding: 24px;
        margin-top: 16px;
        margin-bottom: 16px;
        box-shadow: 0 4px 30px rgba(0, 0, 0, 0.3);
    }
</style>
""", unsafe_allow_html=True)

st.markdown('<div class="main-header">Hyper-Personalized AI Tax Optimizer</div>', unsafe_allow_html=True)
st.caption("Maximize your wealth with PuLP Optimization and LLM-driven exact audit trails.")

# --- SIDEBAR: Configuration ---
with st.sidebar:
    st.header("⚙️ Configuration")
    gemini_key = st.text_input("Gemini API Key (Fast & Cloud)", type="password")
    use_ollama = st.checkbox("Enable Privacy Mode (Local Ollama Llama 3.1)", value=False)
    
    st.divider()
    fy = st.selectbox("Financial Year", ["2025-26", "2024-25"])
    
    if not gemini_key and not use_ollama:
        st.warning("⚠️ Enter Gemini key or enable Ollama for Pass 3 PDF Extraction and Narratives.")

# --- TABS ---
tab1, tab2, tab3, tab4 = st.tabs(["📄 Step 1: Input", "✨ Step 2: Optimization", "📈 Step 3: What-if", "🧠 Step 4: Personal CA"])

with tab1:
    st.markdown("### Profile Quiz & Income Details")
    multi_source = st.radio("Do you have income outside your salary?", ["No, just salary", "Yes, other sources (194A, 44ADA)"])
    
    # PDF Upload
    uploaded_file = st.file_uploader("Upload Form 16 / Salary Slips (PDF)", type="pdf")
    
    if uploaded_file is not None:
        with open("temp.pdf", "wb") as f:
            f.write(uploaded_file.getbuffer())
            
        with st.spinner("Parsing via 3-Pass AI Engine..."):
            parser = PDFParser(api_key=gemini_key if gemini_key else None)
            try:
                # We use regex mock for now since Form16x is mocked
                parsed_data = parser.parse("temp.pdf")
                st.success("Extracted Successfully!")
                
                st.write(f"**Gross Salary Extracted:** ₹{parsed_data.income.gross_salary:,.2f}")
                st.session_state['gross'] = parsed_data.income.gross_salary
            except Exception as e:
                st.error(f"Parser Error: {e}")
                st.info("Falling back to manual entry.")

    if 'gross' not in st.session_state:
        st.session_state['gross'] = 1250000.0

    st.markdown('<div class="glass-card">', unsafe_allow_html=True)
    gross_input = st.number_input("Gross Salary (₹)", value=st.session_state['gross'], step=10000.0)
    
    other_income = 0.0
    biz_income = 0.0
    if multi_source == "Yes, other sources (194A, 44ADA)":
        col_o1, col_o2 = st.columns(2)
        other_income = col_o1.number_input("Interest/Other Income (₹)", 0.0, step=1000.0)
        biz_income = col_o2.number_input("Business Income (44ADA) (₹)", 0.0, step=10000.0)
        
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Calculate initial Engine
    engine_old = TaxEngine(fy=fy, regime="old")
    engine_new = TaxEngine(fy=fy, regime="new")
    
    total_gross = gross_input + other_income + biz_income
    tax_old = engine_old.calculate_tax(total_gross, deductions=0)["total_tax"]
    tax_new = engine_new.calculate_tax(total_gross, deductions=0)["total_tax"]
    
    st.subheader("Current Base Tax (No Deductions Applied)")
    col1, col2 = st.columns(2)
    col1.metric("Old Regime Tax", f"₹ {tax_old:,.2f}")
    col2.metric("New Regime Tax", f"₹ {tax_new:,.2f}", delta=f"₹ {tax_old - tax_new:,.2f} vs Old", delta_color="inverse")
    
    # Save to session
    st.session_state['total_gross'] = total_gross

with tab2:
    st.markdown("### Profile Risk & Goals")
    c1, c2, c3 = st.columns(3)
    liquidity_yrs = c1.slider("Liquidity Horizon (Goals)", 1, 15, 3, help="When do you need the money? e.g. Home purchase in 3 years")
    risk_tol = c2.slider("Risk Tolerance", 1.0, 5.0, 3.0, help="1=Low Risk (FDs), 5=High Risk (Equities)")
    budget = c3.number_input("Available Budget to Invest (₹)", 0.0, 500000.0, 150000.0)
    
    if st.button("Run PuLP Tax Optimization", type="primary"):
        with st.spinner("Hunting deductions & Running Mult-Objective Constraints..."):
            hunter = DeductionHunter()
            # Let's say user already exhausted 50k in EPF
            hunter.add_existing_deduction("80C", 50000, "EPF from Form 16")
            
            headroom = {
                "80C": hunter.get_headroom("80C"),
                "80CCD(1B)": hunter.get_headroom("80CCD(1B)"),
                "80D": hunter.get_headroom("80D")
            }
            
            opt = TaxOptimizer()
            results = opt.optimize(headroom, liquidity_yrs, risk_tol, budget)
            
            st.markdown('<div class="glass-card">', unsafe_allow_html=True)
            st.subheader("Optimal Mathematical Plan")
            if not results:
                st.warning("No instruments fit your strict liquidity and risk constraints!")
            else:
                df = pd.DataFrame(list(results.items()), columns=["Instrument", "Suggested Allocation (₹)"])
                st.dataframe(df, use_container_width=True)
                
                # Chart
                fig = px.pie(df, values='Suggested Allocation (₹)', names='Instrument', hole=0.4)
                fig.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", font_color="white")
                st.plotly_chart(fig)
            st.markdown('</div>', unsafe_allow_html=True)
            
            # AI Narrative
            st.markdown("### AI Tax Advisory")
            ai = AINarrativeGenerator(gemini_key, use_ollama)
            advice = ai.generate_action_plan(
                {"gross": st.session_state.get('total_gross', 0), "headroom": headroom},
                results
            )
            st.info(advice)
            
            # Action Plan PDF (Placeholder)
            st.download_button("Download Action Plan PDF", "PDF binary mock", "tax_plan.pdf")

with tab3:
    st.markdown("### What-If Simulator")
    sim = WhatIfSimulator(TaxEngine(fy=fy, regime="new"), DeductionHunter(), TaxOptimizer())
    hike = st.slider("Expected Hike (%)", 0, 50, 15)
    
    res = sim.simulate_hike(st.session_state.get('total_gross', 1200000), hike)
    st.metric("New Tax Liability (New Regime)", f"₹{res['new_base_tax']:,.2f}", f"+ ₹{res['new_base_tax'] - tax_new:,.2f}")

with tab4:
    st.markdown("### 🧠 Advanced CA Optimizations")
    st.info("A calculator just fills forms. A CA structurally changes how you earn to legally harvest wealth.")
    
    col_ca1, col_ca2 = st.columns(2)
    
    with col_ca1:
        st.markdown('<div class="glass-card">', unsafe_allow_html=True)
        st.subheader("1. HRA vs Regime Evaluator")
        basic = st.number_input("Basic Salary component (₹)", value=st.session_state.get('total_gross', 1200000)*0.5, step=10000.0)
        hra_rec = st.number_input("HRA Received (₹)", value=st.session_state.get('total_gross', 1200000)*0.2, step=10000.0)
        rent = st.number_input("Actual Rent Paid (₹)", value=0.0, step=5000.0)
        is_metro = st.checkbox("Live in a Metro City?", value=True)
        
        exemption = PersonalCA.calculate_hra_exemption(basic, hra_rec, rent, is_metro)
        st.metric("Tax-Free HRA Exemption", f"₹{exemption:,.2f}")
        if exemption == 0 and rent > 0:
            st.warning("Your rent isn't high enough to break the 10% basic threshold. New Regime is likely better.")
        st.markdown('</div>', unsafe_allow_html=True)

        st.markdown('<div class="glass-card">', unsafe_allow_html=True)
        st.subheader("2. Corporate NPS (80CCD-2) Harvest")
        nps_advice = PersonalCA.restructure_corporate_nps(basic)
        st.success(nps_advice['recommendation'])
        st.metric("Estimated Tax Shield", f"₹{nps_advice['tax_saved_via_shift']:,.2f}")
        st.markdown('</div>', unsafe_allow_html=True)

    with col_ca2:
        st.markdown('<div class="glass-card">', unsafe_allow_html=True)
        st.subheader("3. Regime Break-Even Point")
        if st.button("Calculate My Exact Break-Even"):
            with st.spinner("Running binary search on tax slabs..."):
                breakeven = PersonalCA.find_regime_breakeven(engine_old, engine_new, st.session_state.get('total_gross', 1200000))
                if not breakeven['possible']:
                    st.error(breakeven['msg'])
                else:
                    st.success(f"You must find exactly **₹{breakeven['breakeven_deductions_required']:,.2f}** in valid deductions for the Old Regime to mathematically beat the New Regime.")
        st.markdown('</div>', unsafe_allow_html=True)
        
        st.markdown('<div class="glass-card">', unsafe_allow_html=True)
        st.subheader("4. Capital Gains Harvesting")
        st.caption("FY25 Budget allows ₹1.25L of LTCG tax-free annually.")
        ltcg = st.number_input("Unbooked Long Term Capital Gains (₹)", value=0.0, step=10000.0)
        cg_advice = PersonalCA.capital_gains_harvesting(ltcg)
        st.metric("Gains to Book & Reinvest NOW", f"₹{cg_advice['book_gains_now']:,.2f}")
        st.metric("Permanent Tax Liability Erased", f"₹{cg_advice['tax_liability_erased']:,.2f}")
        st.markdown('</div>', unsafe_allow_html=True)
