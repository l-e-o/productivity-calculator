import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
import numpy as np
import math
import re

# --- App Configuration (Baseline v4 Restored) ---
st.set_page_config(page_title="Productivity Business Case Calculator", layout="wide")

st.title("🏛️ Productivity Value Realization")
st.markdown("Quantifying the multi-year value of improving operational efficiency.")

# --- Helper function for live comma formatting ---
def currency_input(label, default_value, help_text, key):
    if key not in st.session_state:
        st.session_state[key] = f"{int(default_value):,}"
    
    def format_on_change():
        raw_val = re.sub(r'[^\d]', '', st.session_state[key])
        if raw_val:
            st.session_state[key] = f"{int(raw_val):,}"
        else:
            st.session_state[key] = "0"

    st.text_input(label, help=help_text, key=key, on_change=format_on_change)
    clean_numeric = re.sub(r'[^\d]', '', st.session_state[key])
    return float(clean_numeric) if clean_numeric else 0.0

# --- Tabs ---
tab1, tab2, tab3 = st.tabs(["📊 Baseline & Industry", "💰 Investment & Horizon", "📈 ROI Report"])

# =================================================================
# TAB 1: OPERATIONAL STRATEGY
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
            ["Retail", "Logistics Service Providers (LSP)", "Manufacturing"], 
            help="Contextualizes the business environment and selects relevant productivity benchmarks."
        )
        
        benchmarks = {
            "Retail": {"leakage": 20.0, "hours": 8.0, "context": "Promo friction & stock-outs"},
            "Logistics Service Providers (LSP)": {"leakage": 25.0, "hours": 10.0, "context": "Manual dispatching & carrier churn"},
            "Manufacturing": {"leakage": 18.0, "hours": 7.2, "context": "Schedule jitter & material lag"}
        }
        
        st.info(f"**Industry Context:** {benchmarks[industry]['context']}. Typical productive leakage is {benchmarks[industry]['leakage']}% ({benchmarks[industry]['hours']} hrs/wk).")

        num_employees = st.number_input("Total Headcount in Scope", min_value=1, value=1, help="Number of users of the solution.")
        annual_salary = currency_input("Avg. Annual Salary ($)", 100000, "Average base salary.", "salary_state")
        fringe_rate = st.slider("Employee Burden Rate (%)", 0, 50, 18, help="Local statutory costs (Super, Tax, etc.).")
        burdened_cost_pp = annual_salary * (1 + fringe_rate/100)
    
    with col2:
        work_days = st.number_input("Productive Working Days / Year", value=220, help="Standardized annual working days.")
        daily_hours = st.number_input("Productive Hours / Day", value=8.00, help="Actual time spent on core tasks.")
        total_annual_hours_pp = work_days * daily_hours
        hourly_rate_pp = burdened_cost_pp / max(total_annual_hours_pp, 1)
        
        st.divider()
        input_method = st.radio("Inefficiency Target:", ["Hours per Week", "Percentage of Week"], horizontal=True, help="Enter the hours per week per user of inefficiency to be reduced or eliminated.")
        
        if st.button(f"✨ Apply {industry} Benchmark"):
            st.session_state['manual_target_hrs'] = benchmarks[industry]['hours']
            st.session_state['manual_target_pct'] = benchmarks[industry]['leakage']
        
        weekly_productive_hours = daily_hours * 5
        if input_method == "Hours per Week":
            default_hrs = st.session_state.get('manual_target_hrs', 0.0)
            baseline_waste_hrs_pw = st.number_input("Productive Inefficiency (Hrs/Wk/Person)", value=default_hrs, min_value=0.0, max_value=float(weekly_productive_hours))
            baseline_waste_pct = baseline_waste_hrs_pw / max(weekly_productive_hours, 1)
        else:
            default_pct = st.session_state.get('manual_target_pct', 10.0)
            baseline_waste_pct_input = st.slider("Inefficiency Percentage (%)", 0, 100, int(default_pct))
            baseline_waste_pct = baseline_waste_pct_input / 100
        
        improvement_target = st.slider("Target Efficiency Gain (%)", 1, 100, 100)

