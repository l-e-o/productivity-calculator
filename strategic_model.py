import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import numpy as np
import math

# --- App Configuration ---
st.set_page_config(page_title="Strategic Business Case", layout="wide")

st.title("🏛️ Strategic Business Case & ROI Realization Model")
st.markdown("Quantifying the multi-year value of operational transformation.")

# --- Tabs ---
tab1, tab2, tab3 = st.tabs(["📊 Baseline & Industry", "💰 Investment & Horizon", "📈 ROI Report"])

# =================================================================
# TAB 1: OPERATIONAL BASELINE (LOCKED STRUCTURE & HELP TOOLTIPS)
# =================================================================
with tab1:
    st.header("1. Operational Baseline")
    col1, col2 = st.columns(2)
    with col1:
        industry = st.selectbox(
            "Industry Vertical", 
            ["Logistics Service Provider (LSP)", "Manufacturing", "Retail"], 
            help="Contextualizes benchmarks. LSPs prioritize throughput; Retailers focus on availability and MFP."
        )
        
        # --- RESTORED INDUSTRY COMMENTARY ---
        if industry == "Retail":
            st.info("""
            **Retail Productivity Benchmarks:**
            * **Typical Burden Rate:** 22% - 28%
            * **Productivity Leakage:** 15% - 25% (High manual reconciliation in MFP/Assortment).
            * **BY Target Gain:** 40% - 60% via automated Financial & Inventory alignment.
            """)
        elif industry == "Logistics Service Provider (LSP)":
            st.info("""
            **LSP Productivity Benchmarks:**
            * **Typical Burden Rate:** 28% - 35%
            * **Productivity Leakage:** 20% - 30% (High 'swivel-chair' activity between TMS/WMS).
            * **BY Target Gain:** 30% - 50% via autonomous dispatch & execution.
            """)
        else: # Manufacturing
            st.info("""
            **Manufacturing Productivity Benchmarks:**
            * **Typical Burden Rate:** 25% - 32%
            * **Productivity Leakage:** 10% - 20% (Master data & schedule churn).
            * **BY Target Gain:** 50%+ via Cognitive demand/supply synchronization.
            """)

        num_employees = st.number_input("Total Headcount in Scope", min_value=1, value=105, help="Staff interacting with the AI.")
        annual_salary = st.number_input("Avg. Annual Salary ($)", value=100000, help="Base salary foundation.")
        fringe_rate = st.slider("Burden Rate (%)", 0, 50, 20, help="Super, Tax, Insurance. Standard AU is 25-30%.")
        burdened_cost_pp = annual_salary * (1 + fringe_rate/100)
    
    with col2:
        work_days = st.number_input("Working Days / Year", value=220, help="Annual productive days.")
        daily_hours = st.number_input("Standard Productive Hours / Day", value=7.50, help="Active task time per day.")
        
        total_annual_hours_pp = work_days * daily_hours
        hourly_rate_pp = burdened_cost_pp / total_annual_hours_pp
        
        st.divider()
        input_method = st.radio("Define Inefficiency Basis:", ["Hours per Week", "Percentage of Total Time"], horizontal=True)
        
        if input_method == "Hours per Week":
            baseline_waste_hrs_pw = st.number_input("Productive Inefficiency (Hrs/Wk/Person)", value=5.0)
            baseline_waste_pct = (baseline_waste_hrs_pw * 52) / total_annual_hours_pp
        else:
            baseline_waste_pct = st.slider("Inefficiency Percentage (%)", 0, 100, 20) / 100
        
        improvement_target = st.slider("Target Efficiency Gain (%)", 1, 100, 100, help="Efficiency recovered by AI.")

# =================================================================
# TAB 2: INVESTMENT & HORIZON (LOCKED STRUCTURE & HELP TOOLTIPS)
# =================================================================
with tab2:
    st.header("2. Investment & Time Horizon")
    c1, c2 = st.columns(2)
    with c1:
        solution_name = st.text_input("Solution Name", value="Blue Yonder Cognitive Merchandise Financial Planning", help="Specific solution for narrative context.")
        initial_setup = st.number_input("Consulting Services Fees", value=500000, help="One-time services costs.")
        recurring_fee = st.number_input("Annual SaaS Fees", value=1200000, help="Yearly subscription fee.")
        analysis_years = st.slider("ROI Horizon (Years)", 2, 10, 7)
        escalation_rate = st.slider("Annual Labor Escalation (%)", 0, 10, 3) / 100
    with c2:
        st.divider()
        impl_unit = st.radio("Implementation Unit:", ["Weeks", "Months"], horizontal=True)
        impl_duration = st.number_input(f"Duration ({impl_unit})", value=26)
        impl_factor = (52 - impl_duration)/52 if impl_unit == "Weeks" else (12 - impl_duration)/12
        
        st.subheader("Internal Team (Year 1)")
        key_users = st.number_input("Number of Key Users", value=5)
        impl_intensity = st.select_slider("Intensity", options=["Low", "Medium", "High"], value="Medium")
        intensity_map = {"Low": 250, "Medium": 500, "High": 750}
        client_internal_investment = (key_users * intensity_map[impl_intensity] * hourly_rate_pp)
        st.info(f"Calculated Client Investment: ${client_internal_investment:,.0f}")
        wacc = st.slider("Discount Rate (WACC %)", 5, 15, 10) / 100
    y1_investment_total = initial_setup + client_internal_investment + recurring_fee

