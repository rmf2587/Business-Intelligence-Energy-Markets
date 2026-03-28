import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import yfinance as yf
import feedparser
import numpy as np
from datetime import datetime

# --- 1. APP CONFIGURATION ---
st.set_page_config(page_title="Executive Energy Suite", layout="wide", initial_sidebar_state="collapsed")

# Inject Custom CSS for Dark Mode Metric Boxes
st.markdown("""
    <style>
    .metric-box {
        background-color: #1E1E1E;
        border: 1px solid #333333;
        border-radius: 8px;
        padding: 15px;
        margin-bottom: 15px;
        box-shadow: 2px 2px 5px rgba(0,0,0,0.5);
    }
    .metric-title { color: #A0A0A0; font-size: 14px; font-weight: bold; margin-bottom: 5px; }
    .metric-value { color: #FFFFFF; font-size: 24px; font-weight: bold; }
    .metric-positive { color: #00FF7F; font-size: 14px; }
    .metric-negative { color: #FF4C4C; font-size: 14px; }
    </style>
    """, unsafe_allow_html=True)

# --- 2. LIVE DATA ENGINE ---
@st.cache_data(ttl=600) # Caches data for 10 minutes to prevent API bans
def fetch_live_market_data():
    # Tickers: Brent, WTI (Proxy for Murban), Nat Gas, Heating Oil (Proxy for Jet/Naphtha)
    tickers = {"Brent Crude": "BZ=F", "WTI Crude": "CL=F", "Natural Gas": "NG=F", "Heating Oil": "HO=F"}
    data_store = []
    
    for name, ticker in tickers.items():
        try:
            # Fetch last 30 days of data
            history = yf.Ticker(ticker).history(period="1mo")
            if not history.empty:
                current_price = history['Close'].iloc[-1]
                avg_30d = history['Close'].mean()
                pct_change = ((current_price - avg_30d) / avg_30d) * 100
                prices_array = history['Close'].tolist()
                
                data_store.append({
                    "Commodity": name, "Price": round(current_price, 2), 
                    "30D Avg": round(avg_30d, 2), "Delta": round(pct_change, 2),
                    "History": prices_array, "Live": True
                })
        except Exception as e:
            continue # Skip gracefully if API fails

    # Fallback/Proxy Generators for Enterprise Commodities (Urea, Sulphur, LNG TTF)
    # In a real enterprise app, replace this block with your Bloomberg/Platts API calls
    base_niche = {"LNG (TTF Proxy)": 45.50, "Sulphur (Proxy)": 1400.00, "Urea (Proxy)": 650.00}
    for name, base in base_niche.items():
        # Generate a realistic 30-day random walk based on WTI volatility
        volatility = data_store[1]['Delta'] / 100 if len(data_store) > 1 else 0.02
        walk = [base * (1 + (np.random.randn() * abs(volatility)))]
        for _ in range(29):
            walk.append(walk[-1] * (1 + (np.random.randn() * 0.015)))
        
        current = walk[-1]
        avg = np.mean(walk)
        data_store.append({
            "Commodity": name, "Price": round(current, 2),
            "30D Avg": round(avg, 2), "Delta": round(((current - avg) / avg) * 100, 2),
            "History": walk, "Live": False
        })
        
    return pd.DataFrame(data_store)

@st.cache_data(ttl=1800) # Cache news for 30 mins
def fetch_live_news():
    try:
        # Pulling live RSS feed from Yahoo Finance Energy
        feed = feedparser.parse("https://feeds.finance.yahoo.com/rss/2.0/headline?s=XLE,CL=F,BZ=F,NG=F")
        return [{"title": entry.title, "link": entry.link, "published": entry.published} for entry in feed.entries[:8]]
    except:
        return []

# --- 3. UI GENERATION ---
st.title("🌐 Live Executive Energy Suite")
st.caption(f"Last Sync: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} | Source: Yahoo Finance API & Proxies")

# Fetch Data
df_market = fetch_live_market_data()
news_items = fetch_live_news()

tab1, tab2, tab3 = st.tabs(["📊 Live Market Monitor", "🛡️ Stress Test Simulator", "📰 Live Intelligence & Analysis"])

# --- TAB 1: LIVE MARKET MONITOR ---
with tab1:
    st.subheader("Global Commodities: Live Pricing & 30-Day Trends")
    
    # Create a dynamic grid (4 columns)
    cols = st.columns(4)
    for index, row in df_market.iterrows():
        col = cols[index % 4]
        with col:
            # HTML for the Box
            delta_class = "metric-positive" if row['Delta'] > 0 else "metric-negative"
            sign = "+" if row['Delta'] > 0 else ""
            status = "🟢 Live" if row['Live'] else "🟡 Proxy"
            
            st.markdown(f"""
                <div class="metric-box">
                    <div class="metric-title">{row['Commodity']} <span style='float:right; font-size:10px;'>{status}</span></div>
                    <div class="metric-value">${row['Price']}</div>
                    <div class="{delta_class}">{sign}{row['Delta']}% vs 30D Avg</div>
                </div>
            """, unsafe_allow_html=True)
            
            # Sparkline Chart below the HTML box
            fig = go.Figure(go.Scatter(y=row['History'], mode='lines', 
                                       line=dict(color='#00FF7F' if row['Delta'] > 0 else '#FF4C4C', width=2),
                                       fill='tozeroy', fillcolor='rgba(0, 255, 127, 0.1)' if row['Delta'] > 0 else 'rgba(255, 76, 76, 0.1)'))
            fig.update_layout(height=60, margin=dict(l=0, r=0, t=0, b=0), 
                              xaxis_visible=False, yaxis_visible=False, 
                              paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)')
            st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})

