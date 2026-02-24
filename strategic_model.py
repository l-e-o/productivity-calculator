import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import numpy as np

# --- App Configuration ---
st.set_page_config(page_title="Strategic Business Case", layout="wide")

st.title("🏛️ Strategic Business Case & 3-Year ROI Model")
st.markdown("Quantifying the value of operational transformation.")

# --- Tabs for Clean UX ---
tab1, tab2, tab3 = st.tabs(["📊 Baseline & Industry", "💰 Investment", "📈 3-Year Cash Flow"])

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
    st.header("2. Capital & Operating Investment")
    st.markdown("Approximating the 'Total Cost of Ownership' including internal effort.")
    
    c1, c2 = st.columns(2)
    with c1:
        initial_setup = st.number_input("External Fees (Software/Consulting)", value=75000)
        recurring_fee = st.number_input("Annual Recurring SaaS/Support Fee", value=15000)
    
    with c2:
        impl_intensity = st.select_slider(
            "Internal Implementation Intensity",
            options=["Low", "Medium", "High"],
            value="Medium",
            help="Approximates internal team effort as a ratio of external fees."
        )
        # Intensity multipliers: Low=0.5x fees, Med=1.0x fees, High=1.5x fees
        intensity_map = {"Low": 0.5, "Medium": 1.0, "High": 1.5}
        internal_resource_cost = (initial_setup + recurring_fee) * intensity_map[impl_intensity]
        
        st.info(f"**Estimated Internal Labor Value:** ${internal_resource_cost:,.0f}")
        st.caption("Includes estimated time for Project Leads, SMEs, and Training.")
        
        wacc = st.slider("Discount Rate (WACC %)", 5, 15, 10) / 100

    total_upfront = initial_setup + internal_resource_cost
    annual_op_cost = recurring_fee

with tab3:
    # --- MATH ENGINE ---
    burdened_cost_pp = annual_salary * (1 + fringe_rate)
    hourly_rate = burdened_cost_pp / total_annual_hours_pp
    
    # 100% Potential Annual Saving (The "Steady State" Benefit)
    annual_waste_pp = total_annual_hours_pp * waste_pct
    max_annual_saving = (annual_waste_pp * num_employees) * improvement_target * hourly_rate
    
    # 3-Year Maturity Curve (Standard Consulting Ramp-up)
    y1_saving = max_annual_saving * 0.40  # Year 1: Adoption Phase
    y2_saving = max_annual_saving * 0.85  # Year 2: Optimization Phase
    y3_saving = max_annual_saving * 1.00  # Year 3: Mature Phase

    # Cash Flow Projection
    data = {
        "Year": ["Year 0 (Now)", "Year 1", "Year 2", "Year 3"],
        "Investment": [-total_upfront, -annual_op_cost, -annual_op_cost, -annual_op_cost],
        "Gross Savings": [0, y1_saving, y2_saving, y3_saving]
    }
    df = pd.DataFrame(data)
    df["Net Cash Flow"] = df["Investment"] + df["Gross Savings"]
    df["Cumulative Cash Flow"] = df["Net Cash Flow"].cumsum()

    # --- THE EXECUTIVE DASHBOARD ---
    st.header(f"Strategy Report: {industry}")
    
    npv = sum(val / (1 + wacc)**i for i, val in enumerate(df["Net Cash Flow"]))
    payback_months = (total_upfront / (y1_saving / 12)) if y1_saving > 0 else 0
    fte_reclaimed = (max_annual_saving / burdened_cost_pp)

    m1, m2, m3, m4 = st.columns(4)
    m1.metric("3-Year Project NPV", f"${npv:,.0f}")
    m2.metric("Discounted Payback", f"{payback_months:.1f} Months")
    m3.metric("Capacity Reclaimed", f"{fte_reclaimed:.1f} FTE")
    m4.metric("Steady State Saving", f"${max_annual_saving:,.0f}/yr")

    # J-Curve Chart
    st.subheader("Value Realization Path (Cumulative Cash Flow)")
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=df["Year"], y=df["Cumulative Cash Flow"],
        mode='lines+markers', line=dict(color='#1f77b4', width=4),
        fill='tozeroy', name="Cumulative Net Position"
    ))
    fig.update_layout(yaxis_title="Net Position ($)", template="plotly_white", height=400)
    st.plotly_chart(fig, use_container_width=True)

    # Financial Table
    st.subheader("Projected Cash Flows")
    st.table(df.style.format("${:,.0f}", subset=["Investment", "Gross Savings", "Net Cash Flow", "Cumulative Cash Flow"]))

    # Summary Text
    st.subheader("📝 Executive Summary")
    st.info(f"By optimizing identified waste of **{waste_hrs_pw:.1f} hours/week**, this project achieves a "
            f"Net Present Value of **${npv:,.0f}** over 3 years. The investment breaks even in "
            f"**{payback_months:.1f} months**, ultimately unlocking a capacity of **{fte_reclaimed:.1f} FTE**.")