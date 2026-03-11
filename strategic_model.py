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
# TAB 1: OPERATIONAL STRATEGY (RESTORED TOOLTIPS)
# =================================================================
with tab1:
    st.header("1. Operational Strategy")
    
    investment_strategy = st.radio(
        "Investment Context:",
        ["New Solution", "Pre-existing Solution Upgrade"],
        horizontal=True,
        help="New: Implementing a capability for the first time. Upgrade: Moving an existing Blue Yonder customer to an AI-Native/Cognitive version."
    )
    
    col1, col2 = st.columns(2)
    with col1:
        industry = st.selectbox(
            "Industry Vertical", 
            ["Retail", "Logistics Service Provider (LSP)", "Manufacturing"], 
            help="Contextualizes the business environment and selects relevant productivity benchmarks."
        )
        
        if industry == "Retail":
            if investment_strategy == "New Solution":
                st.info("**Retail (New):** Leakage: 15-25% (Manual siloes) | Target Gain: 40-60% (Full Automation)")
            else:
                st.info("**Retail (Upgrade):** Leakage: 5-12% (Residual friction) | Target Gain: 10-20% (AI Uplift)")
        elif industry == "Logistics Service Provider (LSP)":
            if investment_strategy == "New Solution":
                st.info("**LSP (New):** Leakage: 20-30% (Swivel-chair activity) | Target Gain: 30-50% (Optimization)")
            else:
                st.info("**LSP (Upgrade):** Leakage: 8-15% (Manual exceptions) | Target Gain: 10-15% (Mgmt by Exception)")
        else: # Manufacturing
            if investment_strategy == "New Solution":
                st.info("**Mfg (New):** Leakage: 20-35% (Siloed data) | Target Gain: 40-60% (Sync Signaling)")
            else:
                st.info("**Mfg (Upgrade):** Leakage: 7-12% (Scenario friction) | Target Gain: 15-25% (Cognitive Uplift)")

        num_employees = st.number_input("Total Headcount in Scope", min_value=1, value=105, help="Staff interacting with the solution.")
        annual_salary = st.number_input("Avg. Annual Salary ($)", value=100000, help="Average base salary.")
        fringe_rate = st.slider("Burden Rate (%)", 0, 50, 20, help="Local statutory costs (Super, Tax, etc.).")
        burdened_cost_pp = annual_salary * (1 + fringe_rate/100)
    
    with col2:
        work_days = st.number_input("Working Days / Year", value=220, help="Standardized annual working days.")
        daily_hours = st.number_input("Standard Productive Hours / Day", value=7.50, help="Actual time spent on core tasks.")
        total_annual_hours_pp = work_days * daily_hours
        hourly_rate_pp = burdened_cost_pp / total_annual_hours_pp
        
        st.divider()
        input_method = st.radio("Define Inefficiency Basis:", ["Hours per Week", "Percentage of Total Time"], horizontal=True, help="Select the metric that best captures current latent manual friction.")
        
        weekly_productive_hours = daily_hours * 5
        if input_method == "Hours per Week":
            baseline_waste_hrs_pw = st.number_input("Productive Inefficiency (Hrs/Wk/Person)", value=4.0, help="Hours lost per person per week.")
            baseline_waste_pct = baseline_waste_hrs_pw / weekly_productive_hours
        else:
            baseline_waste_pct_input = st.slider("Inefficiency Percentage (%)", 0, 100, 10, help="Portion of time consumed by friction.")
            baseline_waste_pct = baseline_waste_pct_input / 100
        
        improvement_target = st.slider("Target Efficiency Gain (%)", 1, 100, 100, help="Efficiency recovered by AI.")

