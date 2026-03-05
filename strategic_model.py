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
        num_employees = st.number_input("Headcount in Scope", min_value=1, value=50)
        annual_salary = st.number_input("Avg. Annual Salary ($)", value=95000, step=5000)
        fringe_rate = st.slider("Burden Rate (Super/Tax/Insurance %)", 0, 50, 28) / 100
        
    with col2:
        work_days = st.number_input("Working Days / Year", value=220)
        daily_hours = st.number_input("Standard Productive Hours / Day", value=7.5)
        
        st.divider()
        input_method = st.radio("Define Waste Basis:", ["Hours per Week", "Percentage of Total Time"], horizontal=True)
        total_annual_hours_pp = work_days * daily_hours
        
        if input_method == "Hours per Week":
            waste_hrs_pw = st.number_input("Identified Waste (Hrs/Week/Person)", value=8.0, step=0.5)
            weeks_per_year = work_days / 5
            waste_pct = (waste_hrs_pw * weeks_per_year) / total_annual_hours_pp
        else:
            waste_pct = st.slider("Estimated Unproductive Time (%)", 0, 100, 20) / 100
            waste_hrs_pw = (waste_pct * total_annual_hours_pp) / (work_days / 5)

        improvement_target = st.slider("Target Efficiency Gain (%)", 0, 100, 50) / 100

with tab2:
    st.header("2. Investment & Time Horizon")
    c1, c2 = st.columns(2)
    with c1:
        initial_setup = st.number_input("External Fees (Software/Consulting)", value=75000)
        recurring_fee = st.number_input("Annual Recurring SaaS/Support Fee", value=15000)
        # --- NEW: Time Horizon Slider ---
        analysis_years = st.slider("ROI Analysis Horizon (Years)", min_value=2, max_value=10, value=3)
    
    with c2:
        impl_intensity = st.select_slider(
            "Internal Implementation Intensity",
            options=["Low", "Medium", "High"],
            value="Medium"
        )
        intensity_map = {"Low": 0.5, "Medium": 1.0, "High": 1.5}
        internal_resource_cost = (initial_setup + recurring_fee) * intensity_map[impl_intensity]
        st.info(f"**Internal Labor Value:** ${internal_resource_cost:,.0f}")
        
        wacc = st.slider("Discount Rate (WACC %)", 5, 15, 10) / 100

    total_upfront = initial_setup + internal_resource_cost

with tab3:
    # --- DYNAMIC MATH ENGINE ---
    burdened_cost_pp = annual_salary * (1 + fringe_rate)
    hourly_rate = burdened_cost_pp / total_annual_hours_pp
    
    # 100% Potential Annual Saving
    max_annual_saving = (total_annual_hours_pp * waste_pct * num_employees) * improvement_target * hourly_rate
    
    # Build Time-Series Data
    years = [f"Year {i}" if i > 0 else "Year 0 (Now)" for i in range(analysis_years + 1)]
    investments = [-total_upfront] + ([-recurring_fee] * analysis_years)
    
    # Benefit Ramp-up logic: Yr1=40%, Yr2=85%, Yr3+=100%
    savings = [0]
    for yr in range(1, analysis_years + 1):
        if yr == 1:
            savings.append(max_annual_saving * 0.40)
        elif yr == 2:
            savings.append(max_annual_saving * 0.85)
        else:
            savings.append(max_annual_saving * 1.00)

    df = pd.DataFrame({
        "Period": years,
        "Investment": investments,
        "Gross Savings": savings
    })
    df["Net Cash Flow"] = df["Investment"] + df["Gross Savings"]
    df["Cumulative Cash Flow"] = df["Net Cash Flow"].cumsum()

    # --- THE EXECUTIVE DASHBOARD ---
    st.header(f"Projected Impact Over {analysis_years} Years")
    
    npv = sum(val / (1 + wacc)**i for i, val in enumerate(df["Net Cash Flow"]))
    payback_months = (total_upfront / (savings[1] / 12)) if savings[1] > 0 else 0
    fte_reclaimed = (max_annual_saving / burdened_cost_pp)

    m1, m2, m3, m4 = st.columns(4)
    m1.metric(f"{analysis_years}-Year NPV", f"${npv:,.0f}")
    m2.metric("Discounted Payback", f"{payback_months:.1f} Months")
    m3.metric("Capacity Reclaimed", f"{fte_reclaimed:.1f} FTE")
    m4.metric("Steady State Saving", f"${max_annual_saving:,.0f}/yr")

    # J-Curve Chart
    st.subheader("Value Realization Path (Cumulative Cash Flow)")
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=df["Period"], y=df["Cumulative Cash Flow"],
        mode='lines+markers', line=dict(color='#1f77b4', width=4),
        fill='tozeroy', name="Cumulative Net Position"
    ))
    fig.update_layout(yaxis_title="Net Position ($)", template="plotly_white", height=400)
    st.plotly_chart(fig, use_container_width=True)
    
    

    # Detailed Table
    st.subheader("Financial Detail Table")
    st.table(df.style.format("${:,.0f}", subset=["Investment", "Gross Savings", "Net Cash Flow", "Cumulative Cash Flow"]))

    # Summary Text
    st.subheader("📝 Executive Summary")
    st.info(f"Over a **{analysis_years}-year** horizon, this initiative delivers a Net Present Value of **${npv:,.0f}**. "
            f"The steady-state annual savings reach **${max_annual_saving:,.0f}**, achieving full maturity by Year 3.")