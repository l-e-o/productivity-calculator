import streamlit as st
import pandas as pd
import plotly.graph_objects as go

# --- App Configuration ---
st.set_page_config(page_title="Productivity ROI Calculator", layout="wide")

st.title("🚀 Productivity Improvement & ROI Calculator")

# --- Sidebar Inputs ---
st.sidebar.header("🌍 Regional Settings")
currency_map = {"AUD": "$", "USD": "$", "EUR": "€", "GBP": "£", "INR": "₹", "JPY": "¥"}
currency_choice = st.sidebar.selectbox("Select Currency", list(currency_map.keys()), index=0) 
symbol = currency_map[currency_choice]

st.sidebar.header("👥 Scale & Scope")
num_employees = st.sidebar.number_input("Number of Employees", min_value=1, value=10, step=1, format="%d")

st.sidebar.header("💰 Individual Cost")
annual_salary = st.sidebar.number_input(f"Avg. Annual Salary ({symbol})", min_value=0, value=120000, step=1000, format="%d")
st.sidebar.caption(f"Selected: {symbol}{annual_salary:,.0f}")
fringe_rate = st.sidebar.slider("Fringe Benefits / Burden Rate (%)", 0, 50, 25) / 100

st.sidebar.header("⏱️ Productivity Baseline")
work_days = st.sidebar.number_input("Annual Available Work Days", value=220, format="%d")
daily_hours = st.sidebar.number_input("Productive Hours per Day", value=7.5)
total_annual_hours_per_person = work_days * daily_hours

st.sidebar.divider()
st.sidebar.header("🎯 Inefficiency Target")

# --- NEW: Toggle between % and Hours ---
input_method = st.sidebar.radio(
    "How do you want to define waste?",
    ["As a Percentage (%)", "As Hours per Week"]
)

if input_method == "As a Percentage (%)":
    unproductive_pct = st.sidebar.slider("Current Unproductive Time (%)", 0, 100, 20) / 100
    # Calculate equivalent hours for the summary
    weekly_waste_hours = (unproductive_pct * total_annual_hours_per_person) / (work_days / 5)
else:
    weekly_waste_hours = st.sidebar.number_input("Unproductive Hours per Week (per person)", value=8.0, step=0.5)
    # Convert weekly hours back to a percentage of annual time
    # Assuming 52 weeks but adjusted for the 'work_days' ratio
    weeks_per_year = work_days / 5
    annual_waste_hours = weekly_waste_hours * weeks_per_year
    unproductive_pct = annual_waste_hours / total_annual_hours_per_person

improvement_pct = st.sidebar.slider("Target Waste Reduction (%)", 0, 100, 50) / 100

# --- Helper Function for Formatting ---
def format_currency(value):
    return f"{symbol}{value:,.2f}"

# --- Calculations ---
burdened_cost_per_person = annual_salary * (1 + fringe_rate)
hourly_rate = burdened_cost_per_person / total_annual_hours_per_person

total_dept_hours = total_annual_hours_per_person * num_employees
total_dept_cost = burdened_cost_per_person * num_employees

# Break down the hours for the chart
hours_wasted_total = total_dept_hours * unproductive_pct
hours_saved = hours_wasted_total * improvement_pct
hours_remaining_waste = hours_wasted_total - hours_saved
hours_productive = total_dept_hours - hours_wasted_total

total_savings = hours_saved * hourly_rate
total_fte_recovered = hours_saved / total_annual_hours_per_person

# --- Display Results ---
if st.button("Generate Productivity Report"):
    st.divider()
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Total Dept. Burdened Cost", format_currency(total_dept_cost))
    with col2:
        st.metric("Total Annual Savings", format_currency(total_savings), delta="ROI Impact")
    with col3:
        st.metric("Capacity Reclaimed", f"{total_fte_recovered:,.2f} FTE")

    # --- Chart Visualization ---
    st.subheader("📊 Annual Hours Allocation (Departmental)")
    
    categories = ["Core Productive Time", "Reclaimed Time (Savings)", "Remaining Waste"]
    values = [hours_productive, hours_saved, hours_remaining_waste]
    colors = ['#2ca02c', '#1f77b4', '#d62728']

    fig = go.Figure(go.Bar(
        x=values, y=categories, orientation='h', marker_color=colors,
        text=[f"{v:,.0f} hrs" for v in values], textposition='auto',
    ))

    fig.update_layout(
        xaxis_title="Total Annual Hours", yaxis=dict(autorange="reversed"),
        margin=dict(l=20, r=20, t=30, b=20), height=350, template="plotly_white"
    )

    st.plotly_chart(fig, use_container_width=True)

    # --- Executive Summary ---
    st.subheader("📝 Executive Summary")
    summary = (
        f"Based on a identified baseline of {weekly_waste_hours:.1f} hours of waste per week per person, "
        f"this optimization project targets a {improvement_pct*100:.0f}% reduction. "
        f"The department will reclaim {hours_saved:,.0f} hours annually, "
        f"representing a financial gain of {format_currency(total_savings)} "
        f"and an increased operational capacity of {total_fte_recovered:,.2f} FTE."
    )
    st.info(summary)
    st.text_area("Copy-paste into your proposal:", value=summary, height=120)

else:
    st.write("👈 Adjust the assumptions in the sidebar and click the button.")