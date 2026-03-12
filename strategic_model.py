import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import numpy as np
import math
import re

# --- App Configuration ---
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
        
        # INDUSTRY BENCHMARK LOGIC
        benchmarks = {
            "Retail": {"leakage": 20.0, "hours": 8.0, "context": "Promo friction & stock-outs"},
            "Logistics Service Providers (LSP)": {"leakage": 25.0, "hours": 10.0, "context": "Manual dispatching & carrier churn"},
            "Manufacturing": {"leakage": 18.0, "hours": 7.2, "context": "Schedule jitter & material lag"}
        }
        
        st.info(f"**Industry Context:** {benchmarks[industry]['context']}. Typical productive leakage is {benchmarks[industry]['leakage']}% ({benchmarks[industry]['hours']} hrs/wk).")

        num_employees = st.number_input("Total Headcount in Scope", min_value=1, value=1, help="Number of users of the solution.")
        annual_salary = currency_input("Avg. Annual Salary ($)", 0, "Average base salary.", "salary_state")
        fringe_rate = st.slider("Employee Burden Rate (%)", 0, 50, 20, help="Local statutory costs (Super, Tax, etc.).")
        burdened_cost_pp = annual_salary * (1 + fringe_rate/100)
    
    with col2:
        work_days = st.number_input("Productive Working Days / Year", value=220, help="Standardized annual working days.")
        daily_hours = st.number_input("Productive Hours / Day", value=8.00, help="Actual time spent on core tasks.")
        total_annual_hours_pp = work_days * daily_hours
        hourly_rate_pp = burdened_cost_pp / total_annual_hours_pp
        
        st.divider()
        input_method = st.radio("Inefficiency Target:", ["Hours per Week", "Percentage of Week"], horizontal=True, help="Enter the hours per week per user of inefficiency to be reduced or eliminated.")
        
        if st.button(f"✨ Apply {industry} Benchmark"):
            st.session_state['manual_target_hrs'] = benchmarks[industry]['hours']
            st.session_state['manual_target_pct'] = benchmarks[industry]['leakage']
        
        weekly_productive_hours = daily_hours * 5
        if input_method == "Hours per Week":
            default_hrs = st.session_state.get('manual_target_hrs', 0.0)
            baseline_waste_hrs_pw = st.number_input("Productive Inefficiency (Hrs/Wk/Person)", value=default_hrs)
            baseline_waste_pct = baseline_waste_hrs_pw / weekly_productive_hours
        else:
            default_pct = st.session_state.get('manual_target_pct', 10)
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
            curr_sub = currency_input("Current Annual Subscription ($)", 0, "Current legacy spend.", "curr_sub_state")
            future_sub = currency_input("Future Annual Subscription ($)", 0, "Total new Cognitive spend.", "future_sub_state")
            y1_recurring = future_sub - curr_sub
            steady_state_recurring = future_sub
        else:
            y1_recurring = currency_input("Annual Subscription ($)", 0, "Recurring subscription cost.", "saas_state")
            steady_state_recurring = y1_recurring
        
        st.divider()
        initial_setup = currency_input("Implementation Services Fees", 0, "Professional services costs.", "services_state")
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
        impl_duration = st.number_input(f"Duration ({impl_unit})", key="dur_key", step=0.1)
        impl_factor = (52 - impl_duration)/52 if impl_unit == "Weeks" else (12 - impl_duration)/12
        
        st.subheader("Client Internal Team")
        key_users = st.number_input("Number of Key Users Dedicated to the Project", value=5)
        impl_intensity = st.select_slider("Intensity", options=["Low", "Medium", "High"], value="Medium")
        intensity_map = {"Low": 250, "Medium": 500, "High": 750}
        client_internal_investment = (key_users * intensity_map[impl_intensity] * hourly_rate_pp)
        st.info(f"Estimated Client Investment (Shadow Cost): ${client_internal_investment:,.0f}")
        
        # ADDED HELP TOOLTIP FOR WACC
        wacc = st.slider(
            "Discount Rate / Weighted Average Cost of Capital (WACC) %", 
            5, 15, 10, 
            help="Weighted Average Cost of Capital: The hurdle rate used to discount future cash flows. Represents the minimum return an organization expects to offset the cost of funding and risk."
        )

    y1_investment_total = initial_setup + client_internal_investment + y1_recurring