# =================================================================
# TAB 3: ROI REPORT & RESTORED EXECUTIVE SUMMARY
# =================================================================
with tab3:
    st.header("📈 ROI Report & Targeter")
    target_mode = st.toggle("Enable Reverse Target Mode", help="Identify required hours for breakeven.")

    final_calc_pct = baseline_waste_pct
    
    if target_mode:
        target_yrs = st.number_input("Target Years to Breakeven", min_value=1.1, value=3.5, step=0.1)
        total_recover = y1_investment_total + (recurring_fee * (target_yrs - 1))
        effective_yrs = target_yrs - (1 - impl_factor)
        esc_hourly_rate = hourly_rate_pp * (1 + escalation_rate)
        final_calc_pct = (total_recover / (effective_yrs if effective_yrs > 0 else 1)) / (total_annual_hours_pp * num_employees * (improvement_target/100 if improvement_target > 1 else improvement_target) * esc_hourly_rate)
        target_hrs_pw_person = (final_calc_pct * total_annual_hours_pp) / 52
        st.markdown(f'<div style="background-color:rgba(30,144,255,0.1); border-left:5px solid #1E90FF; padding:20px; border-radius:5px; margin-bottom:25px;"><span style="font-size:22px; font-weight:bold; color:#1E90FF;">Target identified: Address {target_hrs_pw_person:.2f} productive hours / week per person.</span></div>', unsafe_allow_html=True)

    # --- MATH ENGINE (GROUNDED) ---
    savings, investments = [], []
    for yr in range(1, analysis_years + 1):
        yr_hourly_rate = (burdened_cost_pp * ((1 + escalation_rate) ** (yr - 1))) / total_annual_hours_pp
        yr_saving = (total_annual_hours_pp * final_calc_pct * num_employees) * (improvement_target/100 if improvement_target > 1 else improvement_target) * yr_hourly_rate
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
    total_tco = (recurring_fee * analysis_years) + initial_setup + client_internal_investment
    annual_hrs = total_annual_hours_pp * final_calc_pct * (improvement_target/100 if improvement_target > 1 else improvement_target) * num_employees
    fte_reclaimed = math.floor((annual_hrs / total_annual_hours_pp) * 10) / 10.0
    npv_val = sum(val / (1+wacc)**(i+1) for i, val in enumerate(df['Net Cash Flow']))

    st.subheader("Total Investment Summary (TCO)")
    i1, i2, i3, i4 = st.columns(4)
    i1.metric("Subscription Fees", f"${(recurring_fee * analysis_years):,.0f}")
    i2.metric("Consulting Services", f"${initial_setup:,.0f}")
    i3.metric("Client Investment", f"${client_internal_investment:,.0f}")
    i4.metric("TOTAL TCO", f"${total_tco:,.0f}")
    st.divider()

    st.subheader("Efficiency & Value Realization")
    v1, v2, v3 = st.columns(3)
    v1.metric("Pro-Rated Saving (Yr 1)", f"${savings[0]:,.0f}")
    v2.metric("Steady State Saving (Yr 2+)", f"${savings[1] if analysis_years > 1 else 0:,.0f}")
    v3.metric("FTE Reclaimed", f"{fte_reclaimed} FTE")

    v4, v5, v6 = st.columns(3)
    v4.metric("Annual Hours Reclaimed", f"{annual_hrs:,.0f} hrs")
    v5.metric("Monthly Hours Reclaimed", f"{(annual_hrs/12):,.0f} hrs")
    v6.metric(f"{analysis_years}-Year NPV", f"${npv_val:,.0f}")
    st.divider()

    # --- RESTORED EXPANDED EXECUTIVE SUMMARY ---
    st.subheader("🏛️ Strategic Analysis: Board-Level Overview")
    npv_status = "POSITIVE" if npv_val > 0 else "NEGATIVE"
    recommendation = "STRATEGICALLY VIABLE" if npv_val > 0 else "REQUIRES OPTIMIZATION"
    status_color = "#2E7D32" if npv_val > 0 else "#D32F2F"

    if "Financial Planning" in solution_name or "MFP" in solution_name:
        solution_context = "optimized Open-to-Buy (OTB) allocation, enhanced margin protection, and seamless top-down/bottom-up financial alignment."
    elif industry == "Logistics Service Provider (LSP)":
        solution_context = "increased throughput capacity and asset utilization in lean-margin environments."
    elif industry == "Manufacturing":
        solution_context = "enhanced production synchronization and reduced lead-time volatility."
    else:
        solution_context = "improved operational resilience and decision velocity."

    if npv_val < 0:
        analysis_logic = f'<div style="color:#D32F2F; margin-bottom:20px;"><b>⚠️ Strategic Context: {npv_status} NPV</b><br>Project costs currently exceed the discounted value of labor savings. Tactical adjustments required to meet the {wacc*100:.1f}% hurdle rate.</div>'
    else:
        analysis_logic = f'<div style="color:#2E7D32; margin-bottom:20px;"><b>✅ Financial Viability: {npv_status} NPV</b><br>The investment yields a <b>{npv_status} NPV of ${npv_val:,.0f}</b>, confirming that the project is <b>{recommendation}</b>. This positive Net Present Value signifies that the productivity dividends, when discounted at a {wacc*100:.1f}% cost of capital, outperform the total investment cost. As a "Go" decision, this project serves as a foundational step; while this model captures labor efficiency, it creates the operational "headroom" necessary to unlock secondary hard savings in inventory reduction and margin performance.</div>'

    summary_html = (
        f'<div style="border:1px solid rgba(128,128,128,0.3); padding:30px; border-radius:10px; font-family:\'Segoe UI\',sans-serif; line-height:1.8;">'
        f'<div style="margin-bottom:20px;"><b style="text-transform:uppercase;">Strategic Project Overview</b><br>'
        f'This initiative targets a TCO of <b>${total_tco:,.0f}</b> over a <b>{analysis_years}-year horizon</b>. Beyond a simple software deployment, this represents a transition to a <b>Cognitive Supply Chain</b> powered by <b>{solution_name}</b>. By embedding AI and ML into daily workflows, the organization shifts from reactive manual planning to <b>autonomous "exception-only" management</b>, ensuring human capital is focused on high-impact strategic trade-offs.</div>'
        f'<div style="margin-bottom:20px;"><b style="text-transform:uppercase;">Capacity Realization (Shadow Capacity)</b><br>'
        f'The implementation reclaims <b>{annual_hrs:,.0f} productive hours annually</b>: the financial and operational equivalent of adding <b>{fte_reclaimed} staff members</b> without escalating recruitment or payroll liabilities. This "Shadow Capacity" acts as a <b>Volume Multiplier</b> for the {industry} team, directly enabling {solution_context}</div>'
        f'<hr style="border:0; border-top:1px solid rgba(128,128,128,0.3); margin:25px 0;">{analysis_logic}</div>'
    )
    st.markdown(summary_html, unsafe_allow_html=True)

    # --- RESTORED COMPREHENSIVE GLOSSARY ---
    with st.expander("📝 Professional Glossary & Blue Yonder Strategic Alignment"):
        st.write("**Net Present Value (NPV) Analysis:** NPV calculates the total excess value generated by an investment after accounting for the time value of money and the cost of capital.")
        st.info(f"""
        **Blue Yonder Value Realization Framework**
        In alignment with **Blue Yonder's Cognitive Supply Chain** strategy, this model captures the foundational **Productivity Dividend** of the "Pivot to Growth" roadmap. 
        
        **Customer Performance Benchmarks:**
        * **Labor Productivity:** Typical realization of 15% to 30% efficiency gains through automated task prioritization.
        * **Operational Agility:** Creation of 'Shadow Capacity'—allowing teams to absorb 10-15% volume growth without adding headcount.
        * **Decision Velocity:** AI-assisted work directing reduces 'swivel-chair' activity, enabling planners to focus on high-impact strategic trade-offs.
        
        *Reference: www.blueyonder.com*
        """)
    
    # --- CHART WITH TOGGLE (REPOSITIONED) ---
    chart_view = st.radio("Chart View:", ["Cumulative Path", "Annual Flow"], horizontal=True, help="Toggle between cumulative ROI and annual cash flow.")
    
    fig = go.Figure()
    if chart_view == "Cumulative Path":
        fig.add_trace(go.Scatter(x=df["Period"], y=df["Cumulative Cash Flow"], mode='lines+markers', line=dict(color='#1f77b4', width=4), fill='tozeroy'))
        fig.update_layout(title="Cumulative Cash Flow Path", yaxis_title="Net Position ($)")
    else:
        fig.add_trace(go.Bar(x=df["Period"], y=df["Net Cash Flow"], marker_color='#1f77b4'))
        fig.update_layout(title="Annual Net Cash Flow", yaxis_title="Annual Result ($)")
    
    fig.add_hline(y=0, line_dash="dash", line_color="gray", opacity=0.3)
    fig.update_layout(height=450)
    st.plotly_chart(fig, use_container_width=True)

    st.dataframe(df.style.format({"Investment": "${:,.0f}", "Gross Savings": "${:,.0f}", "Net Cash Flow": "${:,.0f}", "Cumulative Cash Flow": "${:,.0f}"}), hide_index=True, use_container_width=True)