import streamlit as st
import pandas as pd
import plotly.express as px
import pulp

# Page Configuration
st.set_page_config(page_title="Supply Chain Optimization", layout="wide")

st.title("📦 Supply Chain & Procurement Cost Optimization Dashboard")

# 1. Load Clean Dataset
@st.cache_data
def load_data():
    # Load the cleaned dataset created by your notebook
    df = pd.read_csv('cleaned_supply_chain_data.csv')
    df.columns = df.columns.str.strip()
    return df

try:
    df = load_data()
except Exception as e:
    st.error(f"Error loading 'cleaned_supply_chain_data.csv': {e}")
    st.stop()

# Identify Revenue Column
if 'Sales per customer' in df.columns:
    rev_col = 'Sales per customer'
elif 'Sales' in df.columns:
    rev_col = 'Sales'
else:
    rev_col = df.select_dtypes(include=['float64', 'int64']).columns[0]

# 2. Executive KPI Cards
col1, col2, col3, col4 = st.columns(4)

total_revenue = df[rev_col].sum()
late_rate = df['Late_delivery_risk'].mean() * 100 if 'Late_delivery_risk' in df.columns else 0
total_penalties = df['Late_Penalty_Cost'].sum() if 'Late_Penalty_Cost' in df.columns else 0
estimated_savings = total_penalties * 0.40

col1.metric("Total Revenue ($)", f"${total_revenue:,.0f}")
col2.metric("Late Delivery Rate", f"{late_rate:.1f}%")
col3.metric("Delay Loss Penalties", f"${total_penalties:,.0f}")
col4.metric("Est. Cost Savings", f"${estimated_savings:,.0f}")

st.markdown("---")

# 3. Category Risk Visualizations
st.subheader("📊 Category Risk & Loss Breakdown")

if 'Category Name' in df.columns and 'Late_Penalty_Cost' in df.columns:
    category_df = df.groupby('Category Name').agg(
        Total_Sales=(rev_col, 'sum'),
        Total_Penalty=('Late_Penalty_Cost', 'sum')
    ).reset_index()

    fig = px.bar(
        category_df.sort_values(by='Total_Penalty', ascending=False).head(10),
        x='Total_Penalty',
        y='Category Name',
        orientation='h',
        title="Top 10 Categories by Delay Penalty Loss ($)",
        color='Total_Penalty',
        color_continuous_scale='Reds'
    )
    st.plotly_chart(fig)

st.markdown("---")


# -------------------------------------------------------------
# PRESCRIPTIVE LOGISTICS OPTIMIZATION (Linear Programming)
# -------------------------------------------------------------
st.subheader("🎯 Prescriptive Logistics Optimization (Linear Programming)")
st.write("Mathematical optimization model determining minimum shipping cost allocation for **exactly 10,000 units** under a strict late-delivery threshold.")

# 1. Define Modes & Base Parameters
modes = ['Standard Class', 'Second Class', 'First Class', 'Same Day']
cost_per_unit = {'Standard Class': 10, 'Second Class': 18, 'First Class': 28, 'Same Day': 45}

# Simplified/Reliable Delay Rates to guarantee feasibility
delay_rates = {
    'Standard Class': 0.12, 
    'Second Class': 0.06, 
    'First Class': 0.02, 
    'Same Day': 0.01
}

# 2. Fresh Model Instance
prob = pulp.LpProblem("Supply_Chain_10k_Optimization", pulp.LpMinimize)

# 3. Decision Variables (Strictly Non-Negative)
x = {m: pulp.LpVariable(f"Units_{m.replace(' ', '_')}", lowBound=0, cat='Continuous') for m in modes}

# 4. Objective Function: Minimize Cost
prob += pulp.lpSum([cost_per_unit[m] * x[m] for m in modes])

# 5. STRICT CONSTRAINTS
target_demand = 10000

# Constraint 1: STRICT TOTAL DEMAND = 10,000
prob += (pulp.lpSum([x[m] for m in modes]) == target_demand), "Exact_10k_Demand"

# Constraint 2: Max 5% Overall Delay (<= 500 delayed orders out of 10,000)
prob += (pulp.lpSum([delay_rates[m] * x[m] for m in modes]) <= 500), "Max_5_Percent_Delay"

# Constraint 3: Capacity Caps (prevents putting everything in one mode)
prob += x['Standard Class'] <= 4000  # Max 40% Standard
prob += x['Second Class'] <= 4000    # Max 40% Second
prob += x['First Class'] <= 3000     # Max 30% First

# 6. Solve
prob.solve(pulp.PULP_CBC_CMD(msg=False))

# 7. Render Streamlit Outputs (ONLY ONCE)
col_lp1, col_lp2 = st.columns([1, 2])

with col_lp1:
    st.markdown("### **Optimal Allocation**")
    total_calculated_units = 0
    
    for m in modes:
        val = max(0, x[m].varValue) if x[m].varValue is not None else 0
        total_calculated_units += val
        st.write(f"• **{m}:** `{val:,.0f} units`")
    
    st.info(f"**Total Volume:** `{total_calculated_units:,.0f} / 10,000 units`")
    
    opt_cost = pulp.value(prob.objective)
    if opt_cost:
        st.success(f"**Minimized Total Cost:** ${opt_cost:,.2f}")

with col_lp2:
    lp_df = pd.DataFrame({
        'Shipping Mode': modes,
        'Allocated Volume': [max(0, x[m].varValue) if x[m].varValue is not None else 0 for m in modes]
    })
    
    fig_lp = px.pie(
        lp_df, 
        names='Shipping Mode', 
        values='Allocated Volume', 
        title='Optimized 10,000 Order Volume Distribution',
        hole=0.4,
        color_discrete_sequence=px.colors.sequential.RdBu
    )
    st.plotly_chart(fig_lp)

st.markdown("---")

# 5. Raw Data Preview
st.subheader("📋 Raw Data Overview")
st.dataframe(df.head(50))