# =================================================================
# TAB 2: INVESTMENT & HORIZON (RESTORED TOOLTIPS)
# =================================================================
with tab2:
    st.header("2. Investment & Time Horizon")
    c1, c2 = st.columns(2)
    with c1:
        solution_name = st.text_input("Solution Name", value="Cognitive Merchandise Financial Planning (CMFP)", help="Specific module name.")
        
        if investment_strategy == "Pre-existing Solution Upgrade":
            curr_sub = st.number_input("Current Annual Subscription ($)", value=800000, help="Current legacy spend.")
            future_sub = st.number_input("Future Annual Subscription ($)", value=1200000, help="Total new Cognitive spend.")
            y1_recurring = future_sub - curr_sub
            steady_state_recurring = future_sub
        else:
            y1_recurring = st.number_input("Annual SaaS Fees ($)", value=1200000, help="Recurring subscription cost.")
            steady_state_recurring = y1_recurring
        
        st.divider()
        initial_setup = st.number_input("Consulting Services Fees", value=500000, help="Implementation costs.")
        analysis_years = st.slider("ROI Horizon (Years)", 2, 10, 5, help="Evaluation period.")
        escalation_rate = st.slider("Annual Labor Escalation (%)", 0, 10, 3, help="Projected labor inflation.")

    with c2:
        st.divider()
        if 'dur_key' not in st.session_state:
            st.session_state.dur_key = 26.0
        if 'last_unit' not in st.session_state:
            st.session_state.last_unit = "Weeks"

        def convert_duration():
            current_unit = st.session_state.unit_choice
            if current_unit != st.session_state.last_unit:
                if current_unit == "Months":
                    st.session_state.dur_key = round(st.session_state.dur_key / 4.33, 1)
                else:
                    st.session_state.dur_key = round(st.session_state.dur_key * 4.33, 1)
                st.session_state.last_unit = current_unit

        impl_unit = st.radio("Implementation Unit:", ["Weeks", "Months"], horizontal=True, key="unit_choice", on_change=convert_duration, help="Unit for deployment timeline.")
        impl_duration = st.number_input(f"Duration ({impl_unit})", key="dur_key", step=0.1, help="Time to go-live.")
        impl_factor = (52 - impl_duration)/52 if impl_unit == "Weeks" else (12 - impl_duration)/12
        
        st.subheader("Internal Team (Year 1)")
        key_users = st.number_input("Number of Key Users", value=5, help="Internal implementation SMEs.")
        impl_intensity = st.select_slider("Intensity", options=["Low", "Medium", "High"], value="Medium", help="Hours required from SMEs.")
        intensity_map = {"Low": 250, "Medium": 500, "High": 750}
        client_internal_investment = (key_users * intensity_map[impl_intensity] * hourly_rate_pp)
        st.info(f"Calculated Client Investment (Shadow Cost): ${client_internal_investment:,.0f}")
        
        wacc = st.slider("Discount Rate (WACC %)", 5, 15, 10, help="Hurdle rate for NPV.")

    y1_investment_total = initial_setup + client_internal_investment + y1_recurring