# =================================================================
# TAB 3: ROI REPORT
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
    target_mode = st.toggle("Enable Breakeven Period Target")
    final_calc_pct = baseline_waste_pct
    
    if target_mode:
        target_yrs = st.number_input("Target Years to Breakeven", min_value=1.1, value=float(round(current_be, 2)) if current_be > 0 else 3.7, step=0.1)
        cumulative_investment = y1_investment_total + (steady_state_recurring * (target_yrs - 1))
        weight_sum = 0
        for yr in range(1, int(math.ceil(target_yrs)) + 1):
            yr_rate = (burdened_cost_pp * ((1 + escalation_rate/100) ** (yr - 1))) / total_annual_hours_pp
            yr_weight = total_annual_hours_pp * num_employees * (improvement_target/100) * yr_rate
            if yr == 1: weight_sum += yr_weight * impl_factor
            elif yr < target_yrs: weight_sum += yr_weight
            else: weight_sum += yr_weight * (target_yrs - (yr - 1))
        
        final_calc_pct = cumulative_investment / weight_sum if weight_sum > 0 else 0
        target_hrs_pw_person = final_calc_pct * (daily_hours * 5)
        st.markdown(f'<div style="background-color:rgba(30,144,255,0.1); border-left:5px solid #1E90FF; padding:20px; border-radius:5px; margin-bottom:25px;"><span style="font-size:22px; font-weight:bold; color:#1E90FF;">Target identified: Address {target_hrs_pw_person:.2f} productive hours / week per person.</span></div>', unsafe_allow_html=True)

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
        i1, i2, i3, i4, i5, i6, i7, i8 = st.columns(8)
        i1.metric("1st Yr Uplift", f"${y1_recurring:,.0f}")
        i2.metric("Annual Subscription", f"${steady_state_recurring:,.0f}")
        i3.metric("Total Subscription", f"${total_sub_cost:,.0f}")
        i4.metric("Implementation Services", f"${initial_setup:,.0f}")
        i5.metric("Client Investment", f"${client_internal_investment:,.0f}")
        i6.metric("TOTAL TCO", f"${total_tco:,.0f}")
        i7.metric("Break Even", f"{final_be:.1f} Yrs")
        i8.metric("Net Present Value (NPV)", f"${npv_val:,.0f}")
    else:
        i1, i2, i3, i4, i5, i6, i7, i8 = st.columns(8)
        i1.metric("Year 1 Subscription", f"${y1_recurring:,.0f}")
        i2.metric("Annual Subscription", f"${steady_state_recurring:,.0f}")
        i3.metric("Total Subscription", f"${total_sub_cost:,.0f}")
        i4.metric("Implementation Services", f"${initial_setup:,.0f}")
        i5.metric("Client Investment", f"${client_internal_investment:,.0f}")
        i6.metric("TOTAL TCO", f"${total_tco:,.0f}")
        i7.metric("Break Even", f"{final_be:.1f} Yrs")
        i8.metric("Net Present Value (NPV)", f"${npv_val:,.0f}")
    st.divider()

    st.subheader("Efficiency & Value Realization")
    v1, v2, v3, v4 = st.columns(4)
    v1.metric("Prorated Savings (Yr 1)", f"${savings[0]:,.0f}")
    v2.metric("Steady State Savings (Yr 2+)", f"${savings[1] if analysis_years > 1 else 0:,.0f}")
    v3.metric("FTE Equivalence", f"{fte_reclaimed} FTE")
    v4.metric("Hours Reclaimed (Annual / Monthly)", f"{annual_hrs:,.0f} / {(annual_hrs/12):,.0f}")
    st.divider()

    st.subheader("🏛️ Strategic Analysis: Board-Level Overview")
    npv_status = "POSITIVE" if npv_val > 0 else "NEGATIVE"
    recommendation = "STRATEGICALLY VIABLE" if npv_val > 0 else "REQUIRES OPTIMIZATION"

    if npv_val < 0:
        viability_text = f"This {npv_status} Net Present Value indicates that the current scope of automation must be either expanded to recover more latent waste or the subscription costs must be aligned with the anticipated yield of the transformation."
    else:
        viability_text = f"This {npv_status} Net Present Value signifies that the productivity dividends, when discounted at a {wacc:.1f}% cost of capital, outperform the total investment cost."

    industry_impact = {
        "Retail": "improved operational resilience and decision velocity in omni-channel environments.",
        "Logistics Service Providers (LSP)": "increased throughput capacity and asset utilization in lean-margin environments.",
        "Manufacturing": "enhanced production synchronization and reduced lead-time volatility."
    }

    financial_viability = f'<div style="color:{"#2E7D32" if npv_val > 0 else "#D32F2F"}; margin-bottom:20px;"><b>{"✅" if npv_val > 0 else "⚠️"} Financial Viability: {npv_status} NPV</b><br>The investment yields a <b>{npv_status} NPV of ${npv_val:,.0f}</b>, confirming that the project <b>{recommendation}</b>. {viability_text} As a "Go" decision, this project serves as a foundational step; while this model captures labor efficiency, it creates the operational "headroom" necessary to unlock secondary hard savings in inventory reduction and margin performance.</div>'

    summary_html = (
        f'<div style="border:1px solid rgba(128,128,128,0.3); padding:30px; border-radius:10px; font-family:\'Segoe UI\',sans-serif; line-height:1.8;">'
        f'<div style="margin-bottom:20px;"><b style="text-transform:uppercase;">Strategic Project Overview</b><br>'
        f'This initiative targets a TCO of <b>${total_tco:,.0f}</b> over a <b>{analysis_years}-year horizon</b>. Beyond a simple software deployment, this represents a transition to a <b>Cognitive solution</b> powered by <b>Blue Yonder\'s {solution_name}</b>. By embedding AI and ML into daily workflows, the organization shifts from reactive manual planning to <b>autonomous "exception-only" management</b>, ensuring human capital is focused on high-impact strategic trade-offs.</div>'
        f'<div style="margin-bottom:20px;"><b style="text-transform:uppercase;">Capacity Realization (Shadow Capacity)</b><br>'
        f'The implementation reclaims <b>{annual_hrs:,.0f} productive hours annually</b>: the financial and operational equivalent of adding <b>{fte_reclaimed} staff members</b> without escalating recruitment or payroll liabilities. This "Shadow Capacity" acts as a <b>Volume Multiplier</b>, directly enabling {industry_impact[industry]}</div>'
        f'<hr style="border:0; border-top:1px solid rgba(128,128,128,0.3); margin:25px 0;">{financial_viability}</div>'
    )
    st.markdown(summary_html, unsafe_allow_html=True)

    with st.expander("📝 Professional Glossary & Blue Yonder Strategic Alignment"):
        st.write("**Net Present Value (NPV) Analysis:** NPV calculates the total excess value generated by an investment after accounting for the time value of money and the cost of capital.")
        st.info("""
        **Blue Yonder Value Realization Framework**
        * **Labor Productivity:** Typical realization of 15% to 30% efficiency gains through automated task prioritization.
        * **Operational Agility:** Creation of 'Shadow Capacity'—allowing teams to absorb 10-15% volume growth.
        * **Decision Velocity:** AI-assisted work directing reduces 'swivel-chair' activity, enabling planners to focus on high-impact strategic trade-offs.
        """)
    
    chart_view = st.radio("Chart View:", ["Cumulative ROI", "Annual Net ROI"], horizontal=True)
    fig = go.Figure()
    if chart_view == "Cumulative ROI":
        fig.add_trace(go.Scatter(x=df["Period"], y=df["Cumulative Cash Flow"], mode='lines+markers', line=dict(color='#1f77b4', width=4), fill='tozeroy'))
    else:
        fig.add_trace(go.Bar(x=df["Period"], y=df["Net Cash Flow"], marker_color='#1f77b4'))
    fig.add_hline(y=0, line_dash="dash", line_color="gray", opacity=0.3)
    st.plotly_chart(fig, use_container_width=True)
    st.dataframe(df.style.format({"Investment": "${:,.0f}", "Gross Savings": "${:,.0f}", "Net Cash Flow": "${:,.0f}", "Cumulative Cash Flow": "${:,.0f}"}), hide_index=True, use_container_width=True)