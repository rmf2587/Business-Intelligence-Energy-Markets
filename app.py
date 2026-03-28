import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import numpy as np
from datetime import datetime, timedelta

# --- APP CONFIG & THEME ---
st.set_page_config(page_title="Energy Suite v3.0", layout="wide", initial_sidebar_state="expanded")

# Custom CSS for Dark Mode "Boxes" and styling
st.markdown("""
    <style>
    .metric-container {
        background-color: #1e1e1e;
        border: 1px solid #333;
        border-radius: 10px;
        padding: 20px;
        margin-bottom: 20px;
        text-align: center;
    }
    .main { background-color: #0e1117; }
    </style>
    """, unsafe_cache=True)

# --- MOCK DATA ENGINE (MARCH 2026) ---
# Data based on March 27-28, 2026 market closes
commodities = {
    "Brent Crude": {"price": 112.57, "delta": 4.22, "unit": "USD/Bbl", "elasticity": 15},
    "Murban Crude": {"price": 105.32, "delta": 3.37, "unit": "USD/Bbl", "elasticity": 18},
    "LNG (TTF)": {"price": 54.53, "delta": -1.82, "unit": "EUR/MWh", "elasticity": 35},
    "Sulphur": {"price": 1543.33, "delta": 1.20, "unit": "USD/MT", "elasticity": 22},
    "Urea": {"price": 687.50, "delta": 0.85, "unit": "USD/MT", "elasticity": 20},
    "Naphtha": {"price": 848.70, "delta": 0.74, "unit": "USD/MT", "elasticity": 14},
    "Natural Gas (HH)": {"price": 3.03, "delta": 3.31, "unit": "USD/MMBtu", "elasticity": 8},
    "Jet Fuel": {"price": 230.00, "delta": 140.0, "unit": "USD/Bbl", "elasticity": 40}
}

def generate_sparkline(base_price):
    # Simulated 30-day trend for UI visual
    return base_price + np.cumsum(np.random.randn(30) * (base_price * 0.02))

# --- APP TABS ---
tab1, tab2, tab3 = st.tabs(["📊 Live Market Monitor", "🛡️ Stress Test Simulator", "📰 Global Intelligence"])

# --- TAB 1: LIVE MARKET MONITOR ---
with tab1:
    st.subheader("Commodity Performance & 30D Trend")
    rows = [st.columns(4), st.columns(4)]
    
    for i, (name, data) in enumerate(commodities.items()):
        col = rows[i // 4][i % 4]
        with col:
            st.markdown(f'<div class="metric-container">', unsafe_allow_html=True)
            st.metric(name, f"{data['price']} {data['unit']}", f"{data['delta']}%")
            
            # Sparkline Plot
            spark_data = generate_sparkline(data['price'])
            fig_spark = go.Figure()
            fig_spark.add_trace(go.Scatter(y=spark_data, mode='lines', line=dict(color='#00ffcc', width=2)))
            fig_spark.update_layout(
                height=60, margin=dict(l=0, r=0, t=0, b=0),
                xaxis=dict(visible=False), yaxis=dict(visible=False),
                paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)'
            )
            st.plotly_chart(fig_spark, use_container_width=True, config={'displayModeBar': False})
            st.markdown('</div>', unsafe_allow_html=True)

# --- TAB 2: STRESS TEST SIMULATOR ---
with tab2:
    st.title("🛡️ Strategic Stress Test: Hormuz Closure")
    
    col_s1, col_s2 = st.columns([1, 3])
    with col_s1:
        st.markdown("### Simulation Parameters")
        days = st.slider("Duration of Closure (Days)", 1, 120, 14)
        panic = st.select_slider("Market Sentiment", options=["Calm", "Elevated", "Panic"])
        multiplier = {"Calm": 0.7, "Elevated": 1.2, "Panic": 2.8}[panic]

    with col_s2:
        # Simulation Logic
        sim_data = []
        for name, data in commodities.items():
            impact = (np.log1p(days) * data['elasticity'] * multiplier)
            sim_price = round(data['price'] * (1 + (impact / 100)), 2)
            sim_data.append({"Commodity": name, "Current": data['price'], "Simulated": sim_price})
        
        df_sim = pd.DataFrame(sim_data)
        
        # Dual Axis Plot
        fig = make_subplots(specs=[[{"secondary_y": True}]])
        
        # Primary: Oil/Gas/Products
        mask = df_sim['Commodity'] != "Sulphur"
        fig.add_trace(go.Bar(name='Simulated Price', x=df_sim[mask]['Commodity'], y=df_sim[mask]['Simulated'], marker_color='#ff4b4b'), secondary_y=False)
        fig.add_trace(go.Bar(name='Current Price', x=df_sim[mask]['Commodity'], y=df_sim[mask]['Current'], marker_color='#4b4bff'), secondary_y=False)
        
        # Secondary: Sulphur
        s_val = df_sim[df_sim['Commodity'] == "Sulphur"]
        fig.add_trace(go.Bar(name='Simulated Sulphur', x=s_val['Commodity'], y=s_val['Simulated'], marker_color='#ffd700'), secondary_y=True)
        
        fig.update_layout(title_text=f"Impact Analysis: {days} Days @ {panic} Level", barmode='group', template="plotly_dark")
        fig.update_yaxes(title_text="USD / Bbl / MWh", secondary_y=False)
        fig.update_yaxes(title_text="USD/MT (Sulphur)", secondary_y=True)
        st.plotly_chart(fig, use_container_width=True)

# --- TAB 3: GLOBAL INTELLIGENCE ---
with tab3:
    st.header("Latest Intelligence Briefing")
    
    c1, c2 = st.columns(2)
    with c1:
        st.info("### 🚨 IEA Emergency Response")
        st.write("""
        **March 11-28, 2026:** The IEA has activated a record 400M barrel SPR release. 
        - **Americas:** 172M barrels (mostly crude).
        - **Asia-Oceania:** 108M barrels (immediate release).
        - **Europe:** 107M barrels (refined products focus).
        """)
    with c2:
        st.warning("### 🚢 Logistics & Bypass Status")
        st.write("""
        - **Yanbu (Saudi):** Ramping to 3.4 MMbpd; security risk 'High' at Bab al-Mandeb.
        - **Fujairah (UAE):** ADNOC restoring capacity to 1.9 MMbpd after drone strike repairs.
        - **Hormuz:** Commercial traffic remains effectively at zero.
        """)
    
    st.divider()
    st.markdown("#### March 28 News Wire")
    st.write("- *Reuters:* India exploring rupee-denominated oil hedges with non-Gulf producers.")
    st.write("- *Bloomberg:* Jet fuel prices hit $230/bbl in Singapore as Mideast refining hubs shut in.")