# =================================================================
# TAB 2: INVESTMENT & HORIZON
# =================================================================
with tab2:
    st.header("2. Investment & Time Horizon")
    c1, c2 = st.columns(2)
    with c1:
        solution_name = st.text_input("Solution Name", value="Cognitive Merchandise Financial Planning (CMFP)", help="Specific solution or module name.")
        
        if investment_strategy == "Pre-existing Solution Upgrade":
            curr_sub = currency_input("Current Annual Subscription ($)", 717000, "Current legacy spend.", "curr_sub_state")
            future_sub = currency_input("Future Annual Subscription ($)", 1200000, "Total new Cognitive spend.", "future_sub_state")
            y1_recurring = future_sub - curr_sub
            
            incremental_tco = st.toggle("Incremental ROI Mode", value=True, help="If enabled, calculations use the subscription delta for all years.")
            if incremental_tco:
                steady_state_recurring = y1_recurring
            else:
                steady_state_recurring = future_sub
        else:
            y1_recurring = currency_input("Annual Subscription ($)", 0, "Recurring subscription cost.", "saas_state")
            steady_state_recurring = y1_recurring
            incremental_tco = False
        
        st.divider()
        initial_setup = currency_input("Implementation Services Fees", 500000, "Professional services costs.", "services_state")
        analysis_years = st.slider("ROI Horizon (Years)", 2, 10, 5)
        escalation_rate = st.slider("Annual Employee Salary Increases (%)", 0, 10, 3)

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

        impl_unit = st.radio("Implementation Duration Unit:", ["Weeks", "Months"], horizontal=True, key="unit_choice", on_change=convert_duration)
        max_dur = 52.0 if impl_unit == "Weeks" else 12.0
        impl_duration = st.number_input(f"Duration ({impl_unit})", key="dur_key", step=0.1, min_value=0.0, max_value=max_dur)
        impl_factor = (max_dur - impl_duration)/max_dur
        
        st.subheader("Client Internal Team")
        key_users = st.number_input("Number of Key Users Dedicated to the Project", value=4)
        
        # CHANGE: Replaced Intensity Slider with % Commitment Slider
        commitment_pct = st.slider("Team Commitment Level (%)", 0, 100, 50, help="What percentage of these users' time is dedicated to the project during the implementation period?")
        
        # FIXED: Prorated Client Internal Investment
        duration_weeks = impl_duration if impl_unit == "Weeks" else impl_duration * 4.33
        # Calculation: Users * Annual Burdened Cost * (% commitment) * (Proportion of year spent on project)
        client_internal_investment = (key_users * burdened_cost_pp * (commitment_pct / 100.0) * (duration_weeks / 52.0))
        
        st.info(f"Estimated Client Investment (Shadow Cost): ${client_internal_investment:,.0f}")
        
        wacc = st.slider("Discount Rate / WACC %", 5, 15, 10)

    y1_investment_total = initial_setup + client_internal_investment + y1_recurring

