import os
import io
import pandas as pd
import joblib
from fastapi import FastAPI, HTTPException
from dotenv import load_dotenv
from azure.storage.blob import BlobServiceClient

# Load environment variables
load_dotenv()

app = FastAPI(
    title="GreenOps API",
    description="REST API for cloud carbon emissions baseline, forecasting, and sustainability scoring.",
    version="1.0.0"
)

# Helper function to load dataset from Azure Blob Storage or fallback to local CSV
def load_data():
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
            return df
        except Exception as e:
            print(f"Error reading from Azure Blob: {e}. Falling back to local file.")
            
    # Fallback to local
    dataset_path = os.getenv("DATASET_PATH", "data/cloud_usage_enriched.csv")
    if not os.path.exists(dataset_path):
        raise HTTPException(status_code=500, detail=f"Dataset not found at {dataset_path}")
    return pd.read_csv(dataset_path, parse_dates=['date'])

# Helper function to load forecasting model
def load_model():
    model_path = os.getenv("MODEL_PATH", "model/co2e_model.pkl")
    if not os.path.exists(model_path):
        raise HTTPException(status_code=500, detail=f"Model artifact not found at {model_path}. Please train the model first.")
    return joblib.load(model_path)

@app.get('/health')
def health():
    """
    Liveness probe. Returns OK if the API is running.
    """
    return {"status": "ok"}

@app.get('/metrics/summary')
def get_metrics_summary():
    """
    Returns total CO2e (kg), total cost (USD), and highest emitting team and region.
    """
    try:
        df = load_data()
        total_co2e = float(df['co2e_kg'].sum())
        total_cost = float(df['cost_usd'].sum())
        
        # Find top emitting team
        team_emissions = df.groupby('team')['co2e_kg'].sum()
        top_team = str(team_emissions.idxmax()) if not team_emissions.empty else "N/A"
        
        # Find top emitting region
        region_emissions = df.groupby('region')['co2e_kg'].sum()
        top_region = str(region_emissions.idxmax()) if not region_emissions.empty else "N/A"
        
        return {
            "total_co2e_kg": round(total_co2e, 4),
            "total_cost_usd": round(total_cost, 2),
            "top_emitting_team": top_team,
            "top_emitting_region": top_region
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get('/metrics/daily')
def get_metrics_daily():
    """
    Returns a daily array of dates and carbon emissions (kg CO2e) for trend charting.
    """
    try:
        df = load_data()
        daily = df.groupby('date')['co2e_kg'].sum().reset_index()
        daily = daily.sort_values('date')
        
        # Format dates as strings
        daily['date'] = daily['date'].dt.strftime('%Y-%m-%d')
        return daily.to_dict(orient='records')
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get('/forecast')
def get_forecast():
    """
    Performs recursive time-series forecasting for the next 30 days and returns predicted daily emissions.
    """
    try:
        df = load_data()
        model = load_model()
        
        # Sort and aggregate daily total CO2e
        daily = df.groupby('date')['co2e_kg'].sum().sort_index().reset_index()
        
        history = daily.copy()
        predictions = []
        last_date = history['date'].max()
        
        # Forecast 30 days recursively
        for i in range(1, 31):
            forecast_date = last_date + pd.Timedelta(days=i)
            
            # Fetch lags and rolling mean from rolling history
            lag_7_val = float(history.iloc[-7]['co2e_kg'])
            lag_14_val = float(history.iloc[-14]['co2e_kg'])
            rolling_7_val = float(history.iloc[-7:]['co2e_kg'].mean())
            dow_val = int(forecast_date.dayofweek)
            
            # Predict
            features = [[lag_7_val, lag_14_val, rolling_7_val, dow_val]]
            pred_co2e = float(model.predict(features)[0])
            
            # Append new predicted value to history for recursive future lags
            new_row = pd.DataFrame({
                'date': [forecast_date],
                'co2e_kg': [pred_co2e]
            })
            history = pd.concat([history, new_row], ignore_index=True)
            
            predictions.append({
                "date": forecast_date.strftime('%Y-%m-%d'),
                "predicted_co2e": round(pred_co2e, 4)
            })
            
        return predictions
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get('/green-score')
def get_green_score():
    """
    Calculates the average daily CO2e from the dataset, assigns a letter grade (A-F),
    and suggests a pipeline gate verdict (PASS, WARNING, BLOCKED).
    """
    try:
        df = load_data()
        daily_emissions = df.groupby('date')['co2e_kg'].sum()
        avg_daily_co2e = float(daily_emissions.mean())
        
        # Scoring Criteria
        if avg_daily_co2e < 2.0:
            grade = "A"
            action = "Excellent - no action needed"
            gate = "PASS"
        elif avg_daily_co2e < 5.0:
            grade = "B"
            action = "Good - minor optimisation advised"
            gate = "PASS"
        elif avg_daily_co2e < 10.0:
            grade = "C"
            action = "Moderate - review VM sizing"
            gate = "PASS"
        elif avg_daily_co2e < 20.0:
            grade = "D"
            action = "Poor - immediate rightsizing required"
            gate = "WARNING"
        else:
            grade = "F"
            action = "Critical - pipeline soft gate triggered"
            gate = "BLOCKED"
            
        return {
            "grade": grade,
            "avg_daily_co2e": round(avg_daily_co2e, 4),
            "action": action,
            "gate": gate
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
