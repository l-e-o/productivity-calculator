import streamlit as st
import pandas as pd

# --- App Configuration ---
st.set_page_config(page_title="Productivity ROI Calculator", layout="wide")

st.title("🚀 Productivity Improvement & ROI Calculator")
st.markdown("Quantify the financial and capacity impact of process optimization.")

# --- Sidebar Inputs ---
st.sidebar.header("🌍 Regional Settings")
currency_map = {"AUD": "$", "USD": "$", "EUR": "€", "GBP": "£", "INR": "₹", "JPY": "¥"}
currency_choice = st.sidebar.selectbox("Select Currency", list(currency_map.keys()), index=0) 
symbol = currency_map[currency_choice]

st.sidebar.header("👥 Scale & Scope")
num_employees = st.sidebar.number_input("Number of Employees", min_value=1, value=10, step=1, format="%d")

st.sidebar.header("💰 Individual Cost")
annual_salary = st.sidebar.number_input(f"Avg. Annual Salary ({symbol})", min_value=0, value=120000, step=1000, format="%d")
st.sidebar.caption(f"Current selection: {symbol}{annual_salary:,.0f}")

fringe_rate = st.sidebar.slider("Fringe Benefits / Burden Rate (%)", 0, 50, 25) / 100

st.sidebar.header("⏱️ Time & Efficiency")
work_days = st.sidebar.number_input("Annual Available Work Days", value=220, format="%d")
daily_hours = st.sidebar.number_input("Productive Hours per Day", value=7.5)

st.sidebar.divider()
unproductive_pct = st.sidebar.slider("Current Unproductive Time (%)", 0, 100, 20) / 100
improvement_pct = st.sidebar.slider("Target Waste Reduction (%)", 0, 100, 50) / 100

# --- Helper Function for Formatting ---
def format_currency(value):
    return f"{symbol}{value:,.2f}"

# --- Calculations ---
burdened_cost_per_person = annual_salary * (1 + fringe_rate)
total_annual_hours_per_person = work_days * daily_hours
hourly_rate = burdened_cost_per_person / total_annual_hours_per_person

total_dept_hours = total_annual_hours_per_person * num_employees
total_dept_cost = burdened_cost_per_person * num_employees

# Break down the hours
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

    # --- Chart Visualization (Improved with Plotly) ---
    st.subheader("📊 Annual Hours Allocation")
    
    import plotly.graph_objects as go

    # Prepare data
    categories = ["Core Productive Time", "Reclaimed Time (Savings)", "Remaining Unproductive"]
    values = [hours_productive, hours_saved, hours_remaining_waste]
    colors = ['#2ca02c', '#1f77b4', '#d62728']  # Green, Blue, Red

    fig = go.Figure(go.Bar(
        x=values,
        y=categories,
        orientation='h',
        marker_color=colors,
        text=[f"{v:,.0f} hrs" for v in values],
        textposition='auto',
    ))

    fig.update_layout(
        xaxis_title="Total Annual Hours (Departmental)",
        yaxis=dict(autorange="reversed"), # Puts 'Core Productive' at the top
        margin=dict(l=20, r=20, t=20, b=20),
        height=300
    )

    st.plotly_chart(fig, use_container_width=True)
    

    # --- Summary Section ---
    st.subheader("📝 Executive Summary")
    summary = (
        f"By reducing unproductive time by {improvement_pct*100:.0f}%, "
        f"the department will reclaim {hours_saved:,.0f} hours annually. "
        f"This represents a financial gain of {format_currency(total_savings)} "
        f"and increases operational capacity by {total_fte_recovered:,.2f} FTE."
    )
    st.info(summary)
    st.text_area("Copy-paste into your proposal:", value=summary, height=120)

else:
    st.write("👈 Adjust the assumptions and click the button.")