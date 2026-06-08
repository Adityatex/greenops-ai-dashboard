import streamlit as st
import pandas as pd
import requests
import os

# Set page configuration
st.set_page_config(
    page_title="GreenOps AI Dashboard",
    page_icon="🌱",
    layout="wide",
    initial_sidebar_state="expanded"
)

# API Base URL from environment or fallback to localhost
API_BASE_URL = os.getenv("API_BASE_URL", "http://127.0.0.1:8000")

# Helper function to fetch data from the FastAPI backend
def fetch_from_api(endpoint):
    url = f"{API_BASE_URL}{endpoint}"
    try:
        response = requests.get(url, timeout=5)
        if response.status_code == 200:
            return response.json()
        else:
            st.sidebar.error(f"API Error ({response.status_code}): {response.text}")
            return None
    except Exception as e:
        return None

# Custom styling for premium look and feel
st.markdown("""
    <style>
    .main {
        background-color: #f8f9fa;
    }
    .metric-card {
        background: #ffffff;
        padding: 20px;
        border-radius: 12px;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.05);
        border-left: 5px solid #2ec4b6;
        margin-bottom: 15px;
    }
    .metric-label {
        font-size: 14px;
        color: #6c757d;
        font-weight: 500;
    }
    .metric-value {
        font-size: 28px;
        color: #1d3557;
        font-weight: 700;
        margin-top: 5px;
    }
    .score-badge {
        font-size: 48px;
        font-weight: 800;
        text-align: center;
        padding: 10px;
        border-radius: 10px;
        color: white;
        margin-bottom: 10px;
    }
    </style>
""", unsafe_allow_html=True)

# Title & Overview
st.title("🌱 GreenOps AI: Unified Carbon Reduction Dashboard")
st.write("Exposes real-time cloud carbon footprint metrics, ML-driven time-series forecasting, and shift-left sustainability gating.")

# Sidebar Status
st.sidebar.subheader("🔌 Connection Status")
health_data = fetch_from_api("/health")

if health_data and health_data.get("status") == "ok":
    st.sidebar.success("FastAPI Backend: ONLINE 🟢")
    st.sidebar.info(f"Connected to API base: `{API_BASE_URL}`")
    
    # Fetch dynamic data from REST API
    summary = fetch_from_api("/metrics/summary")
    daily_data = fetch_from_api("/metrics/daily")
    green_score = fetch_from_api("/green-score")
    
    if summary and daily_data and green_score:
        
        # 1. Row 1: KPI Metrics & Green Score
        col1, col2, col3, col_score = st.columns([1, 1, 1, 1.2])
        
        with col1:
            st.metric(
                label="Total Carbon Footprint",
                value=f"{summary['total_co2e_kg']:,.2f} kg CO2e"
            )
            st.markdown("""
                <div class="metric-card" style="border-left-color: #e63946; padding: 10px; margin-top: -15px;">
                    <div class="metric-label">Cloud Sustainability Target</div>
                    <div class="metric-value" style="font-size: 16px; color: #e63946;">Goal: < 2.0 kg/day</div>
                </div>
            """, unsafe_allow_html=True)
            
        with col2:
            st.metric(
                label="Total Cloud Cost",
                value=f"${summary['total_cost_usd']:,.2f} USD"
            )
            st.markdown("""
                <div class="metric-card" style="border-left-color: #457b9d; padding: 10px; margin-top: -15px;">
                    <div class="metric-label">Primary Cloud Region</div>
                    <div class="metric-value" style="font-size: 16px; color: #457b9d;">{0}</div>
                </div>
            """.format(summary['top_emitting_region']), unsafe_allow_html=True)
            
        with col3:
            st.metric(
                label="Highest-Emission Team",
                value=summary['top_emitting_team']
            )
            st.markdown("""
                <div class="metric-card" style="border-left-color: #ffb703; padding: 10px; margin-top: -15px;">
                    <div class="metric-label">Daily Avg Cost</div>
                    <div class="metric-value" style="font-size: 16px; color: #ffb703;">$12.99 USD</div>
                </div>
            """, unsafe_allow_html=True)
            
        with col_score:
            # Color coding for Green Score
            grade = green_score["grade"]
            gate = green_score["gate"]
            bg_color = "#2a9d8f" # A, B, C (PASS)
            if gate == "WARNING":
                bg_color = "#f4a261"
            elif gate == "BLOCKED":
                bg_color = "#e76f51"
                
            st.markdown(f"""
                <div style="background-color: {bg_color}; padding: 15px; border-radius: 12px; color: white;">
                    <div style="font-size: 12px; font-weight: 600; text-transform: uppercase; opacity: 0.8;">Shift-Left Sustainability Score</div>
                    <div style="font-size: 40px; font-weight: 800; line-height: 1;">Grade {grade}</div>
                    <div style="font-size: 14px; font-weight: 600; margin-top: 5px;">VERDICT: {gate}</div>
                    <div style="font-size: 11px; opacity: 0.9; margin-top: 5px;">{green_score['action']}</div>
                </div>
            """, unsafe_allow_html=True)

        st.markdown("---")
        
        # 2. Row 2: Daily Emissions Trend Line Chart
        st.subheader("📈 Daily Carbon Emissions Trend (Historical)")
        daily_df = pd.DataFrame(daily_data)
        daily_df['date'] = pd.to_datetime(daily_df['date'])
        daily_df = daily_df.set_index('date')
        st.line_chart(daily_df['co2e_kg'], color="#2ec4b6")
        
        st.markdown("---")
        
        # 3. Row 3: Time-Series Carbon Forecasting API Query
        st.subheader("🔮 30-Day Carbon Emissions Time-Series Forecast")
        st.write("Click below to query the FastAPI time-series model (Linear Regression) to predict emissions recursively for the next month.")
        
        if st.button("🔮 Generate 30-Day Forecast"):
            with st.spinner("Querying forecasting API..."):
                forecast_data = fetch_from_api("/forecast")
                if forecast_data:
                    forecast_df = pd.DataFrame(forecast_data)
                    forecast_df['date'] = pd.to_datetime(forecast_df['date'])
                    forecast_df = forecast_df.set_index('date')
                    
                    col_f1, col_f2 = st.columns([2, 1])
                    with col_f1:
                        st.line_chart(forecast_df['predicted_co2e'], color="#e63946")
                    with col_f2:
                        st.write("**Forecasted Daily Value Grid**")
                        st.dataframe(forecast_df, width='stretch')
                else:
                    st.error("Failed to fetch forecast predictions from the API backend.")

else:
    st.sidebar.error("FastAPI Backend: OFFLINE 🔴")
    st.warning("⚠️ **Connection Error**: Streamlit cannot connect to the FastAPI backend service.")
    st.info(f"Please verify that the FastAPI backend is running locally at: `{API_BASE_URL}`")
    st.markdown("""
        To start the FastAPI backend server, open a new terminal, activate your virtual environment, and run:
        ```bash
        greenops-env\\Scripts\\activate
        uvicorn api.main:app --reload
        ```
    """)
