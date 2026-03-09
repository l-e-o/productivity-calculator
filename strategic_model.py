import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import numpy as np

# --- App Configuration ---
st.set_page_config(page_title="Strategic Business Case", layout="wide")

st.title("🏛️ Strategic Business Case & ROI Realization Model")
st.markdown("Quantifying the multi-year value of operational transformation.")

# --- Tabs ---
tab1, tab2, tab3 = st.tabs(["📊 Baseline & Industry", "💰 Investment & Horizon", "📈 ROI Report"])

with tab1:
    st.header("1. Operational Baseline")
    col1, col2 = st.columns(2)
    with col1:
        industry = st.selectbox("Industry Vertical", ["Logistics Service Provider (LSP)", "Manufacturing", "Retail"])
        num_employees = st.number_input("Total Headcount in Scope", min_value=1, value=50)
        annual_salary = st.number_input("Avg. Annual Salary ($)", value=95000)
        fringe_rate = st.slider("Burden Rate (%)", 0, 50, 28) / 100
        burdened_cost_pp = annual_salary * (1 + fringe_rate)
    with col2:
        work_days = st.number_input("Working Days / Year", value=220)
        daily_hours = st.number_input("Standard Productive Hours / Day", value=7.50)
        total_annual_hours_pp = work_days * daily_hours
        hourly_rate_pp = burdened_cost_pp / total_annual_hours_pp
        st.divider()
        input_method = st.radio("Define Inefficiency Basis:", ["Hours per Week", "Percentage of Total Time"], horizontal=True)
        if input_method == "Hours per Week":
            baseline_waste_hrs_pw = st.number_input("Productive Inefficiency (Hrs/Wk)", value=8.0)
            baseline_waste_pct = (baseline_waste_hrs_pw * (work_days/5)) / total_annual_hours_pp
        else:
            baseline_waste_pct = st.slider("Inefficiency Percentage (%)", 0, 100, 20) / 100
        improvement_target = st.slider("Target Efficiency Gain (%)", 1, 100, 50) / 100

with tab2:
    st.header("2. Investment & Time Horizon")
    c1, c2 = st.columns(2)
    with c1:
        initial_setup = st.number_input("Consulting Services Fees", value=500000)
        recurring_fee = st.number_input("Annual SaaS Fees", value=1200000)
        analysis_years = st.slider("ROI Horizon (Years)", 2, 10, 7)
        escalation_rate = st.slider("Annual Labor Escalation (%)", 0, 10, 3) / 100
        st.divider()
        impl_unit = st.radio("Implementation Unit:", ["Weeks", "Months"], horizontal=True)
        impl_duration = st.number_input(f"Duration ({impl_unit})", value=26)
        impl_factor = (52 - impl_duration)/52 if impl_unit == "Weeks" else (12 - impl_duration)/12
    with c2:
        st.subheader("Internal Team (Year 1)")
        key_users = st.number_input("Number of Key Users", value=5)
        impl_intensity = st.select_slider("Intensity", options=["Low", "Medium", "High"], value="Medium")
        intensity_map = {"Low": 250, "Medium": 500, "High": 750}
        client_internal_investment = (key_users * intensity_map[impl_intensity] * hourly_rate_pp)
        st.info(f"Calculated Client Investment: ${client_internal_investment:,.0f}")
        wacc = st.slider("Discount Rate (WACC %)", 5, 15, 10) / 100
    y1_investment_total = initial_setup + client_internal_investment + recurring_fee