# =================================================================
# TAB 3: ROI REPORT (ULTRA-PRECISION & RESTORED NARRATIVES)
# =================================================================
with tab3:
    st.header("📈 ROI Report & Targeter")
    
    def get_be_years(in_waste_pct):
        s, i = [], []
        for yr in range(1, analysis_years + 1):
            yr_rate = (burdened_cost_pp * ((1 + escalation_rate/100) ** (yr - 1))) / total_annual_hours_pp
            yr_sav = (total_annual_hours_pp * in_waste_pct * num_employees) * (improvement_target/100) * yr_rate
            if yr == 1:
                s.append(yr_sav * impl_factor)
                i.append(-y1_investment_total)
            else:
                s.append(yr_sav)
                i.append(-steady_state_recurring)
        cum_cf = np.cumsum(np.array(s) + np.array(i))
        for idx in range(len(cum_cf)):
            if cum_cf[idx] >= 0:
                if idx == 0: return y1_investment_total / (s[0]) if s[0] > 0 else 0
                prev_cum = cum_cf[idx-1]
                net_now = (s[idx] + i[idx])
                return idx + (abs(prev_cum) / net_now) if net_now > 0 else idx
        return 0.0

    current_be = get_be_years(baseline_waste_pct)
    target_mode = st.toggle("Enable Reverse Target Mode", help="Breakeven analysis.")
    final_calc_pct = baseline_waste_pct
    
    if target_mode:
        target_yrs = st.number_input("Target Years to Breakeven", min_value=1.1, value=float(round(current_be, 2)) if current_be > 0 else 3.7, step=0.1, help="Desired years to achieve full payback.")
        
        cumulative_investment = y1_investment_total + (steady_state_recurring * (target_yrs - 1))
        weight_sum = 0
        for yr in range(1, int(math.ceil(target_yrs)) + 1):
            yr_rate = (burdened_cost_pp * ((1 + escalation_rate/100) ** (yr - 1))) / total_annual_hours_pp
            yr_weight = total_annual_hours_pp * num_employees * (improvement_target/100) * yr_rate
            if yr == 1:
                weight_sum += yr_weight * impl_factor
            elif yr < target_yrs:
                weight_sum += yr_weight
            else:
                fraction = target_yrs - (yr - 1)
                weight_sum += yr_weight * fraction
        
        final_calc_pct = cumulative_investment / weight_sum if weight_sum > 0 else 0
        target_hrs_pw_person = final_calc_pct * (daily_hours * 5)
        
        st.markdown(f'<div style="background-color:rgba(30,144,255,0.1); border-left:5px solid #1E90FF; padding:20px; border-radius:5px; margin-bottom:25px;"><span style="font-size:22px; font-weight:bold; color:#1E90FF;">Target identified: Address {target_hrs_pw_person:.2f} productive hours / week per person.</span></div>', unsafe_allow_html=True)

    # Final Math Processing
    savings, investments = [], []
    for yr in range(1, analysis_years + 1):
        yr_hourly_rate = (burdened_cost_pp * ((1 + escalation_rate/100) ** (yr - 1))) / total_annual_hours_pp
        yr_saving = (total_annual_hours_pp * final_calc_pct * num_employees) * (improvement_target/100) * yr_hourly_rate
        if yr == 1:
            savings.append(yr_saving * impl_factor)
            investments.append(-y1_investment_total)
        else:
            savings.append(yr_saving)
            investments.append(-steady_state_recurring)
    
    df = pd.DataFrame({"Period": [f"Year {i}" for i in range(1, analysis_years + 1)], "Investment": investments, "Gross Savings": savings})
    df["Net Cash Flow"] = df["Investment"] + df["Gross Savings"]
    df["Cumulative Cash Flow"] = df["Net Cash Flow"].cumsum()

    final_be = get_be_years(final_calc_pct)
    total_sub_cost = y1_recurring + (steady_state_recurring * (analysis_years - 1))
    total_tco = total_sub_cost + initial_setup + client_internal_investment
    annual_hrs = total_annual_hours_pp * final_calc_pct * (improvement_target/100) * num_employees
    fte_reclaimed = math.floor((annual_hrs / total_annual_hours_pp) * 10) / 10.0
    npv_val = sum(val / (1+(wacc/100))**(i+1) for i, val in enumerate(df['Net Cash Flow']))

    st.subheader("Total Investment Summary (TCO)")
    if investment_strategy == "Pre-existing Solution Upgrade":
        i1, i2, i3, i4, i5, i6 = st.columns(6)
        i1.metric("1st Yr Uplift", f"${y1_recurring:,.0f}")
        i2.metric("Annual Sub", f"${steady_state_recurring:,.0f}")
        i3.metric("Total Sub", f"${total_sub_cost:,.0f}")
        i4.metric("TOTAL TCO", f"${total_tco:,.0f}")
        i5.metric("Break-Even", f"{final_be:.1f} Yrs" if final_be > 0 else "N/A")
        i6.metric("NPV", f"${npv_val:,.0f}")
    else:
        i1, i2, i3, i4, i5 = st.columns(5)
        i1.metric("Annual Sub", f"${steady_state_recurring:,.0f}")
        i2.metric("Total Sub", f"${total_sub_cost:,.0f}")
        i3.metric("TOTAL TCO", f"${total_tco:,.0f}")
        i4.metric("Break-Even", f"{final_be:.1f} Yrs" if final_be > 0 else "N/A")
        i5.metric("NPV", f"${npv_val:,.0f}")
    st.divider()

    st.subheader("Efficiency & Value Realization")
    v1, v2, v3, v4 = st.columns(4)
    v1.metric("Pro-Rated Saving (Yr 1)", f"${savings[0]:,.0f}")
    v2.metric("Steady State Saving (Yr 2+)", f"${savings[1] if analysis_years > 1 else 0:,.0f}")
    v3.metric("FTE Reclaimed", f"{fte_reclaimed} FTE")
    v4.metric("Hours Reclaimed (Ann / Mon)", f"{annual_hrs:,.0f} / {(annual_hrs/12):,.0f}")
    st.divider()

    st.subheader("🏛️ Strategic Analysis: Board-Level Overview")
    npv_status = "POSITIVE" if npv_val > 0 else "NEGATIVE"
    recommendation = "STRATEGICALLY VIABLE" if npv_val > 0 else "REQUIRES OPTIMIZATION"

    if industry == "Logistics Service Provider (LSP)":
        solution_context = "increased throughput capacity and asset utilization in lean-margin environments."
    elif industry == "Manufacturing":
        solution_context = "enhanced production synchronization and reduced lead-time volatility."
    else:
        solution_context = "improved operational resilience and decision velocity."

    if npv_val < 0:
        financial_viability = f'<div style="color:#D32F2F; margin-bottom:20px;"><b>⚠️ Strategic Context: {npv_status} NPV</b><br>Project costs currently exceed the discounted value of labor savings. Tactical adjustments required to meet the {wacc:.1f}% hurdle rate based on productivity alone. This indicates that the current scope of automation must be either expanded to recover more latent waste or the subscription costs must be aligned with the anticipated yield of the transformation.</div>'
    else:
        financial_viability = f'<div style="color:#2E7D32; margin-bottom:20px;"><b>✅ Financial Viability: {npv_status} NPV</b><br>The investment yields a <b>{npv_status} NPV of ${npv_val:,.0f}</b>, confirming that the project is <b>{recommendation}</b>. This positive Net Present Value signifies that the productivity dividends, when discounted at a {wacc:.1f}% cost of capital, outperform the total investment cost. As a "Go" decision, this project serves as a foundational step; while this model captures labor efficiency, it creates the operational "headroom" necessary to unlock secondary hard savings in inventory reduction and margin performance.</div>'

    summary_html = (
        f'<div style="border:1px solid rgba(128,128,128,0.3); padding:30px; border-radius:10px; font-family:\'Segoe UI\',sans-serif; line-height:1.8;">'
        f'<div style="margin-bottom:20px;"><b style="text-transform:uppercase;">Strategic Project Overview</b><br>'
        f'This initiative targets a TCO of <b>${total_tco:,.0f}</b> over a <b>{analysis_years}-year horizon</b>. Beyond a simple software deployment, this represents a transition to a <b>Cognitive solution</b> powered by <b>Blue Yonder\'s {solution_name}</b>. By embedding AI and ML into daily workflows, the organization shifts from reactive manual planning to <b>autonomous "exception-only" management</b>, ensuring human capital is focused on high-impact strategic trade-offs.</div>'
        f'<div style="margin-bottom:20px;"><b style="text-transform:uppercase;">Capacity Realization (Shadow Capacity)</b><br>'
        f'The implementation reclaims <b>{annual_hrs:,.0f} productive hours annually</b>: the financial and operational equivalent of adding <b>{fte_reclaimed} staff members</b> without escalating recruitment or payroll liabilities. This "Shadow Capacity" acts as a <b>Volume Multiplier</b> for the {industry} team, directly enabling {solution_context}</div>'
        f'<hr style="border:0; border-top:1px solid rgba(128,128,128,0.3); margin:25px 0;">{financial_viability}</div>'
    )
    st.markdown(summary_html, unsafe_allow_html=True)

    with st.expander("📝 Professional Glossary & Blue Yonder Strategic Alignment"):
        st.write("**Net Present Value (NPV) Analysis:** NPV calculates the total excess value generated by an investment after accounting for the time value of money.")
        st.info(f"""
        **Blue Yonder Value Realization Framework**
        In alignment with **Blue Yonder's Cognitive Supply Chain** strategy, this model captures the foundational **Productivity Dividend**.
        * **Labor Productivity:** Typical realization of 15% to 30% efficiency gains through automated task prioritization.
        * **Operational Agility:** Creation of 'Shadow Capacity'—allowing teams to absorb 10-15% volume growth.
        * **Decision Velocity:** AI-assisted work directing reduces 'swivel-chair' activity, enabling planners to focus on high-impact strategic trade-offs.
        """)
    
    chart_view = st.radio("Chart View:", ["Cumulative Path", "Annual Flow"], horizontal=True, help="Toggle visualizations.")
    fig = go.Figure()
    if chart_view == "Cumulative Path":
        fig.add_trace(go.Scatter(x=df["Period"], y=df["Cumulative Cash Flow"], mode='lines+markers', line=dict(color='#1f77b4', width=4), fill='tozeroy'))
    else:
        fig.add_trace(go.Bar(x=df["Period"], y=df["Net Cash Flow"], marker_color='#1f77b4'))
    fig.add_hline(y=0, line_dash="dash", line_color="gray", opacity=0.3)
    st.plotly_chart(fig, use_container_width=True)
    st.dataframe(df.style.format({"Investment": "${:,.0f}", "Gross Savings": "${:,.0f}", "Net Cash Flow": "${:,.0f}", "Cumulative Cash Flow": "${:,.0f}"}), hide_index=True, use_container_width=True)