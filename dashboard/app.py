import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import os

# Set page configuration
st.set_page_config(
    page_title="GreenOps AI Dashboard",
    page_icon="🌱",
    layout="wide",
    initial_sidebar_state="expanded"
)

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

st.title("🌱 GreenOps AI: Cloud Sustainability & Carbon Dashboard")
st.markdown("### Sprint 1: Carbon Baseline & Dataset Explorer")
st.write("This interactive dashboard aggregates, cleans, and analyzes Xebia's simulated cloud infrastructure usage to establish a carbon emissions baseline (kg CO2e).")

# Load enriched data
enriched_path = 'data/cloud_usage_enriched.csv'

if not os.path.exists(enriched_path):
    st.error(f"Enriched dataset not found at `{enriched_path}`. Please run `python data/process_dataset.py` first to generate it.")
else:
    df = pd.read_csv(enriched_path, parse_dates=['date'])
    
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
            use_container_width=True,
            hide_index=True
        )
        
    with col_team:
        st.subheader("👥 Emissions by Engineering Team")
        team_co2e = df.groupby('team')['co2e_kg'].sum().sort_values(ascending=False).reset_index()
        team_co2e.columns = ['Team', 'CO2e (kg)']
        st.dataframe(
            team_co2e.style.background_gradient(cmap='Blues', subset=['CO2e (kg)']),
            use_container_width=True,
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
    
    st.dataframe(filtered_df, use_container_width=True)
    st.caption(f"Showing {len(filtered_df)} records of {len(df)} after filtering.")
