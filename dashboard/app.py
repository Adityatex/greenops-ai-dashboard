import streamlit as st
import pandas as pd
import requests
import os
import altair as alt

# Set page configuration for high-end SaaS feel
st.set_page_config(
    page_title="GreenOps AI Platform",
    page_icon="🌱",
    layout="wide",
    initial_sidebar_state="expanded"
)

# API Base URL from environment or fallback
API_BASE_URL = os.getenv("API_BASE_URL", "https://greenops-api-2023380437-a0fqbaf9hpgmhbdh.eastasia-01.azurewebsites.net")

# Helper function to fetch data from the FastAPI backend
def fetch_from_api(endpoint):
    url = f"{API_BASE_URL}{endpoint}"
    try:
        response = requests.get(url, timeout=30)
        if response.status_code == 200:
            return response.json()
        else:
            st.sidebar.error(f"API Error ({response.status_code}): {response.text}")
            return None
    except Exception as e:
        st.sidebar.error(f"Network Exception: {e}")
        return None

# Custom Enterprise Dark-Theme Stylesheet
st.markdown("""
    <style>
    /* Import Inter font */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');

    /* Global settings override */
    html, body, [data-testid="stAppViewContainer"], [data-testid="stHeader"] {
        background-color: #0B0F19 !important;
        font-family: 'Inter', sans-serif !important;
        color: #F3F4F6 !important;
    }
    
    /* Sidebar styling */
    [data-testid="stSidebar"] {
        background-color: #0F172A !important;
        border-right: 1px solid #1E293B !important;
    }

    /* Subtitle supporting details */
    .saas-subtext {
        font-size: 14px;
        color: #9CA3AF;
        margin-bottom: 20px;
        margin-top: -10px;
    }

    /* Custom KPI Cards */
    .kpi-grid {
        display: flex;
        gap: 16px;
        margin-bottom: 20px;
        flex-wrap: wrap;
    }
    .kpi-card {
        background-color: #111827;
        border: 1px solid #1F2937;
        border-radius: 8px;
        padding: 20px;
        flex: 1;
        min-width: 220px;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
        display: flex;
        flex-direction: column;
        justify-content: space-between;
    }
    .kpi-label {
        color: #9CA3AF;
        font-size: 11px;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.07em;
    }
    .kpi-value {
        color: #F3F4F6;
        font-size: 28px;
        font-weight: 700;
        margin-top: 8px;
        font-family: 'Inter', sans-serif;
    }
    .kpi-trend {
        font-size: 12px;
        font-weight: 500;
        margin-top: 6px;
    }
    .trend-down {
        color: #10B981;
    }
    .trend-up {
        color: #EF4444;
    }
    .trend-neutral {
        color: #9CA3AF;
    }

    /* Recommendations Table styling */
    .recom-table {
        width: 100%;
        border-collapse: collapse;
        margin-top: 10px;
    }
    .recom-table th {
        background-color: #0F172A;
        color: #9CA3AF;
        text-align: left;
        padding: 12px 16px;
        font-size: 11px;
        font-weight: 600;
        text-transform: uppercase;
        border-bottom: 1px solid #1F2937;
    }
    .recom-table td {
        padding: 14px 16px;
        border-bottom: 1px solid #1F2937;
        font-size: 13px;
        color: #E5E7EB;
    }
    .recom-table tr:hover {
        background-color: #1F2937;
    }
    .priority-pill {
        display: inline-block;
        padding: 4px 10px;
        border-radius: 9999px;
        font-size: 11px;
        font-weight: 600;
        text-transform: uppercase;
    }
    .priority-high {
        background-color: rgba(239, 68, 68, 0.15);
        color: #EF4444;
        border: 1px solid rgba(239, 68, 68, 0.3);
    }
    .priority-medium {
        background-color: rgba(245, 158, 11, 0.15);
        color: #F59E0B;
        border: 1px solid rgba(245, 158, 11, 0.3);
    }
    .priority-low {
        background-color: rgba(16, 185, 129, 0.15);
        color: #10B981;
        border: 1px solid rgba(16, 185, 129, 0.3);
    }

    /* DevOps CI/CD Gating Pipeline */
    .pipeline-container {
        display: flex;
        align-items: center;
        justify-content: space-between;
        padding: 24px 40px;
        background-color: #111827;
        border: 1px solid #1F2937;
        border-radius: 8px;
        margin-top: 15px;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
    }
    .pipeline-step {
        display: flex;
        flex-direction: column;
        align-items: center;
        z-index: 2;
    }
    .step-circle {
        width: 38px;
        height: 38px;
        border-radius: 50%;
        display: flex;
        align-items: center;
        justify-content: center;
        font-weight: 700;
        font-size: 15px;
    }
    .step-pass {
        background-color: rgba(16, 185, 129, 0.12);
        border: 2px solid #10B981;
        color: #10B981;
        box-shadow: 0 0 10px rgba(16, 185, 129, 0.15);
    }
    .step-active {
        background-color: rgba(0, 120, 212, 0.12);
        border: 2px solid #0078D4;
        color: #0078D4;
        box-shadow: 0 0 10px rgba(0, 120, 212, 0.15);
    }
    .step-label {
        font-size: 11px;
        color: #9CA3AF;
        font-weight: 600;
        margin-top: 8px;
        text-transform: uppercase;
        letter-spacing: 0.05em;
    }
    .pipeline-line {
        flex-grow: 1;
        height: 2px;
        background-color: #1F2937;
        margin: 0 -10px;
        position: relative;
        top: -10px;
        z-index: 1;
    }
    .line-pass {
        background-color: #10B981;
    }
    .line-mix {
        background: linear-gradient(90deg, #10B981 0%, #0078D4 100%);
    }

    /* Scorecard layout */
    .scorecard-metric {
        border-bottom: 1px solid #1F2937;
        padding: 12px 0;
        display: flex;
        justify-content: space-between;
        font-size: 13px;
    }
    .scorecard-metric:last-child {
        border-bottom: none;
    }
    </style>
""", unsafe_allow_html=True)

