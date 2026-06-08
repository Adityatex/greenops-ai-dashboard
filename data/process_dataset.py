import os
import pandas as pd
import matplotlib.pyplot as plt

def main():
    print("=== TASK A: LOAD & EXPLORE ===")
    dataset_path = 'data/cloud_usage_dataset.csv'
    
    if not os.path.exists(dataset_path):
        print(f"Error: Dataset not found at {dataset_path}")
        return
        
    df = pd.read_csv(dataset_path, parse_dates=['date'])
    
    # 2. Print shape, dtypes, and head
    print(f"\nDataset Shape: {df.shape}")
    print("\nDataset DataTypes:")
    print(df.dtypes)
    print("\nDataset Head (First 10 rows):")
    print(df.head(10))
    
    # 3. Check and handle null values
    print("\nNull Values Count:")
    nulls = df.isnull().sum()
    print(nulls)
    if nulls.sum() > 0:
        print("\nHandling missing rows...")
        # Drop rows where critical columns are null, or fill them
        df = df.dropna().reset_index(drop=True)
        print(f"Dataset Shape after dropping nulls: {df.shape}")
    else:
        print("No null values found.")
        
    # 4. Print total cost and average daily cost
    total_cost = df['cost_usd'].sum()
    # Calculate daily cost
    daily_cost_series = df.groupby('date')['cost_usd'].sum()
    avg_daily_cost = daily_cost_series.mean()
    
    print(f"\nTotal Billed Cost: ${total_cost:,.2f} USD")
    print(f"Average Daily Cost: ${avg_daily_cost:,.2f} USD")
    
    print("\n=== TASK B: CO2e CALCULATION ===")
    # 1. Create a new column co2e_kg
    # Emission Factors:
    # - CPU Compute: 0.0002 kg CO2e per CPU-hour
    # - Storage: 0.00006 kg CO2e per GB-month (divide by 30 for daily)
    # - Data Transfer: 0.001 kg CO2e per GB transferred
    df['co2e_kg'] = (df['cpu_hours'] * 0.0002) + (df['storage_gb'] * 0.00006 / 30) + (df['data_transfer_gb'] * 0.001)
    
    # 2. Print total CO2e
    total_co2e = df['co2e_kg'].sum()
    print(f"\nTotal Carbon Emissions: {total_co2e:,.4f} kg CO2e")
    
    # 3. Group by service_type and print CO2e
    print("\nCarbon Emissions by Service Type:")
    service_co2e = df.groupby('service_type')['co2e_kg'].sum().sort_values(ascending=False)
    for service, val in service_co2e.items():
        print(f" - {service}: {val:,.4f} kg CO2e")
        
    # 4. Group by team and print CO2e
    print("\nCarbon Emissions by Team:")
    team_co2e = df.groupby('team')['co2e_kg'].sum().sort_values(ascending=False)
    for team, val in team_co2e.items():
        print(f" - {team}: {val:,.4f} kg CO2e")
        
    print("\n=== TASK C: VISUALISATION ===")
    # Set modern style
    plt.style.use('seaborn-v0_8-whitegrid' if 'seaborn-v0_8-whitegrid' in plt.style.available else 'default')
    
    # 1. Plot daily CO2e over time
    plt.figure(figsize=(10, 5))
    daily_co2e = df.groupby('date')['co2e_kg'].sum().sort_index()
    plt.plot(daily_co2e.index, daily_co2e.values, color='#2ec4b6', linewidth=2.5, marker='o', markersize=4, label='Daily CO2e')
    plt.title('Daily Carbon Footprint (kg CO2e)', fontsize=14, fontweight='bold', color='#1d3557')
    plt.xlabel('Date', fontsize=12)
    plt.ylabel('CO2e (kg)', fontsize=12)
    plt.grid(True, linestyle='--', alpha=0.6)
    plt.xticks(rotation=45)
    plt.tight_layout()
    daily_chart_path = 'data/daily_co2e_chart.png'
    plt.savefig(daily_chart_path, dpi=150)
    plt.close()
    print(f"Saved daily emissions chart to {daily_chart_path}")
    
    # 2. Plot CO2e by region
    plt.figure(figsize=(8, 5))
    region_co2e = df.groupby('region')['co2e_kg'].sum().sort_values(ascending=False)
    colors = ['#1d3557', '#457b9d', '#a8dadc']
    bars = plt.bar(region_co2e.index, region_co2e.values, color=colors[:len(region_co2e)], edgecolor='grey', width=0.5)
    plt.title('Carbon Footprint by Cloud Region (kg CO2e)', fontsize=14, fontweight='bold', color='#1d3557')
    plt.xlabel('Region', fontsize=12)
    plt.ylabel('CO2e (kg)', fontsize=12)
    plt.grid(axis='y', linestyle='--', alpha=0.6)
    
    # Add labels on top of the bars
    for bar in bars:
        height = bar.get_height()
        plt.text(bar.get_x() + bar.get_width()/2., height + (height * 0.01),
                 f"{height:,.2f} kg", ha='center', va='bottom', fontsize=10, fontweight='bold')
                 
    plt.tight_layout()
    regional_chart_path = 'data/regional_co2e_chart.png'
    plt.savefig(regional_chart_path, dpi=150)
    plt.close()
    print(f"Saved regional emissions chart to {regional_chart_path}")
    
    print("\n=== TASK D: SAVE ENRICHED DATASET ===")
    enriched_path = 'data/cloud_usage_enriched.csv'
    df.to_csv(enriched_path, index=False)
    print(f"Saved enriched dataset to {enriched_path}")

if __name__ == '__main__':
    main()
