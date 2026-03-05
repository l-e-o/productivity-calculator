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
        num_employees = st.number_input("Total Headcount in Scope (Beneficiaries)", min_value=1, value=50)
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
        initial_setup = st.number_input("External Fees (Implementation/Consulting)", value=500000)
        recurring_fee = st.number_input("Annual SaaS Fee (Paid in Advance)", value=1200000)
        analysis_years = st.slider("ROI Analysis Horizon (Years)", min_value=2, max_value=10, value=5)
        escalation_rate = st.slider("Annual Labor Escalation/Inflation (%)", 0, 10, 3) / 100
    
    with c2:
        st.subheader("Internal Project Team (Year 1 Implementation)")
        key_users = st.number_input("Number of Key Users / SMEs", min_value=1, value=5, step=1)
        
        impl_intensity = st.select_slider(
            "Internal Implementation Intensity",
            options=["Low", "Medium", "High"],
            value="Medium"
        )
        
        intensity_map = {"Low": 250, "Medium": 500, "High": 750}
        burdened_cost_pp = annual_salary * (1 + fringe_rate)
        hourly_rate_pp = burdened_cost_pp / (work_days * daily_hours)
        
        internal_labor_invest = (key_users * intensity_map[impl_intensity] * hourly_rate_pp)
        st.info(f"**Year 1 Internal Labor Value:** ${internal_labor_invest:,.0f}")
        
        wacc = st.slider("Discount Rate (WACC %)", 5, 15, 10) / 100

    y1_investment_total = initial_setup + internal_labor_invest + recurring_fee

with tab3:
    # --- MATH ENGINE ---
    savings_list = []
    investments_list = []
    
    for yr in range(1, analysis_years + 1):
        current_yr_hourly_rate = hourly_rate_pp * ((1 + escalation_rate) ** (yr - 1))
        yr_max_saving = (total_annual_hours_pp * waste_pct * num_employees) * improvement_target * current_yr_hourly_rate
        
        if yr == 1:
            savings_list.append(0) # Year 1 Implementation
            investments_list.append(-y1_investment_total)
        else:
            savings_list.append(yr_max_saving) # Steady State Starts Year 2
            investments_list.append(-recurring_fee)

    years = [f"Year {i}" for i in range(1, analysis_years + 1)]

    df = pd.DataFrame({
        "Period": years,
        "Investment": investments_list,
        "Gross Savings": savings_list
    })
    
    df["Net Cash Flow"] = df["Investment"] + df["Gross Savings"]
    df["Cumulative Cash Flow"] = df["Net Cash Flow"].cumsum()

    # --- THE EXECUTIVE DASHBOARD ---
    st.header(f"Projected Impact: {industry}")
    
    npv = sum(val / (1 + wacc)**(i+1) for i, val in enumerate(df["Net Cash Flow"]))
    steady_state = savings_list[-1]
    
    # Metrics
    m1, m2, m3, m4 = st.columns(4)
    m1.metric(f"{analysis_years}-Year NPV", f"${npv:,.0f}")
    m1.caption(f"Terminal Year Saving: ${steady_state:,.0f}/yr")
    
    # Calculate Year 2 (First Year of Benefits) for clarity
    m2.metric("Year 2 Base Saving", f"${savings_list[1]:,.0f}")
    m3.metric("Year 1 Cash Requirement", f"${y1_investment_total:,.0f}")
    m4.metric("Inflation (Labor Escalation)", f"{escalation_rate*100:.1f}%")

    # --- PIVOTABLE GRAPH LOGIC ---
    st.divider()
    graph_view = st.radio("Select Visualization View:", ["Cumulative Cash Flow (J-Curve)", "Annual Net Cash Flow"], horizontal=True)

    fig = go.Figure()

    if graph_view == "Cumulative Cash Flow (J-Curve)":
        y_data = df["Cumulative Cash Flow"]
        title = "Value Realization Path (Cumulative Position)"
        fill = 'tozeroy'
    else:
        y_data = df["Net Cash Flow"]
        title = "Annual Operational Performance (Net Cash Flow)"
        fill = None

    fig.add_trace(go.Scatter(
        x=df["Period"], y=y_data,
        mode='lines+markers', line=dict(color='#1f77b4', width=4),
        fill=fill, name="Net Position"
    ))
    
    fig.add_hline(y=0, line_dash="dash", line_color="white", opacity=0.3)
    fig.update_layout(title=title, yaxis_title="USD ($)", template="plotly_white", height=450)
    st.plotly_chart(fig, use_container_width=True)

    # Detailed Table
    st.subheader("Financial Detail Table")
    st.table(df.style.format("${:,.0f}", subset=["Investment", "Gross Savings", "Net Cash Flow", "Cumulative Cash Flow"]))

    st.info(f"**Logic Note:** Savings commence in Year 2. The terminal steady-state value of **${steady_state:,.0f}** in Year {analysis_years} "
            f"includes a compounded **{escalation_rate*100:.1f}%** annual labor escalation.")