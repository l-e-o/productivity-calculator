import streamlit as st

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
num_employees = st.sidebar.number_input(
    "Number of Employees", 
    min_value=1, 
    value=10, 
    step=1,
    format="%d"
)

st.sidebar.header("💰 Individual Cost")
# Note: format="%d" ensures the input is treated as an integer. 
# While Streamlit's input box itself might hide commas during typing, 
# we show the formatted version below for clarity.
annual_salary = st.sidebar.number_input(
    f"Avg. Annual Salary ({symbol})", 
    min_value=0, 
    value=120000, 
    step=1000,
    format="%d"
)
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
# These are calculated outside the button to allow for potential live-updating charts
burdened_cost_per_person = annual_salary * (1 + fringe_rate)
total_annual_hours_per_person = work_days * daily_hours
hourly_rate = burdened_cost_per_person / total_annual_hours_per_person

total_dept_cost = burdened_cost_per_person * num_employees
hours_wasted_dept = (total_annual_hours_per_person * unproductive_pct) * num_employees
hours_saved_dept = hours_wasted_dept * improvement_pct

total_savings = hours_saved_dept * hourly_rate
total_fte_recovered = hours_saved_dept / total_annual_hours_per_person

# --- Display Results ---
if st.button("Generate Productivity Report"):
    st.divider()
    
    # Key Metric Row
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Total Dept. Burdened Cost", format_currency(total_dept_cost))
        st.caption(f"Includes salary + {fringe_rate*100:.0f}% benefits")

    with col2:
        st.metric("Total Annual Savings", format_currency(total_savings), delta="ROI Impact")
        st.write(f"Blended Labor Rate: {format_currency(hourly_rate)}/hr")

    with col3:
        # Fixed the closing bracket here to prevent the SyntaxError
        st.metric("Capacity Reclaimed", f"{total_fte_recovered:,.2f} FTE")
        st.write(f"{hours_saved_dept:,.1f} Total Hours Saved/Year")

    # --- Summary Section ---
    st.subheader("📝 Executive Summary")
    summary = (
        f"By reducing unproductive time by {improvement_pct*100:.0f}%, "
        f"the department will reclaim {hours_saved_dept:,.0f} hours annually. "
        f"This represents a financial gain of {format_currency(total_savings)} "
        f"and increases operational capacity by {total_fte_recovered:,.2f} FTE."
    )
    st.info(summary)
    
    # Text area for copy-pasting into emails/proposals
    st.text_area("Copy-paste this into your project proposal:", value=summary, height=120)

else:
    st.write("👈 Adjust the assumptions in the sidebar and click the button to see the impact.")