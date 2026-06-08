import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import os
import io
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
st.markdown("### Sprint 1: Carbon Baseline & Dataset Explorer")
st.write("This interactive dashboard aggregates, cleans, and analyzes Xebia's simulated cloud infrastructure usage to establish a carbon emissions baseline (kg CO2e).")

if df is None:
    st.error("Enriched dataset not found. Please paste your Azure Connection String in `.env` or run `python data/process_dataset.py` to generate a local baseline.")
else:
    
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
        
        # Interactive chart via Streamlit
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
        selected_provider = st.multiselect("Cloud Provider", options=df['provider'].unique(), default=df['provider'].unique())
    with col_f2:
        selected_service = st.multiselect("Service Type", options=df['service_type'].unique(), default=df['service_type'].unique())
    with col_f3:
        selected_team = st.multiselect("Team", options=df['team'].unique(), default=df['team'].unique())
        
    filtered_df = df[
        (df['provider'].isin(selected_provider)) &
        (df['service_type'].isin(selected_service)) &
        (df['team'].isin(selected_team))
    ]
    
    st.dataframe(filtered_df, width='stretch')
    st.caption(f"Showing {len(filtered_df)} records of {len(df)} after filtering.")