with tab3:
    st.header("📈 ROI Report & Targeter")
    target_mode = st.toggle("Enable Reverse Target Mode")
    calc_waste_pct = baseline_waste_pct
    
    if target_mode:
        target_yrs = st.number_input("Target Years to Breakeven", min_value=1.1, value=3.5, step=0.1)
        total_recover = y1_investment_total + (recurring_fee * (target_yrs - 1))
        effective_yrs = target_yrs - (1 - impl_factor)
        esc_hourly_rate = hourly_rate_pp * (1 + escalation_rate)
        calc_waste_pct = (total_recover / (effective_yrs if effective_yrs > 0 else 1)) / (total_annual_hours_pp * num_employees * improvement_target * esc_hourly_rate)
        target_hrs_pw = (calc_waste_pct * total_annual_hours_pp / (work_days / 5))
        st.markdown(f'<div style="background-color:rgba(30,144,255,0.1); border-left:5px solid #1E90FF; padding:20px; border-radius:5px; margin-bottom:25px;"><span style="font-size:1.1em;">Target identified for {target_yrs} yr breakeven:</span><br><span style="font-size:22px; font-weight:bold; color:#1E90FF;">Address {target_hrs_pw:.2f} productive hours / week per person.</span></div>', unsafe_allow_html=True)

    # Calculation Logic
    savings, investments = [], []
    for yr in range(1, analysis_years + 1):
        curr_rate = hourly_rate_pp * ((1 + escalation_rate) ** (yr - 1))
        yr_saving = (total_annual_hours_pp * calc_waste_pct * num_employees) * improvement_target * curr_rate
        if yr == 1:
            savings.append(yr_saving * impl_factor)
            investments.append(-y1_investment_total)
        else:
            savings.append(yr_saving)
            investments.append(-recurring_fee)
    
    df = pd.DataFrame({"Period": [f"Year {i}" for i in range(1, analysis_years + 1)], "Investment": investments, "Gross Savings": savings})
    df["Net Cash Flow"] = df["Investment"] + df["Gross Savings"]
    df["Cumulative Cash Flow"] = df["Net Cash Flow"].cumsum()

    # Metrics
    total_subs = recurring_fee * analysis_years
    total_tco = total_subs + initial_setup + client_internal_investment
    fte_reclaimed = (savings[1]/burdened_cost_pp) if analysis_years > 1 else 0
    annual_hrs = total_annual_hours_pp * calc_waste_pct * num_employees * improvement_target
    npv_val = sum(val / (1+wacc)**(i+1) for i, val in enumerate(df['Net Cash Flow']))

    st.subheader("Total Investment Summary (TCO)")
    i1, i2, i3, i4 = st.columns(4)
    i1.metric("Subscription Fees", f"${total_subs:,.0f}")
    i2.metric("Consulting Services", f"${initial_setup:,.0f}")
    i3.metric("Client Investment", f"${client_internal_investment:,.0f}")
    i4.metric("TOTAL TCO", f"${total_tco:,.0f}")
    st.divider()

    st.subheader("Efficiency & Value Realization")
    v1, v2, v3 = st.columns(3)
    v1.metric("Pro-Rated Saving (Yr 1)", f"${savings[0]:,.0f}")
    v2.metric("Steady State Saving (Yr 2+)", f"${savings[1] if analysis_years > 1 else 0:,.0f}")
    v3.metric("FTE Reclaimed", f"{fte_reclaimed:.1f} FTE")
    st.divider()

    # --- THE EXECUTIVE SUMMARY (Professional Polish) ---
    st.subheader("🏛️ Strategic Analysis: Board-Level Overview")
    
    npv_status = "POSITIVE" if npv_val > 0 else "NEGATIVE"
    recommendation = "STRATEGICALLY VIABLE" if npv_val > 0 else "REQUIRES OPTIMIZATION"
    status_color = "#2E7D32" if npv_val > 0 else "#D32F2F"

    if npv_val < 0:
        analysis_logic = (
            f'<div style="color:#D32F2F; margin-bottom:20px;"><b>⚠️ Strategic Context: {npv_status} NPV</b><br>'
            f'A negative NPV indicates that the project costs currently exceed the discounted value of projected productivity gains over {analysis_years} years. '
            f'At a {wacc*100:.1f}% discount rate, the investment profile requires tactical adjustments to reach the capital hurdle.</div>'
            f'<div><b>🛠️ Optimization Roadmap:</b><br>'
            f'1. <b>Scalability:</b> Increase the employee scope (currently {num_employees}) to lower per-unit cost.<br>'
            f'2. <b>Time-to-Value:</b> Accelerate implementation to pull forward the realization of steady-state savings.<br>'
            f'3. <b>Efficiency Depth:</b> Utilize AI-driven work prioritization to exceed the {improvement_target*100:.0f}% gain target.</div>'
        )
    else:
        analysis_logic = (
            f'<div style="color:#2E7D32; margin-bottom:20px;"><b>✅ Strategic Context: {npv_status} NPV</b><br>'
            f'A positive NPV confirms that the expected labor-capital efficiencies significantly outperform the investment cost. '
            f'This project is expected to generate <b>${npv_val:,.0f} in incremental value</b> above the corporate hurdle rate of {wacc*100:.1f}%.</div>'
            f'<div><b>🚀 Growth Reinvestment Strategy:</b><br>'
            f'1. <b>Operational Agility:</b> Pivot the {fte_reclaimed:.1f} reclaimed FTE capacity toward high-impact supply chain strategic planning.<br>'
            f'2. <b>Systemic Scaling:</b> Standardize the AI Copilot methodology across adjacent business units to compound NPV.<br>'
            f'3. <b>Hard Saving Correlation:</b> Begin measuring downstream improvements in inventory turns and OTIF enabled by this reclaimed capacity.</div>'
        )

    summary_html = (
        f'<div style="border:1px solid rgba(128,128,128,0.3); padding:30px; border-radius:10px; font-family:\'Segoe UI\',sans-serif; line-height:1.8;">'
        f'<div style="margin-bottom:20px;"><b style="text-transform:uppercase;">Strategic Project Overview</b><br>'
        f'This initiative targets a TCO of <b>${total_tco:,.0f}</b> over <b>{analysis_years} years</b>. The model evaluates '
        f'<b>Productivity Efficiency</b> realized through the deployment of AI-assisted work directing and attention focus mechanisms.</div>'
        f'<div style="margin-bottom:20px;"><b style="text-transform:uppercase;">Capacity Realization (Shadow Capacity)</b><br>'
        f'The implementation will reclaim <b>{annual_hrs:,.0f} productive hours annually</b>. This is the financial equivalent of '
        f'securing <b>{fte_reclaimed:.1f} additional FTEs</b> without escalating payroll, recruitment, or training liabilities. '
        f'This represents <b>Scalable Growth Capacity</b>, enabling the business to absorb higher volume or complexity within the existing team structure.</div>'
        f'<div style="margin-bottom:20px;"><b style="text-transform:uppercase;">Financial Viability</b><br>'
        f'The investment yields a <b>{npv_status} NPV of ${npv_val:,.0f}</b>. Steady-state annual savings reach <b>${savings[1] if analysis_years > 1 else 0:,.0f}</b> '
        f'post-implementation. Project Status: <b>{recommendation}</b>.</div>'
        f'<hr style="border:0; border-top:1px solid rgba(128,128,128,0.3); margin:25px 0;">'
        f'{analysis_logic}'
        f'</div>'
    )
    st.markdown(summary_html, unsafe_allow_html=True)

    # --- PROFESSIONAL GLOSSARY & MODEL SCOPE (Blue Yonder Context) ---
    with st.expander("📝 Professional Glossary & Model Scope"):
        st.write("""
        **Net Present Value (NPV) Analysis**
        NPV is the standard financial metric for evaluating project profitability. It calculates the difference between the present value of cash inflows and the present value of cash outflows over time.
        """)
        st.write(f"""
        * **Positive NPV:** Indicates the project's projected earnings (in today's dollars) exceed the anticipated costs. This is a primary indicator of a value-adding investment.
        * **Negative NPV:** Indicates the project's costs exceed the present value of its future benefits. This typically warrants a review of costs or an increase in project scope.
        * **Strategic Interpretation:** A dollar spent today is compared against the present value of future labor-saving dividends, adjusted for the corporate cost of capital ({wacc*100:.1f}%).
        """)
        st.info(f"""
        **Blue Yonder Strategic Alignment & Model Scope**
        Consistent with **Blue Yonder’s** focus on the "Cognitive Supply Chain," this model quantifies the ROI of human-centric AI. By utilizing AI-powered "Copilots" to direct work and focus user attention, this calculator measures the primary **Productivity Dividend**.
        
        **Exclusions:** This specific model focuses on labor efficiency. It does not yet quantify Blue Yonder’s downstream "Hard Saving" outcomes such as:
        * **Inventory Optimization:** Reductions in safety stock and carrying costs.
        * **Service Level Improvements:** Gains in On-Time In-Full (OTIF) metrics.
        * **Freight Spend Efficiency:** Reductions in expedited shipping through AI-driven planning.
        
        *Reference: www.blueyonder.com*
        """)

    # Visuals
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=df["Period"], y=df["Cumulative Cash Flow"], mode='lines+markers', line=dict(color='#1f77b4', width=4), fill='tozeroy'))
    fig.add_hline(y=0, line_dash="dash", line_color="gray", opacity=0.3)
    fig.update_layout(height=450, title="Cumulative Cash Flow Path")
    st.plotly_chart(fig, use_container_width=True)

    st.subheader("Financial Detail Table")
    st.dataframe(df.style.format({
        "Investment": "${:,.0f}", "Gross Savings": "${:,.0f}", 
        "Net Cash Flow": "${:,.0f}", "Cumulative Cash Flow": "${:,.0f}"
    }), hide_index=True, use_container_width=True)