import streamlit as st

# --- App Configuration ---
st.set_page_config(page_title="Productivity ROI Calculator", layout="wide")

st.title("🚀 Productivity Improvement & ROI Calculator")

# --- Sidebar Inputs ---
st.sidebar.header("🌍 Regional Settings")
# 1. Currency Selection
currency_map = {"USD": "$", "AUD": "$", "EUR": "€", "GBP": "£", "INR": "₹", "JPY": "¥"}
currency_choice = st.sidebar.selectbox("Select Currency", list(currency_map.keys()), index=1) # Default to AUD
symbol = currency_map[currency_choice]

st.sidebar.header("👥 Scale & Scope")
num_employees = st.sidebar.number_input("Number of Employees", min_value=1, value=10, step=1)

st.sidebar.header("💰 Individual Cost")
annual_salary = st.sidebar.number_input(f"Avg. Annual Salary ({symbol})", value=120000, step=5000)
fringe_rate = st.sidebar.slider("Fringe Benefits (%)", 0, 50, 25) / 100

st.sidebar.header("⏱️ Time & Efficiency")
work_days = st.sidebar.number_input("Annual Work Days", value=220)
daily_hours = st.sidebar.number_input("Productive Hours/Day", value=7.5)
unproductive_pct = st.sidebar.slider("Current Inefficiency (%)", 0, 100, 20) / 100
improvement_pct = st.sidebar.slider("Waste Reduction Target (%)", 0, 100, 50) / 100

# --- Helper Function for Formatting ---
def format_currency(value):
    # 2. Figure formats with thousands separators and 2 decimal places
    return f"{symbol}{value:,.2f}"

# --- Calculations ---
if st.button("Generate Detailed Report"):
    # Math Logic
    indiv_burdened = annual_salary * (1 + fringe_rate)
    total_annual_hours = work_days * daily_hours
    hourly_rate = indiv_burdened / total_annual_hours
    
    total_dept_cost = indiv_burdened * num_employees
    hours_saved_dept = (total_annual_hours * unproductive_pct * improvement_pct) * num_employees
    
    total_savings = hours_saved_dept * hourly_rate
    total_fte_recovered = hours_saved_dept / total_annual_hours

    # --- Display Results ---
    st.divider()
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Total Dept. Burdened Cost", format_currency(total_dept_cost))
        st.caption(f"Based on {num_employees} Headcount")

    with col2:
        # Using format_currency for the delta/display
        st.metric("Total Annual Savings", format_currency(total_savings))
        st.write(f"Labor Rate: {format_currency(hourly_rate)}/hr")

    with col3:
        # FTE usually stays as a float, but we'll ensure 2 decimal precision
        st.metric("Capacity Reclaimed", f"{total_fte_