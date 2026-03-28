import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import numpy as np
from datetime import datetime

# --- CONFIG ---
st.set_page_config(page_title="Energy Suite: Stress Test v2", layout="wide")

# --- SIMULATOR LOGIC (The "Crisis Engine") ---
def calculate_crisis_price(base, days, elasticity):
    # Model: Initial shock + log growth - diminishing IEA buffer
    iea_buffer = 0.05 if days > 30 else 0.02
    premium = (np.log1p(days) * elasticity) - (days * iea_buffer)
    return round(base * (1 + max(0, premium / 100)), 2)

# --- SIDEBAR: STRESS TEST SIMULATOR ---
st.sidebar.header("🛡️ Strategic Stress Test")
st.sidebar.markdown("Model the impact of a sustained Hormuz closure.")

days_closed = st.sidebar.slider("Days of Total Closure", 0, 180, 14)
aggression = st.sidebar.select_slider("Market Panic Level", options=["Low", "Standard", "Contagion"])

panic_multiplier = {"Low": 0.8, "Standard": 1.2, "Contagion": 2.5}[aggression]

# --- DATA BASELINES (March 2026) ---
commodities = {
    "Brent Crude": {"base": 112.57, "elasticity": 15},
    "Murban Crude": {"base": 105.32, "elasticity": 18},
    "LNG (TTF)": {"base": 97.73, "elasticity": 35},
    "Sulphur": {"base": 1543.33, "elasticity": 22},
    "Urea": {"base": 687.50, "elasticity": 20},
    "Jet Fuel": {"base": 4.24, "elasticity": 12},
    "Naphtha": {"base": 848.70, "elasticity": 14},
    "Natural Gas": {"base": 3.03, "elasticity": 8}
}

# --- UI LAYOUT ---
st.title("🌐 Executive Energy Suite: War-Room Edition")
st.caption(f"Simulating Impact for {days_closed} Days of Closure | Risk Level: {aggression}")

tab1, tab2, tab3, tab4 = st.tabs(["📊 Live/Simulated Monitor", "🚢 Logistics & Volumes", "🗺️ Regional Impact", "📝 Daily Briefing"])

with tab1:
    st.subheader("Projected Commodity Prices")
    cols = st.columns(4)
    
    sim_results = []
    for i, (name, stats) in enumerate(commodities.items()):
        sim_price = calculate_crisis_price(stats['base'], days_closed, stats['elasticity'] * panic_multiplier)
        delta = round(((sim_price - stats['base']) / stats['base']) * 100, 1)
        
        with cols[i % 4]:
            st.metric(name, f"${sim_price}", f"+{delta}%" if delta > 0 else "0%", delta_color="inverse")
            sim_results.append({"Commodity": name, "Current": stats['base'], "Simulated": sim_price})

    # Visualization
    df_sim = pd.DataFrame(sim_results)
    fig = go.Figure()
    fig.add_trace(go.Bar(name='Current Price', x=df_sim['Commodity'], y=df_sim['Current'], marker_color='#1f77b4'))
    fig.add_trace(go.Bar(name='Simulated (Crisis)', x=df_sim['Commodity'], y=df_sim['Simulated'], marker_color='#d62728'))
    fig.update_layout(barmode='group', title=f"Price Escalation at {days_closed} Days Closure")
    st.plotly_chart(fig, use_container_width=True)

with tab2:
    st.subheader("Strategic Supply Chain Metrics")
    v1, v2, v3 = st.columns(3)
    # Volumes adjusted by simulation days
    oil_on_water = 1210 - (days_closed * 2.5) # Depleting storage
    v1.metric("Oil on Water", f"{round(oil_on_water, 1)}M Bbls", f"-{days_closed * 2.5}M", delta_color="inverse")
    v2.metric("Yanbu Bypass Cap", "4.4 MMbpd", "Max Capacity")
    v3.metric("Fujairah Bypass Cap", "1.9 MMbpd", "Security Alert")

with tab3:
    st.header("Regional Impact Assessment")
    if days_closed > 30:
        st.error("### 🚨 CRITICAL: Global Supply Exhaustion Imminent")
    
    c1, c2 = st.columns(2)
    with c1:
        st.markdown(f"**Asia (CN, JP, KR, IN):** At {days_closed} days, India's strategic reserves are at {(100 - (days_closed/0.9)):.1f}% capacity. Rationing expected.")
    with c2:
        st.markdown(f"**Europe:** TTF prices projected to hit **€{(97.73 * (1 + (days_closed*0.02))):.2f}**. Storage injection effectively halted.")

with tab4:
    st.markdown(f"### Daily Briefing: Day {days_closed} Analysis")
    st.write(f"""
    At the current {days_closed}-day mark, the global energy system is transitioning from a 'Shock' phase to a 'Structural Deficit'. 
    The IEA release of 2.5 MMbpd is currently covering only 15% of the total lost volume from the Persian Gulf.
    
    **Immediate Action:** We recommend hedging long-term Naphtha and Urea contracts immediately, as these are showing the highest sensitivity to the {aggression} panic multiplier.
    """)
