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
        annual_salary = st.number_input("Avg. Annual Salary ($)", value=95000, step=5000)
        fringe_rate = st.slider("Burden Rate (Super/Tax/Insurance %)", 0, 50, 28) / 100
        burdened_cost_pp = annual_salary * (1 + fringe_rate)
        
    with col2:
        work_days = st.number_input("Working Days / Year", value=220)
        daily_hours = st.number_input("Standard Productive Hours / Day", value=7.5)
        total_annual_hours_pp = work_days * daily_hours
        hourly_rate_pp = burdened_cost_pp / total_annual_hours_pp
        
        st.divider()
        input_method = st.radio("Define Inefficiency Basis:", ["Hours per Week", "Percentage of Total Time"], horizontal=True)
        
        if input_method == "Hours per Week":
            baseline_waste_hrs_pw = st.number_input("Productive Inefficiency (Hrs/Week/Person)", value=8.0, step=0.5)
            weeks_per_year = work_days / 5
            baseline_waste_pct = (baseline_waste_hrs_pw * weeks_per_year) / total_annual_hours_pp
        else:
            baseline_waste_pct = st.slider("Inefficiency Percentage (%)", 0, 100, 20) / 100
            baseline_waste_hrs_pw = (baseline_waste_pct * total_annual_hours_pp) / (work_days / 5)

        improvement_target = st.slider("Target Efficiency Gain (%)", 1, 100, 50) / 100

with tab2:
    st.header("2. Investment & Time Horizon")
    c1, c2 = st.columns(2)
    with c1:
        initial_setup = st.number_input("External Fees (Implementation/Consulting)", value=500000)
        recurring_fee = st.number_input("Annual SaaS Fee (Paid in Advance)", value=1200000)
        analysis_years = st.slider("ROI Analysis Horizon (Years)", min_value=2, max_value=10, value=5)
        escalation_rate = st.slider("Annual Labor Escalation (%)", 0, 10, 3) / 100
    
    with c2:
        st.subheader("Internal Project Team (Year 1 Only)")
        key_users = st.number_input("Number of Key Users / SMEs", min_value=1, value=5, step=1)
        impl_intensity = st.select_slider("Implementation Intensity", options=["Low", "Medium", "High"], value="Medium")
        
        intensity_map = {"Low": 250, "Medium": 500, "High": 750}
        internal_labor_invest = (key_users * intensity_map[impl_intensity] * hourly_rate_pp)
        st.info(f"**Year 1 Internal Labor Value:** ${internal_labor_invest:,.0f}")
        wacc = st.slider("Discount Rate (WACC %)", 5, 15, 10) / 100

    y1_investment_total = initial_setup + internal_labor_invest + recurring_fee

with tab3:
    st.header("📈 ROI Report & Targeter")
    
    st.subheader("🎯 Breakeven Targeter")
    target_mode = st.toggle("Enable Reverse Target Mode")
    
    calc_waste_pct = baseline_waste_pct
    calc_waste_hrs = baseline_waste_hrs_pw

    if target_mode:
        target_years = st.number_input("Target Years to Breakeven (Decimal)", min_value=1.1, max_value=float(analysis_years), value=3.5, step=0.1)
        total_cost_to_recover = y1_investment_total + (recurring_fee * (target_years - 1))
        req_annual_saving = total_cost_to_recover / (target_years - 1)
        
        esc_hourly_rate = hourly_rate_pp * (1 + escalation_rate)
        calc_waste_pct = req_annual_saving / (total_annual_hours_pp * num_employees * improvement_target * esc_hourly_rate)
        calc_waste_hrs = (calc_waste_pct * total_annual_hours_pp) / (work_days / 5)
        st.success(f"**Target Identified:** To break even in {target_years} years, address **{calc_waste_hrs:.2f} hours** per person/week.")

    # MATH ENGINE
    savings, investments = [], []
    for yr in range(1, analysis_years + 1):
        curr_rate = hourly_rate_pp * ((1 + escalation_rate) ** (yr - 1))
        yr_saving_calc = (total_annual_hours_pp * calc_waste_pct * num_employees) * improvement_target * curr_rate
        
        if yr == 1:
            savings.append(0)
            investments.append(-y1_investment_total)
        else:
            savings.append(yr_saving_calc)
            investments.append(-recurring_fee)
    
    df = pd.DataFrame({"Period": [f"Year {i}" for i in range(1, analysis_years + 1)], "Investment": investments, "Gross Savings": savings})
    df["Net Cash Flow"] = df["Investment"] + df["Gross Savings"]
    df["Cumulative Cash Flow"] = df["Net Cash Flow"].cumsum()
    
    total_horizon_investment = abs(df["Investment"].sum())
    npv_val = sum(val / (1 + wacc)**(i+1) for i, val in enumerate(df['Net Cash Flow']))
    
    # CALCULATE FTE EQUIVALENT (Steady State Year 2)
    # Reclaimed FTE = Annual Saving / Burdened Salary (at Year 2 escalation)
    fte_equiv = savings[1] / (burdened_cost_pp * (1 + escalation_rate))

    # DASHBOARD METRICS
    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Total Investment (TCO)", f"${total_horizon_investment:,.0f}")
    m2.metric("Annual Saving (Year 2)", f"${savings[1]:,.0f}")
    m3.metric("FTE Equivalent Reclaimed", f"{fte_equiv:.1f} FTE", help="Total full-time capacity recovered across the organization.")
    m4.metric(f"{analysis_years}-Year NPV", f"${npv_val:,.0f}")

    st.divider()

    graph_view = st.radio("View:", ["Cumulative Cash Flow", "Annual Net Cash Flow"], horizontal=True)
    fig = go.Figure()
    y_data = df["Cumulative Cash Flow"] if "Cumulative" in graph_view else df["Net Cash Flow"]
    fig.add_trace(go.Scatter(x=df["Period"], y=y_data, mode='lines+markers', line=dict(color='#1f77b4', width=4), fill='tozeroy' if "Cumulative" in graph_view else None))
    fig.add_hline(y=0, line_dash="dash", line_color="white", opacity=0.3)
    fig.update_layout(template="plotly_white", height=400)
    st.plotly_chart(fig, use_container_width=True)

    st.subheader("Financial Detail Table")
    st.table(df.style.format("${:,.0f}", subset=["Investment", "Gross Savings", "Net Cash Flow", "Cumulative Cash Flow"]))