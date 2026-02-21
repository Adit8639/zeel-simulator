import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px

# --- 1. PAGE CONFIG & HIGH-END UI ---
st.set_page_config(page_title="ZEEL Content EV Simulator", layout="wide", initial_sidebar_state="expanded")

st.markdown("""
    <style>
        .stApp { background-color: #F8F9FA; }
        h1, h2, h3, h4 { color: #1E3A8A !important; font-family: 'Inter', sans-serif; font-weight: 800; }
        .metric-card { background-color: #FFFFFF; padding: 20px; border-radius: 8px; box-shadow: 0 4px 6px rgba(0,0,0,0.05); border-left: 5px solid #1E3A8A; }
        .metric-label { font-size: 1rem; color: #64748B; font-weight: 600; text-transform: uppercase; }
        .metric-value { font-size: 2.2rem; color: #0F172A; font-weight: 800; margin-top: 5px; }
        .metric-delta.positive { color: #16A34A; font-weight: 700; font-size: 1.1rem;}
        .metric-delta.negative { color: #DC2626; font-weight: 700; font-size: 1.1rem;}
    </style>
""", unsafe_allow_html=True)

st.markdown("<h1>📊 ZEEL Capital Allocation & EV Simulator</h1>", unsafe_allow_html=True)
st.markdown("### *Algorithmic stress-testing of Micro-Pilots & 70/30 TRP-Linked Producer Contracts*")
st.markdown("---")

# --- 2. ADVANCED INPUTS (SIDEBAR) ---
st.sidebar.header("⚙️ Financial Parameters")
st.sidebar.markdown("Define the unit economics for a standard 10-show portfolio.")

c_tv = st.sidebar.slider("Legacy TV Production Cost (₹ Cr / Show)", 20, 100, 50, 5)
c_pilot = st.sidebar.slider("Digital Micro-Pilot Cost (₹ Cr / Show)", 1.0, 5.0, 2.0, 0.5)

st.sidebar.markdown("---")
st.sidebar.header("📉 Probabilistic Risk Profile")
flop_rate = st.sidebar.slider("Estimated Flop Rate (%)", 30, 80, 60, 5) / 100.0
hit_rate = st.sidebar.slider("Estimated Blockbuster Rate (%)", 5, 30, 10, 5) / 100.0
avg_rate = 1.0 - flop_rate - hit_rate

if avg_rate < 0:
    st.sidebar.error("Flop + Hit rate cannot exceed 100%. Adjust sliders.")
    st.stop()

# --- 3. THE CORE ALGORITHM (FINANCIAL LOGIC) ---
N = 10 # Standard portfolio size of 10 shows for easy visualization

# Revenue Assumptions (Multiples of TV Cost)
rev_flop = c_tv * 0.2  # Flops recover only 20% of cost via ads
rev_avg = c_tv * 1.1   # Average shows yield 10% ROI
rev_hit = c_tv * 2.0   # Hits yield 100% ROI

# A. LEGACY MODEL (Direct to TV, 100% Fixed Cost)
leg_cost = N * c_tv
leg_rev = N * ((flop_rate * rev_flop) + (avg_rate * rev_avg) + (hit_rate * rev_hit))
leg_roi = leg_rev - leg_cost

# B. PROPOSED MODEL (Micro-Pilot Gate + 70/30 TRP Contracts)
# 1. Pilot Phase: Test all 10 shows
pilot_spend = N * c_pilot

# 2. Gatekeeper: Flops are identified and vaulted. 
# Savings: We DO NOT spend (c_tv) on them.
flops_killed = N * flop_rate

# 3. Production Phase: Survivors (Avg + Hits) proceed to TV under 70/30 contracts.
# 70% is guaranteed. The 30% variable is paid based on TRP.
# If Avg: They get 70% + 15% (partial bonus) = 85% of standard cost.
# If Hit: They get 70% + 50% (massive upside bonus) = 120% of standard cost.
cost_avg_show = c_pilot + (c_tv * 0.85)
cost_hit_show = c_pilot + (c_tv * 1.20)

prop_cost_avg = (N * avg_rate) * cost_avg_show
prop_cost_hits = (N * hit_rate) * cost_hit_show
prop_total_cost = pilot_spend + prop_cost_avg + prop_cost_hits

# Under Proposed, Flop Revenue is 0 (IP Vaulted), but we save the massive production cost.
prop_rev = (N * avg_rate * rev_avg) + (N * hit_rate * rev_hit)
prop_roi = prop_rev - prop_total_cost

