# 📦 Global Supply Chain & Procurement Cost Optimization Model

An end-to-end data science and prescriptive analytics framework designed to model Total Cost of Ownership (TCO), analyze delivery delay penalty risks, and perform mathematical linear programming optimization across global supply chain networks.

![Streamlit](https://img.shields.io/badge/Dashboard-Streamlit-FF4B4B?style=for-the-badge&logo=streamlit&logoColor=white)
![Python](https://img.shields.io/badge/Python-3.10+-3776AB?style=for-the-badge&logo=python&logoColor=white)
![PuLP](https://img.shields.io/badge/Optimization-PuLP%20(LP)-00599C?style=for-the-badge)
![Plotly](https://img.shields.io/badge/Data%20Viz-Plotly-3F4F75?style=for-the-badge&logo=plotly&logoColor=white)

---

## 📌 Executive Summary

Global supply chain networks frequently face significant profit margin leakages driven by late delivery penalties, sub-optimal carrier allocations, and unmitigated Service Level Agreement (SLA) breaches. 

This project delivers a **two-tiered analytical pipeline**:
1. **Descriptive & Diagnostic Analytics:** Quantifies lead-time variances, maps high-risk product categories, and calculates cumulative financial penalty losses across 180,000+ order transactions.
2. **Prescriptive Optimization (Linear Programming):** Formulates a constrained LP mathematical model in **PuLP** to dynamically allocate order volumes across fulfillment channels—minimizing total shipping expenditure while enforcing a strict **<5% overall late-delivery threshold**.

---

## 🎯 Key Business Impact & Insights

* **Financial Leakage Identified:** Quantified over **$1M+ in cumulative late delivery penalties** across historical order flows.
* **Category Vulnerability:** Mapped category-wise risk profiles, revealing that the top 10 categories account for over **65% of delay penalty spend**.
* **Prescriptive Spend Reduction:** The LP optimization model projects a **~$400K+ recovery in operational expenditure** by re-allocating order volumes away from sub-optimal shipping channels under realistic capacity constraints

## 🛠️ System Architecture & Workflow

┌────────────────────────────────┐
│   Data Cleaning & Wrangling    │  ---> Pandas, NumPy, Feature Engineering
└──────────────┬─────────────────┘
               │
┌──────────────▼─────────────────┐
│ Total Cost of Ownership (TCO)  │  ---> Penalty Calculations & Lead-Time Variance
└──────────────┬─────────────────┘
               │
┌──────────────▼─────────────────┐
│  Linear Programming (PuLP)     │  ---> Mathematical Cost Minimization under SLAs
└──────────────┬─────────────────┘
               │
┌──────────────▼─────────────────┐
│   Interactive Streamlit UI     │  ---> Executive Dashboard with Plotly Visuals
└────────────────────────────────┘
## 🧮 Linear Programming (LP) Mathematical Formulation

The prescriptive optimization model minimizes total logistics shipping expenditure across fulfillment modes while strictly adhering to Service Level Agreement (SLA) delivery limits and carrier capacity caps.

### **Objective Function**
Minimize the total cost of shipping across all allocated volumes:

$$\min Z = \sum_{m \in M} c_m \cdot x_m$$

---

### **Decision Variables**
* $x_m \ge 0$: Volume (number of units) allocated to shipping mode $m \in M$.
* $M = \{\text{Standard Class}, \text{Second Class}, \text{First Class}, \text{Same Day}\}$

---

### **Model Parameters**
* $c_m$: Cost per unit shipped via mode $m$
  * $c_{\text{Standard}} = \$10$
  * $c_{\text{Second}} = \$18$
  * $c_{\text{First}} = \$28$
  * $c_{\text{Same Day}} = \$45$
* $r_m$: Historical late-delivery risk probability for mode $m$
* $D$: Target order demand ($D = 10,000 \text{ units}$)
* $\alpha$: Maximum acceptable overall late-delivery threshold ($\alpha = 0.05$ or $5\%$)

---

### **Constraints**

1. **Total Demand Satisfaction:**  
   The sum of all order volumes across all modes must equal total demand exactly:
   $$\sum_{m \in M} x_m = D$$

2. **Maximum Late Delivery Risk SLA Constraint:**  
   The expected number of late shipments across all modes cannot exceed 5% of total demand:
   $$\sum_{m \in M} (r_m \cdot x_m) \le \alpha \cdot D$$

3. **Operational Capacity Caps:**  
   To reflect real-world logistics bottlenecks, volume allocated to specific modes is capped:
   $$x_{\text{Standard Class}} \le 0.40 \cdot D \quad (4,000 \text{ units max})$$
   $$x_{\text{Second Class}} \le 0.40 \cdot D \quad (4,000 \text{ units max})$$
   $$x_{\text{First Class}} \le 0.30 \cdot D \quad (3,000 \text{ units max})$$

4. **Non-Negativity Constraint:**  
   Allocated shipping volume cannot be negative:
   $$x_m \ge 0 \quad \forall m \in M$$