# --- TAB 2: STRESS TEST SIMULATOR ---
with tab2:
    st.subheader("Geopolitical Stress Test: Price Impact Modeling")
    
    c1, c2 = st.columns([1, 3])
    with c1:
        st.write("Adjust the parameters to simulate supply chain disruptions.")
        days_disrupted = st.slider("Duration of Supply Shock (Days)", 0, 90, 14)
        panic_factor = st.select_slider("Market Sentiment Multiplier", options=[0.8, 1.0, 1.5, 2.5], value=1.5)
        
    with c2:
        # Dynamic Simulation based on Live Prices
        sim_data = []
        for index, row in df_market.iterrows():
            # Elasticity logic: Energy products spike harder than slower-moving niche inputs initially
            elasticity = 0.5 if "Sulphur" in row['Commodity'] or "Urea" in row['Commodity'] else 1.2
            simulated_price = row['Price'] * (1 + ((days_disrupted / 100) * panic_factor * elasticity))
            sim_data.append({"Commodity": row['Commodity'], "Live": row['Price'], "Simulated": simulated_price})
            
        df_sim = pd.DataFrame(sim_data)
        
        # Dual-Axis Plotly Chart
        fig_sim = make_subplots(specs=[[{"secondary_y": True}]])
        
        # Primary Axis Data (Crude, Gas)
        mask_primary = ~df_sim['Commodity'].str.contains("Sulphur")
        fig_sim.add_trace(go.Bar(name='Live Price', x=df_sim[mask_primary]['Commodity'], y=df_sim[mask_primary]['Live'], marker_color='#1f77b4'), secondary_y=False)
        fig_sim.add_trace(go.Bar(name='Sim Shock Price', x=df_sim[mask_primary]['Commodity'], y=df_sim[mask_primary]['Simulated'], marker_color='#FF4C4C'), secondary_y=False)
        
        # Secondary Axis Data (Sulphur)
        mask_sec = df_sim['Commodity'].str.contains("Sulphur")
        if any(mask_sec):
            fig_sim.add_trace(go.Line(name='Sulphur (Live)', x=df_sim[mask_sec]['Commodity'], y=df_sim[mask_sec]['Live'], marker_color='#FFA500'), secondary_y=True)
            fig_sim.add_trace(go.Line(name='Sulphur (Sim)', x=df_sim[mask_sec]['Commodity'], y=df_sim[mask_sec]['Simulated'], line=dict(color='#FFA500', dash='dash')), secondary_y=True)
            
        fig_sim.update_layout(template="plotly_dark", barmode='group', margin=dict(t=30, b=0))
        fig_sim.update_yaxes(title_text="Standard Commodities (USD)", secondary_y=False)
        fig_sim.update_yaxes(title_text="Sulphur Metrics (USD/MT)", secondary_y=True, showgrid=False)
        st.plotly_chart(fig_sim, use_container_width=True)

# --- TAB 3: DYNAMIC INTELLIGENCE & NEWS ---
with tab3:
    c_news, c_analysis = st.columns([2, 1])
    
    with c_news:
        st.subheader("📰 Live Global Energy Feed")
        if news_items:
            for item in news_items:
                st.markdown(f"**[{item['title']}]({item['link']})**")
                st.caption(f"Published: {item['published']}")
                st.divider()
        else:
            st.warning("News feed temporarily unavailable. Please check firewall settings.")
            
    with c_analysis:
        st.subheader("🤖 Algorithmic Market Briefing")
        
        # Dynamic Analysis based on current dataframe state
        bullish_count = sum(df_market['Delta'] > 0)
        total_assets = len(df_market)
        sentiment = "Bullish / Inflating" if bullish_count > (total_assets / 2) else "Bearish / Deflating"
        avg_move = df_market['Delta'].mean()
        
        st.info(f"**Current Macro Sentiment:** {sentiment}")
        st.write(f"""
        Based on live data integration, **{bullish_count} out of {total_assets}** tracked commodities are currently trading above their 30-day moving average.
        
        The average market momentum across the tracked portfolio is **{avg_move:.2f}%**. 
        
        *Implications:* If average portfolio momentum remains positive, expect heightened short-term margin pressure on downstream refined products and agricultural inputs. The dynamic stress test currently projects maximum exposure on high-elasticity assets like Natural Gas and Brent Crude if supply chain bottlenecks persist beyond 14 days.
        """)