# --- 4. TOP-LINE METRIC CARDS ---
col1, col2, col3 = st.columns(3)

with col1:
    st.markdown(f"""
        <div class="metric-card">
            <div class="metric-label">Legacy Portfolio Net ROI</div>
            <div class="metric-value">₹ {leg_roi:,.1f} Cr</div>
            <div class="metric-delta {'negative' if leg_roi < 0 else 'positive'}">High capital burn on flops</div>
        </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown(f"""
        <div class="metric-card" style="border-left-color: #10B981;">
            <div class="metric-label">Proposed Portfolio Net ROI</div>
            <div class="metric-value">₹ {prop_roi:,.1f} Cr</div>
            <div class="metric-delta positive">Flops vaulted early + optimized contracts</div>
        </div>
    """, unsafe_allow_html=True)

with col3:
    cash_freed = prop_roi - leg_roi
    st.markdown(f"""
        <div class="metric-card" style="border-left-color: #8B5CF6;">
            <div class="metric-label">Free Cash Flow Generated</div>
            <div class="metric-value">₹ {cash_freed:,.1f} Cr</div>
            <div class="metric-delta positive">+ Added directly to EBITDA</div>
        </div>
    """, unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# --- 5. DATA VISUALIZATION (WATERFALL & BAR CHARTS) ---
tab1, tab2 = st.tabs(["📉 The EBITDA Waterfall (Value Bridge)", "📊 Capital Deployment Breakdown"])

with tab1:
    st.markdown("#### How the Strategy Generates Value (Bridge from Legacy to Proposed)")
    
    # Calculate Waterfall steps
    savings_on_flops = (N * flop_rate) * c_tv  # Money NOT spent on producing flops
    cost_of_piloting = -1 * (N * c_pilot)      # Money spent on pilots
    contract_variance = (leg_cost - ((N * flop_rate * c_tv) + prop_cost_avg + prop_cost_hits + cost_of_piloting)) * -1
    lost_salvage_rev = -1 * (N * flop_rate * rev_flop) # Revenue lost because flops weren't aired

    fig_waterfall = go.Figure(go.Waterfall(
        name="Value Bridge",
        orientation="v",
        measure=["absolute", "relative", "relative", "relative", "relative", "total"],
        x=["Legacy ROI", "Saved TV Prod (Flops)", "Micro-Pilot Costs", "Lost Salvage Rev", "70/30 Contract Impact", "Proposed ROI"],
        textposition="outside",
        text=[f"₹{leg_roi}C", f"+₹{savings_on_flops}C", f"₹{cost_of_piloting}C", f"₹{lost_salvage_rev}C", f"₹{contract_variance}C", f"₹{prop_roi}C"],
        y=[leg_roi, savings_on_flops, cost_of_piloting, lost_salvage_rev, contract_variance, prop_roi],
        decreasing={"marker":{"color":"#EF4444"}},
        increasing={"marker":{"color":"#10B981"}},
        totals={"marker":{"color":"#1E3A8A"}}
    ))
    fig_waterfall.update_layout(plot_bgcolor="white", paper_bgcolor="white", height=500, margin=dict(t=30, b=40))
    fig_waterfall.update_yaxes(showgrid=True, gridcolor='lightgray')
    st.plotly_chart(fig_waterfall, use_container_width=True)

with tab2:
    st.markdown("#### Capital Deployment: Where is the money going?")
    
    leg_waste = (N * flop_rate) * c_tv
    leg_productive = leg_cost - leg_waste
    
    prop_waste = (N * flop_rate) * c_pilot
    prop_productive = prop_total_cost - prop_waste
    
    df_bar = pd.DataFrame({
        "Model": ["Legacy Model", "Proposed Model"],
        "Wasted Capital (Burned on Flops)": [leg_waste, prop_waste],
        "Productive Capital (Invested in Hits/Avg)": [leg_productive, prop_productive]
    })
    
    fig_bar = px.bar(df_bar, x="Model", y=["Wasted Capital (Burned on Flops)", "Productive Capital (Invested in Hits/Avg)"],
                     color_discrete_sequence=["#EF4444", "#10B981"], barmode="stack", height=500)
    fig_bar.update_layout(plot_bgcolor="white", paper_bgcolor="white", legend_title_text="Capital Type")
    fig_bar.update_yaxes(title_text="Total Capital Deployed (₹ Cr)", showgrid=True, gridcolor='lightgray')
    st.plotly_chart(fig_bar, use_container_width=True)