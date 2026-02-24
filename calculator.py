import streamlit as st

# --- App Configuration ---
st.set_page_config(page_title="Productivity ROI Calculator", layout="wide")

st.title("🚀 Departmental Productivity ROI Calculator")
st.markdown("Quantify the impact of process improvements across your team or department.")

# --- Sidebar Inputs ---
st.sidebar.header("1. Scale & Scope")
num_employees = st.sidebar.number_input("Number of Employees in Scope", min_value=1, value=10, step=1)

st.sidebar.header("2. Individual Cost Assumptions")
annual_salary = st.sidebar.number_input("Avg. Gross Annual Salary ($)", value=120000, step=5000)
fringe_rate = st.sidebar.slider("Fringe Benefits / Burden Rate (%)", 0, 50, 25) / 100

st.sidebar.header("3. Time & Efficiency")
work_days = st.sidebar.number_input("Annual Available Work Days", value=220)
daily_hours = st.sidebar.number_input("Productive Hours per Day", value=7.5)
unproductive_pct = st.sidebar.slider("Current Unproductive Time (%)", 0, 100, 20) / 100
improvement_pct = st.sidebar.slider("Target Waste Reduction (%)", 0, 100, 50) / 100

# --- Calculations ---
if st.button("Calculate Total Impact"):
    # Individual Math
    individual_burdened_cost = annual_salary * (1 + fringe_rate)
    total_annual_hours_per_person = work_days * daily_hours
    hourly_rate = individual_burdened_cost / total_annual_hours_per_person
    
    # Departmental Math
    total_dept_cost = individual_burdened_cost * num_employees
    hours_wasted_dept = (total_annual_hours_per_person * unproductive_pct) * num_employees
    hours_saved_dept = hours_wasted_dept * improvement_pct
    
    total_savings = hours_saved_dept * hourly_rate
    total_fte_recovered = hours_saved_dept / total_annual_hours_per_person

    # --- Display Results ---
    st.divider()
    
    # High-Level Metrics
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Total Dept. Burdened Cost", f"${total_dept_cost:,.0f}")
        st.caption(f"For {num_employees} employees")

    with col2:
        st.metric("Total Annual Savings", f"${total_savings:,.2f}", delta="ROI Positive")
        st.write(f"Based on ${hourly_rate:.2f}/hr blended rate")

    with col3:
        st.metric("Total Capacity Reclaimed", f"{total_fte_recovered:.2f} FTE")
        st.write(f"{hours_saved_dept:,.0f} total hours saved/year")

    # Visualizing the Capacity
    st.info(f"**Strategic Result:** By optimizing these tasks, you effectively 'hire' **{total_fte_recovered:.2f} additional staff members** without increasing your payroll budget by a single dollar.")

else:
    st.write("Adjust the parameters and click 'Calculate' to see the departmental impact.")