# =================================================================
# TAB 3: ROI REPORT
# =================================================================
with tab3:
    if annual_salary <= 0:
        st.warning("⚠️ Please provide an **Avg. Annual Salary** in Tab 1.")
        st.stop()

    st.header("📈 ROI Report & Targeter")
    
    def calc_npv_logic(eff_multiplier, current_wacc):
        test_pct = final_calc_pct * eff_multiplier
        c_savings = []
        for yr in range(1, analysis_years + 1):
            yr_rate = (burdened_cost_pp * ((1 + escalation_rate/100) ** (yr - 1))) / max(total_annual_hours_pp, 1)
            yr_sav = (total_annual_hours_pp * test_pct * num_employees) * (improvement_target/100) * yr_rate
            c_savings.append(yr_sav * impl_factor if yr == 1 else yr_sav)
        c_invest = [-y1_investment_total] + ([-steady_state_recurring] * (analysis_years - 1))
        return sum((c_savings[k] + c_invest[k]) / (1+(current_wacc/100))**(k+1) for k in range(analysis_years))

    def get_be_years(in_waste_pct):
        if in_waste_pct <= 0: return 0.0
        s, i = [], []
        for yr in range(1, analysis_years + 1):
            yr_rate = (burdened_cost_pp * ((1 + escalation_rate/100) ** (yr - 1))) / max(total_annual_hours_pp, 1)
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
                if idx == 0: return y1_investment_total / s[0] if s[0] > 0 else 0
                prev_cum = cum_cf[idx-1]
                net_now = (s[idx] + i[idx])
                return idx + (abs(prev_cum) / net_now) if net_now > 0 else idx
        return 0.0

    current_be = get_be_years(baseline_waste_pct)
    target_mode = st.toggle("Enable Breakeven Period Target")
    final_calc_pct = baseline_waste_pct
    
    if target_mode:
        target_yrs = st.number_input("Target Years to Breakeven", min_value=1.1, value=float(round(current_be, 2)) if current_be > 0 else 3.7, step=0.1)
        cumulative_investment = y1_investment_total + (steady_state_recurring * (target_yrs - 1))
        weight_sum = 0
        for yr in range(1, int(math.ceil(target_yrs)) + 1):
            yr_rate = (burdened_cost_pp * ((1 + escalation_rate/100) ** (yr - 1))) / max(total_annual_hours_pp, 1)
            yr_weight = total_annual_hours_pp * num_employees * (improvement_target/100) * yr_rate
            if yr == 1: weight_sum += yr_weight * impl_factor
            elif yr < target_yrs: weight_sum += yr_weight
            else: weight_sum += yr_weight * (target_yrs - (yr - 1))
        
        final_calc_pct = cumulative_investment / max(weight_sum, 1)
        target_hrs_pw_person = final_calc_pct * (daily_hours * 5)
        st.markdown(f'<div style="background-color:rgba(30,144,255,0.1); border-left:5px solid #1E90FF; padding:20px; border-radius:5px; margin-bottom:25px;"><span style="font-size:22px; font-weight:bold; color:#1E90FF;">Target identified: Address {target_hrs_pw_person:.2f} productive hours / week per person.</span></div>', unsafe_allow_html=True)

    savings, investments = [], []
    for yr in range(1, analysis_years + 1):
        yr_hourly_rate = (burdened_cost_pp * ((1 + escalation_rate/100) ** (yr - 1))) / max(total_annual_hours_pp, 1)
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
    fte_reclaimed = math.floor((annual_hrs / max(total_annual_hours_pp, 1)) * 10) / 10.0
    
    expected_npv = calc_npv_logic(1.0, wacc)
    downside_npv = calc_npv_logic(0.8, wacc)
    upside_npv = calc_npv_logic(1.2, wacc)
    risk_adj_npv = (expected_npv * 0.60) + (downside_npv * 0.25) + (upside_npv * 0.15)

    st.subheader("Total Investment Summary (TCO)")
    l1_c1, l1_c2, l1_c3, l1_c4, l1_c5 = st.columns(5)
    if investment_strategy == "Pre-existing Solution Upgrade":
        l1_c1.metric("1st Yr Uplift", f"${y1_recurring:,.0f}")
    else:
        l1_c1.metric("Year 1 Sub", f"${y1_recurring:,.0f}")
    l1_c2.metric("Annual Recurring", f"${steady_state_recurring:,.0f}")
    l1_c3.metric("Total Sub", f"${total_sub_cost:,.0f}")
    l1_c4.metric("Services", f"${initial_setup:,.0f}")
    l1_c5.metric("Client Inv (Prorated)", f"${client_internal_investment:,.0f}")
    
    l2_c1, l2_c2, l2_c3 = st.columns(3)
    l2_c1.metric("TOTAL TCO", f"${total_tco:,.0f}")
    l2_c2.metric("Break Even", f"{final_be:.1f} Yrs" if final_be > 0 else "Beyond")
    l2_c3.metric("Risk-Adj NPV", f"${risk_adj_npv:,.0f}")
    st.divider()

    st.subheader("Efficiency & Value Realization")
    v1, v2, v3, v4 = st.columns(4)
    v1.metric("Prorated Savings (Yr 1)", f"${savings[0]:,.0f}")
    v2.metric("Steady Savings (Yr 2+)", f"${savings[1] if analysis_years > 1 else 0:,.0f}")
    v3.metric("FTE Equivalence", f"{fte_reclaimed} FTE")
    v4.metric("Hours Reclaimed", f"{annual_hrs:,.0f} / Yr")
    st.divider()

    summary_html = (
        f'<div style="border:1px solid rgba(128,128,128,0.3); padding:30px; border-radius:10px;">'
        f'This initiative targets a TCO of <b>${total_tco:,.0f}</b> over <b>{analysis_years} years</b>. '
        f'The implementation reclaims <b>{annual_hrs:,.0f} hours annually</b>: the equivalent of <b>{fte_reclaimed} staff members</b>. '
        f'The investment yields a <b>Risk-Adjusted NPV of ${risk_adj_npv:,.0f}</b>.</div>'
    )
    st.markdown(summary_html, unsafe_allow_html=True)

    st.subheader("🎯 Sensitivity Analysis")
    with st.expander("📊 View NPV Matrix"):
        eff_variants, wacc_variants = [0.8, 0.9, 1.0, 1.1, 1.2], [wacc-4, wacc-2, wacc, wacc+2, wacc+4]
        matrix_data, text_data = [], []
        base_hrs_reclaimed = final_calc_pct * (daily_hours * 5)
        for e_var in eff_variants:
            row_vals, row_text = [], []
            for w_var in wacc_variants:
                val = calc_npv_logic(e_var, w_var)
                row_vals.append(val)
                display_text = f"{val/1_000_000:.1f}M" if abs(val) >= 1_000_000 else f"{val/1_000:.0f}k"
                row_text.append(f"🎯 <b>{display_text}</b>" if round(e_var, 1) == 1.0 and w_var == wacc else display_text)
            matrix_data.append(row_vals)
            text_data.append(row_text)

        fig_heat = px.imshow(matrix_data, x=[f"{w}%" for w in wacc_variants], y=[f"{int(ev*100)}%" for ev in eff_variants], color_continuous_scale="RdYlGn", aspect="auto")
        fig_heat.update_traces(text=text_data, texttemplate="%{text}", textfont=dict(size=14))
        st.plotly_chart(fig_heat, width='stretch')

    chart_view = st.radio("Chart View:", ["Cumulative ROI", "Annual Net ROI"], horizontal=True)
    fig = go.Figure()
    if chart_view == "Cumulative ROI":
        fig.add_trace(go.Scatter(x=df["Period"], y=df["Cumulative Cash Flow"], mode='markers+lines', fill='tozeroy'))
    else:
        fig.add_trace(go.Bar(x=df["Period"], y=df["Net Cash Flow"]))
    st.plotly_chart(fig, width='stretch')
    
    st.dataframe(df.style.format({
        "Investment": "${:,.0f}",
        "Gross Savings": "${:,.0f}",
        "Net Cash Flow": "${:,.0f}",
        "Cumulative Cash Flow": "${:,.0f}"
    }), hide_index=True, width='stretch')