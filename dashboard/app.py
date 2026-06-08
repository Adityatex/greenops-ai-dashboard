import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import os
import io
import joblib
from dotenv import load_dotenv
from azure.storage.blob import BlobServiceClient

# Load environment variables
load_dotenv()

# Set page configuration
st.set_page_config(
    page_title="GreenOps AI Dashboard",
    page_icon="🌱",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Cache data loading to optimize performance
@st.cache_data
def load_dataset():
    conn_str = os.getenv("AZURE_STORAGE_CONNECTION_STRING")
    if conn_str:
        try:
            blob_service_client = BlobServiceClient.from_connection_string(conn_str)
            container_name = "greenops-data"
            blob_name = "cloud_usage_enriched.csv"
            container_client = blob_service_client.get_container_client(container_name)
            blob_client = container_client.get_blob_client(blob_name)
            data = blob_client.download_blob().readall()
            df = pd.read_csv(io.BytesIO(data), parse_dates=['date'])
            return df, "Live Cloud Mode ☁️"
        except Exception as e:
            st.sidebar.error(f"Azure Connection Error: {e}")
            
    # Fallback to local
    enriched_path = 'data/cloud_usage_enriched.csv'
    if os.path.exists(enriched_path):
        df = pd.read_csv(enriched_path, parse_dates=['date'])
        return df, "Local Offline Mode 💾"
    else:
        return None, None

# Load dataset and determine mode
df, mode_label = load_dataset()

# Custom Styling for Premium Design
st.markdown("""
    <style>
    .main {
        background-color: #f8f9fa;
    }
    .metric-card {
        background: white;
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
    </style>
""", unsafe_allow_html=True)

# Add sidebar details
if mode_label:
    st.sidebar.subheader("🔌 Connection Status")
    if "Live Cloud" in mode_label:
        st.sidebar.success(mode_label)
        st.sidebar.info("Data source: Azure Blob Storage (`greenops-data`)")
    else:
        st.sidebar.warning(mode_label)
        st.sidebar.info("Data source: Local filesystem (`data/cloud_usage_enriched.csv`)")

st.title("🌱 GreenOps AI: Cloud Sustainability & Carbon Dashboard")
st.write("This interactive dashboard aggregates, cleans, and analyzes Xebia's simulated cloud infrastructure usage to establish a carbon emissions baseline and forecast future trends.")

if df is None:
    st.error("Enriched dataset not found. Please paste your Azure Connection String in `.env` or run `python data/process_dataset.py` to generate a local baseline.")
else:
    # Create main tabs
    tab_analytics, tab_forecast = st.tabs(["📊 Baseline Analytics", "🔮 AI Carbon Forecasting"])
    
    with tab_analytics:
        st.markdown("### Sprint 1: Carbon Baseline & Dataset Explorer")
        
        # Calculate global metrics
        total_cost = df['cost_usd'].sum()
        total_co2e = df['co2e_kg'].sum()
        avg_daily_cost = df.groupby('date')['cost_usd'].sum().mean()
        avg_daily_co2e = df.groupby('date')['co2e_kg'].sum().mean()
        
        # KPI Grid Layout
        st.markdown("---")
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.markdown(f"""
                <div class="metric-card">
                    <div class="metric-label">Total Cloud Spend</div>
                    <div class="metric-value">${total_cost:,.2f}</div>
                </div>
            """, unsafe_allow_html=True)
            
        with col2:
            st.markdown(f"""
                <div class="metric-card" style="border-left-color: #e63946;">
                    <div class="metric-label">Total Carbon Footprint</div>
                    <div class="metric-value">{total_co2e:,.2f} kg CO2e</div>
                </div>
            """, unsafe_allow_html=True)
            
        with col3:
            st.markdown(f"""
                <div class="metric-card" style="border-left-color: #457b9d;">
                    <div class="metric-label">Average Daily Cost</div>
                    <div class="metric-value">${avg_daily_cost:,.2f}</div>
                </div>
            """, unsafe_allow_html=True)
            
        with col4:
            st.markdown(f"""
                <div class="metric-card" style="border-left-color: #ffb703;">
                    <div class="metric-label">Avg Daily Emissions</div>
                    <div class="metric-value">{avg_daily_co2e:,.3f} kg</div>
                </div>
            """, unsafe_allow_html=True)

        st.markdown("---")
        
        # Graphs and Visualizations Section
        col_left, col_right = st.columns([2, 1])
        
        with col_left:
            st.subheader("📈 Carbon Emissions Over Time")
            daily_co2e = df.groupby('date')['co2e_kg'].sum().sort_index()
            st.line_chart(daily_co2e, color="#2ec4b6")
            
        with col_right:
            st.subheader("🌍 Emissions by Cloud Region")
            region_co2e = df.groupby('region')['co2e_kg'].sum().sort_values(ascending=False)
            st.bar_chart(region_co2e, color="#1d3557")

        st.markdown("---")
        
        # Service and Team breakdowns
        col_srv, col_team = st.columns(2)
        
        with col_srv:
            st.subheader("🔌 Emissions by Cloud Service Type")
            service_co2e = df.groupby('service_type')['co2e_kg'].sum().sort_values(ascending=False).reset_index()
            service_co2e.columns = ['Service Type', 'CO2e (kg)']
            st.dataframe(
                service_co2e.style.background_gradient(cmap='Greens', subset=['CO2e (kg)']),
                width='stretch',
                hide_index=True
            )
            
        with col_team:
            st.subheader("👥 Emissions by Engineering Team")
            team_co2e = df.groupby('team')['co2e_kg'].sum().sort_values(ascending=False).reset_index()
            team_co2e.columns = ['Team', 'CO2e (kg)']
            st.dataframe(
                team_co2e.style.background_gradient(cmap='Blues', subset=['CO2e (kg)']),
                width='stretch',
                hide_index=True
            )

        st.markdown("---")
        
        # Dataset Explorer section
        st.subheader("🔍 Enriched Dataset Explorer")
        st.write("Browse the raw telemetry logs containing resource utilization metrics and computed carbon equivalence values.")
        
        # Filters
        col_f1, col_f2, col_f3 = st.columns(3)
        with col_f1:
            selected_provider = st.multiselect("Cloud Provider", options=df['provider'].unique(), default=df['provider'].unique(), key="f_provider")
        with col_f2:
            selected_service = st.multiselect("Service Type", options=df['service_type'].unique(), default=df['service_type'].unique(), key="f_service")
        with col_f3:
            selected_team = st.multiselect("Team", options=df['team'].unique(), default=df['team'].unique(), key="f_team")
            
        filtered_df = df[
            (df['provider'].isin(selected_provider)) &
            (df['service_type'].isin(selected_service)) &
            (df['team'].isin(selected_team))
        ]
        
        st.dataframe(filtered_df, width='stretch')
        st.caption(f"Showing {len(filtered_df)} records of {len(df)} after filtering.")
        
    with tab_forecast:
        st.markdown("### Sprint 2: AI Carbon Forecasting Model")
        st.write("Predict future cloud carbon footprints using time-series features (lags, rolling averages, and days-of-week).")
        
        model_path = 'model/co2e_model.pkl'
        plot_path = 'model/forecast_plot.png'
        
        if not os.path.exists(model_path) or not os.path.exists(plot_path):
            st.warning("Forecasting model has not been trained yet. Please run `python model/train_model.py` in your terminal to train the model and generate metrics.")
        else:
            # Model stats and comparisons
            st.subheader("📊 Model Evaluation & Comparison")
            col_m1, col_m2, col_m3 = st.columns(3)
            with col_m1:
                st.markdown("""
                    <div class="metric-card" style="border-left-color: #1d3557;">
                        <div class="metric-label">Best Selected Model</div>
                        <div class="metric-value">Linear Regression</div>
                    </div>
                """, unsafe_allow_html=True)
            with col_m2:
                st.markdown("""
                    <div class="metric-card" style="border-left-color: #e63946;">
                        <div class="metric-label">Linear Regression RMSE</div>
                        <div class="metric-value">0.0250 kg</div>
                    </div>
                """, unsafe_allow_html=True)
            with col_m3:
                st.markdown("""
                    <div class="metric-card" style="border-left-color: #2ec4b6;">
                        <div class="metric-label">Random Forest RMSE</div>
                        <div class="metric-value">0.0259 kg</div>
                    </div>
                """, unsafe_allow_html=True)
                
            st.image(plot_path, caption="Evaluation Results: Actual vs. Predicted daily emissions over the 30-day testing window.", width='stretch')
            
            st.markdown("---")
            
            # Prediction interface
            st.subheader("🔮 Live Daily Carbon Predictor")
            st.write("Input simulated telemetry lag factors and rolling metrics to generate a live daily carbon prediction.")
            
            # Loading model
            model = joblib.load(model_path)
            
            col_p1, col_p2 = st.columns(2)
            with col_p1:
                input_lag7 = st.number_input("Emissions 7 days ago (kg CO2e)", min_value=0.0, max_value=2.0, value=0.045, step=0.005)
                input_lag14 = st.number_input("Emissions 14 days ago (kg CO2e)", min_value=0.0, max_value=2.0, value=0.042, step=0.005)
            with col_p2:
                input_roll7 = st.number_input("7-Day rolling average emissions (kg CO2e)", min_value=0.0, max_value=2.0, value=0.044, step=0.005)
                day_options = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
                selected_day = st.selectbox("Forecast Day of Week", options=day_options, index=0)
                input_dow = day_options.index(selected_day)
                
            if st.button("Predict Daily CO2e emissions"):
                # Make prediction
                # Features shape: ['lag_7', 'lag_14', 'rolling_7', 'dow']
                pred_val = model.predict([[input_lag7, input_lag14, input_roll7, input_dow]])[0]
                
                st.markdown("---")
                st.markdown(f"### Predicted Emissions: **{pred_val:.4f} kg CO2e**")
                
                # Context comparison
                mean_daily = 0.0445
                pct_diff = ((pred_val - mean_daily) / mean_daily) * 100
                if pct_diff > 0:
                    st.warning(f"This is **{pct_diff:.1f}% higher** than the average daily baseline emissions ({mean_daily:.4f} kg).")
                else:
                    st.info(f"This is **{abs(pct_diff):.1f}% lower** than the average daily baseline emissions ({mean_daily:.4f} kg).")
