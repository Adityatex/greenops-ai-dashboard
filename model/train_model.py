import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import joblib
from sklearn.linear_model import LinearRegression
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_squared_error

def main():
    print("=== TASK A: FEATURE ENGINEERING ===")
    
    # 1. Load cloud_usage_enriched.csv
    enriched_path = 'data/cloud_usage_enriched.csv'
    if not os.path.exists(enriched_path):
        print(f"Error: Enriched dataset not found at {enriched_path}. Please run process_dataset.py first.")
        return
        
    df = pd.read_csv(enriched_path, parse_dates=['date'])
    
    # Aggregate to daily total CO2e
    daily = df.groupby('date')['co2e_kg'].sum().reset_index()
    daily = daily.sort_values('date').reset_index(drop=True)
    print(f"Daily aggregation created. Shape: {daily.shape}")
    
    # 2. Create lag features
    daily['lag_7'] = daily['co2e_kg'].shift(7)
    daily['lag_14'] = daily['co2e_kg'].shift(14)
    
    # 3. Create a rolling mean
    daily['rolling_7'] = daily['co2e_kg'].rolling(7).mean()
    
    # 4. Create a day-of-week feature
    daily['dow'] = daily['date'].dt.dayofweek
    
    # 5. Drop NaN rows introduced by shifting
    daily_clean = daily.dropna().reset_index(drop=True)
    print(f"Features engineered. Shape after dropping NaNs: {daily_clean.shape}")
    
    print("\n=== TASK B: TRAIN/TEST SPLIT & MODEL TRAINING ===")
    
    # 6. Use the last 30 days as the test set, everything else as training
    train_df = daily_clean.iloc[:-30]
    test_df = daily_clean.iloc[-30:]
    
    # 7. Define features and target
    features = ['lag_7', 'lag_14', 'rolling_7', 'dow']
    target = 'co2e_kg'
    
    X_train = train_df[features]
    y_train = train_df[target]
    X_test = test_df[features]
    y_test = test_df[target]
    
    print(f"Train set size: {len(X_train)} days")
    print(f"Test set size: {len(X_test)} days")
    
    # 8. Train a Linear Regression model
    lr_model = LinearRegression()
    lr_model.fit(X_train, y_train)
    print("Linear Regression model trained successfully.")
    
    # 9. Train a RandomForestRegressor (Stretch target)
    rf_model = RandomForestRegressor(n_estimators=100, random_state=42)
    rf_model.fit(X_train, y_train)
    print("Random Forest Regressor model trained successfully.")
    
    print("\n=== TASK C: EVALUATE THE MODEL ===")
    
    # 10. Predict on the test set
    y_pred_lr = lr_model.predict(X_test)
    y_pred_rf = rf_model.predict(X_test)
    
    # 11. Calculate RMSE
    rmse_lr = np.sqrt(mean_squared_error(y_test, y_pred_lr))
    rmse_rf = np.sqrt(mean_squared_error(y_test, y_pred_rf))
    
    mean_daily_emissions = daily_clean[target].mean()
    ten_percent_limit = mean_daily_emissions * 0.1
    
    print(f"Mean Daily CO2e: {mean_daily_emissions:.4f} kg")
    print(f"10% of Mean Daily CO2e: {ten_percent_limit:.4f} kg")
    print(f"Linear Regression RMSE: {rmse_lr:.4f} kg ({(rmse_lr/mean_daily_emissions)*100:.2f}% of mean)")
    print(f"Random Forest RMSE: {rmse_rf:.4f} kg ({(rmse_rf/mean_daily_emissions)*100:.2f}% of mean)")
    
    # Interpret results
    best_model_name = "Linear Regression"
    best_model = lr_model
    best_rmse = rmse_lr
    
    if rmse_rf < rmse_lr:
        best_model_name = "Random Forest"
        best_model = rf_model
        best_rmse = rmse_rf
        
    print(f"\nBest Performing Model: {best_model_name}")
    
    if best_rmse < ten_percent_limit:
        print(f"[PASS] The model error ({best_rmse:.4f} kg) is less than 10% of the mean daily emissions.")
    else:
        print(f"[WARNING] The model error ({best_rmse:.4f} kg) is greater than 10% of the mean daily emissions.")
        print("Interpretation: Adding seasonality features, regional indicators, or utilizing advanced models (ARIMA/Prophet) might help improve accuracy.")
        
    # 13. Plot actual vs predicted CO2e for the 30-day test period
    plt.figure(figsize=(10, 5))
    plt.plot(test_df['date'], y_test.values, label='Actual CO2e', color='#1d3557', linewidth=2, marker='o')
    plt.plot(test_df['date'], y_pred_lr, label=f'Linear Regression (RMSE: {rmse_lr:.4f})', color='#e63946', linestyle='--', marker='x')
    plt.plot(test_df['date'], y_pred_rf, label=f'Random Forest (RMSE: {rmse_rf:.4f})', color='#2ec4b6', linestyle=':', marker='^')
    
    plt.title('30-Day Test Period: Actual vs Predicted Carbon Emissions', fontsize=14, fontweight='bold', color='#1d3557')
    plt.xlabel('Date', fontsize=12)
    plt.ylabel('CO2e (kg)', fontsize=12)
    plt.legend(frameon=True, facecolor='white', edgecolor='lightgrey')
    plt.grid(True, linestyle='--', alpha=0.6)
    plt.xticks(rotation=45)
    plt.tight_layout()
    
    os.makedirs('model', exist_ok=True)
    plot_path = 'model/forecast_plot.png'
    plt.savefig(plot_path, dpi=150)
    plt.close()
    print(f"Saved evaluation plot to {plot_path}")
    
    print("\n=== TASK D: SAVE MODEL ARTEFACT ===")
    
    # 14. Save the trained model
    model_path = 'model/co2e_model.pkl'
    joblib.dump(best_model, model_path)
    print(f"Saved best model ({best_model_name}) to {model_path}")

if __name__ == '__main__':
    main()