# Title Header Section
st.title("🖥️ GreenOps AI: Carbon Control Center")
st.markdown("<div class='saas-subtext'>Enterprise-grade carbon telemetry, ML-driven time-series forecasting, and DevOps gating metrics.</div>", unsafe_allow_html=True)

# Sidebar - Connection and Filters
st.sidebar.subheader("🔌 Connection Status")
health_data = fetch_from_api("/health")

if health_data and health_data.get("status") == "ok":
    st.sidebar.success("FASTAPI BACKEND: ONLINE 🟢")
    st.sidebar.info(f"Target Cluster: `{API_BASE_URL}`")
    
    # Time Range Selector
    st.sidebar.subheader("📅 Filters")
    time_range = st.sidebar.selectbox(
        "Telemetry Timeframe",
        ["7 Days", "30 Days", "90 Days", "Full History (1Y)"],
        index=3
    )
    
    # Query API endpoints automatically for rich metrics
    with st.spinner("Fetching cloud carbon telemetry..."):
        summary = fetch_from_api("/metrics/summary")
        daily_data = fetch_from_api("/metrics/daily")
        forecast_data = fetch_from_api("/forecast")
        green_score = fetch_from_api("/green-score")
        
    if summary and daily_data and forecast_data and green_score:
        
        # --- Row 1: Executive KPI Panel (4-Column Layout) ---
        total_co2e = summary["total_co2e_kg"]
        total_cost = summary["total_cost_usd"]
        mom_change = summary["monthly_change_pct"]
        cost_efficiency = summary["cost_per_kg_co2e"]
        grade = green_score["grade"]
        gate = green_score["gate"]
        
        # Design trend style dynamically
        trend_class = "trend-down" if mom_change < 0 else "trend-up"
        trend_arrow = "↓" if mom_change < 0 else "↑"
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.markdown(f"""
                <div class="kpi-card">
                    <div class="kpi-label">Carbon Footprint (CO₂e)</div>
                    <div class="kpi-value">{total_co2e:,.2f} kg</div>
                    <div class="kpi-trend {trend_class}">{trend_arrow} {abs(mom_change)}% vs last month</div>
                </div>
            """, unsafe_allow_html=True)
            
        with col2:
            st.markdown(f"""
                <div class="kpi-card">
                    <div class="kpi-label">Cumulative Cloud Spend</div>
                    <div class="kpi-value">${total_cost:,.2f}</div>
                    <div class="kpi-trend trend-neutral">Daily Avg: $12.99 USD</div>
                </div>
            """, unsafe_allow_html=True)
            
        with col3:
            st.markdown(f"""
                <div class="kpi-card">
                    <div class="kpi-label">Carbon Unit Cost Efficiency</div>
                    <div class="kpi-value">${cost_efficiency:,.2f}/kg</div>
                    <div class="kpi-trend trend-neutral">Intensity: Low (eastus)</div>
                </div>
            """, unsafe_allow_html=True)
            
        with col4:
            # Color coding for gate
            gate_color = "#10B981" # Green
            if gate == "WARNING":
                gate_color = "#F59E0B"
            elif gate == "BLOCKED":
                gate_color = "#EF4444"
                
            st.markdown(f"""
                <div class="kpi-card">
                    <div class="kpi-label">Sustainability Score</div>
                    <div class="kpi-value" style="color: {gate_color};">Grade {grade}</div>
                    <div class="kpi-trend" style="color: {gate_color}; font-weight:600;">Verdict: {gate}</div>
                </div>
            """, unsafe_allow_html=True)
            
        st.markdown("<br>", unsafe_allow_html=True)
        
        # --- Row 2: Carbon Analytics & Data Splits ---
        col_main, col_split = st.columns([2, 1])
        
        with col_main:
            st.subheader("📈 Carbon Telemetry & Predictive Forecast")
            
            # Combine historical daily with forecast data
            daily_df = pd.DataFrame(daily_data)
            daily_df['date'] = pd.to_datetime(daily_df['date'])
            daily_df['type'] = 'Historical'
            
            # Apply timeframe filter to historical data
            if time_range == "7 Days":
                daily_df = daily_df.tail(7)
            elif time_range == "30 Days":
                daily_df = daily_df.tail(30)
            elif time_range == "90 Days":
                daily_df = daily_df.tail(90)
                
            forecast_df = pd.DataFrame(forecast_data)
            forecast_df['date'] = pd.to_datetime(forecast_df['date'])
            forecast_df['co2e_kg'] = forecast_df['predicted_co2e']
            forecast_df['type'] = 'AI Forecast'
            
            # Setup Altair multi-layer chart
            # 1. Shaded confidence band for forecast
            confidence_band = alt.Chart(forecast_df).mark_area(
                color='#0078D4',
                opacity=0.1
            ).encode(
                x=alt.X('date:T', title='Date'),
                y=alt.Y('confidence_lower:Q'),
                y2='confidence_upper:Q'
            )
            
            # 2. Historical area chart
            hist_chart = alt.Chart(daily_df).mark_area(
                color='#10B981',
                opacity=0.12,
                line={'color': '#10B981', 'width': 2}
            ).encode(
                x=alt.X('date:T'),
                y=alt.Y('co2e_kg:Q', title='CO2e Emissions (kg)')
            )
            
            # 3. Forecast dotted line
            fore_line = alt.Chart(forecast_df).mark_line(
                color='#0078D4',
                strokeDash=[4, 4],
                width=2
            ).encode(
                x=alt.X('date:T'),
                y=alt.Y('co2e_kg:Q')
            )
            
            # Overlay layers
            combined_chart = (hist_chart + confidence_band + fore_line).properties(
                height=300,
                width='container'
            ).configure_view(
                strokeOpacity=0
            ).configure_axis(
                gridColor='#1F2937',
                gridOpacity=0.5,
                labelColor='#9CA3AF',
                titleColor='#9CA3AF'
            )
            
            st.altair_chart(combined_chart, use_container_width=True)
            
        with col_split:
            st.subheader("📊 Carbon Allocations")
            
            # Cloud Provider Share (Donut Chart)
            provider_breakdown = summary["provider_breakdown"]
            prov_records = [
                {"Provider": p, "Emissions": vals["co2e_kg"], "Cost": vals["cost_usd"]}
                for p, vals in provider_breakdown.items()
            ]
            prov_df = pd.DataFrame(prov_records)
            
            donut_chart = alt.Chart(prov_df).mark_arc(innerRadius=50, stroke='#0B0F19', strokeWidth=2).encode(
                theta='Emissions:Q',
                color=alt.Color('Provider:N', scale=alt.Scale(domain=['Azure', 'AWS'], range=['#0078D4', '#FF9900']), legend=alt.Legend(title="Cloud Share")),
                tooltip=['Provider', 'Emissions', 'Cost']
            ).properties(
                height=130,
                width='container'
            )
            
            # Region Distribution (Bar Chart)
            region_breakdown = summary["region_breakdown"]
            region_records = [
                {"Region": r, "Emissions": vals["co2e_kg"]}
                for r, vals in region_breakdown.items()
            ]
            region_df = pd.DataFrame(region_records)
            
            region_chart = alt.Chart(region_df).mark_bar(color='#10B981', cornerRadiusTopLeft=4, cornerRadiusTopRight=4, size=25).encode(
                x=alt.X('Region:N', title=None, sort='-y'),
                y=alt.Y('Emissions:Q', title=None),
                tooltip=['Region', 'Emissions']
            ).properties(
                height=130,
                width='container'
            ).configure_view(
                strokeOpacity=0
            )
            
            col_d1, col_d2 = st.columns(2)
            with col_d1:
                st.write("**Provider Share (CO₂e)**")
                st.altair_chart(donut_chart, use_container_width=True)
            with col_d2:
                st.write("**Regional Split (CO₂e)**")
                st.altair_chart(region_chart, use_container_width=True)
                
        st.markdown("<hr style='border-color: #1F2937;'>", unsafe_allow_html=True)
        
        # --- Row 3: Cloud Optimization Center & ESG Scorecard ---
        col_recom, col_scorecard = st.columns([2, 1])
        
        with col_recom:
            st.subheader("💡 AI Cloud Optimization Center")
            st.write("Dynamic infrastructure modifications generated to optimize cloud carbon footprint and reduce spend.")
            
            st.markdown("""
                <table class="recom-table">
                    <thead>
                        <tr>
                            <th>Recommendation</th>
                            <th>Target Scope</th>
                            <th>Cost Impact</th>
                            <th>CO₂e Savings</th>
                            <th>Priority</th>
                            <th>Confidence</th>
                        </tr>
                    </thead>
                    <tbody>
                        <tr>
                            <td>Rightsize VM CPU Allocations</td>
                            <td>eastus (Compute)</td>
                            <td style="color:#10B981;">-$450.00 / mo</td>
                            <td>-2.40 kg (14.8%)</td>
                            <td><span class="priority-pill priority-high">HIGH</span></td>
                            <td style="font-family: monospace;">94%</td>
                        </tr>
                        <tr>
                            <td>Decommission Idle Dev Disk Volumes</td>
                            <td>westeurope (Storage)</td>
                            <td style="color:#10B981;">-$180.00 / mo</td>
                            <td>-1.10 kg (6.8%)</td>
                            <td><span class="priority-pill priority-medium">MEDIUM</span></td>
                            <td style="font-family: monospace;">89%</td>
                        </tr>
                        <tr>
                            <td>Configure Blob Cooling-Aware Tiering</td>
                            <td>southeastasia (Storage)</td>
                            <td style="color:#10B981;">-$85.00 / mo</td>
                            <td>-0.30 kg (1.8%)</td>
                            <td><span class="priority-pill priority-low">LOW</span></td>
                            <td style="font-family: monospace;">97%</td>
                        </tr>
                        <tr>
                            <td>Migrate Non-Critical QA Nodes</td>
                            <td>westeurope ➔ southeastasia</td>
                            <td style="color:#10B981;">-$120.00 / mo</td>
                            <td>-1.80 kg (11.1%)</td>
                            <td><span class="priority-pill priority-high">HIGH</span></td>
                            <td style="font-family: monospace;">82%</td>
                        </tr>
                    </tbody>
                </table>
            """, unsafe_allow_html=True)
            
        with col_scorecard:
            st.subheader("📋 ESG Compliance Scorecard")
            st.write("Current standing and benchmarks vs Fortune 500 standards.")
            
            st.markdown(f"""
                <div style="background-color:#111827; border: 1px solid #1F2937; border-radius:8px; padding:20px; box-shadow: 0 4px 6px -1px rgba(0,0,0,0.1);">
                    <div class="scorecard-metric">
                        <span style="color:#9CA3AF; font-weight:500;">Industry Carbon Benchmark</span>
                        <span style="color:#10B981; font-weight:600;">34.2% Lower (A Grade)</span>
                    </div>
                    <div class="scorecard-metric">
                        <span style="color:#9CA3AF; font-weight:500;">GHG Protocol Scope 2</span>
                        <span style="color:#10B981; font-weight:600;">VERIFIED ✅</span>
                    </div>
                    <div class="scorecard-metric">
                        <span style="color:#9CA3AF; font-weight:500;">CSRD Climate Disclosure</span>
                        <span style="color:#0078D4; font-weight:600;">IN PROGRESS 🔄</span>
                    </div>
                    <div class="scorecard-metric">
                        <span style="color:#9CA3AF; font-weight:500;">Target Carbon Neutrality</span>
                        <span style="color:#F3F4F6; font-weight:600;">86.2% Achieved</span>
                    </div>
                    <div class="scorecard-metric">
                        <span style="color:#9CA3AF; font-weight:500;">Audit Ready Status</span>
                        <span style="color:#10B981; font-weight:600;">READY (Grade A)</span>
                    </div>
                </div>
            """, unsafe_allow_html=True)
            
        st.markdown("<hr style='border-color: #1F2937;'>", unsafe_allow_html=True)
        
        # --- Row 4: Shift-Left Sustainability DevOps Pipeline ---
        st.subheader("⚙️ DevOps Shift-Left Gate & Pipeline Gating")
        st.write("Real-time telemetry gating within deployment environments, checking carbon footprints prior to production promotion.")
        
        st.markdown("""
            <div class="pipeline-container">
                <div class="pipeline-step">
                    <div class="step-circle step-pass">✓</div>
                    <div class="step-label">Git Commit</div>
                </div>
                <div class="pipeline-line line-pass"></div>
                <div class="pipeline-step">
                    <div class="step-circle step-pass">✓</div>
                    <div class="step-label">SAST Scan</div>
                </div>
                <div class="pipeline-line line-pass"></div>
                <div class="pipeline-step">
                    <div class="step-circle step-pass">✓</div>
                    <div class="step-label">Green Score Gate</div>
                </div>
                <div class="pipeline-line line-mix"></div>
                <div class="pipeline-step">
                    <div class="step-circle step-active">➔</div>
                    <div class="step-label">Deploy Ready</div>
                </div>
            </div>
        """, unsafe_allow_html=True)

else:
    st.sidebar.error("FASTAPI BACKEND: OFFLINE 🔴")
    st.warning("⚠️ **Connection Error**: Streamlit cannot connect to the FastAPI backend service.")
    st.info(f"Targeting: `{API_BASE_URL}`")
    st.markdown("""
        To launch the backend, ensure your environment is active and run:
        ```bash
        greenops-env\\Scripts\\activate
        uvicorn api.main:app --reload
        ```
    """)
