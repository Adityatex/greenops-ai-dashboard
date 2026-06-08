import os
import io
import pandas as pd
from dotenv import load_dotenv
from azure.storage.blob import BlobServiceClient

def main():
    # Load environment variables from .env
    load_dotenv()
    
    conn_str = os.getenv("AZURE_STORAGE_CONNECTION_STRING")
    if not conn_str:
        print("Error: AZURE_STORAGE_CONNECTION_STRING is not set in environment or .env file.")
        print("Please write your Azure Connection String inside a '.env' file in the root of the project:")
        print("AZURE_STORAGE_CONNECTION_STRING=\"your_actual_connection_string_here\"")
        return
        
    print("Connecting to Azure Blob Storage...")
    try:
        blob_service_client = BlobServiceClient.from_connection_string(conn_str)
        container_name = "greenops-data"
        blob_name = "cloud_usage_enriched.csv"
        
        container_client = blob_service_client.get_container_client(container_name)
        blob_client = container_client.get_blob_client(blob_name)
        
        print(f"Downloading '{blob_name}' from container '{container_name}'...")
        data = blob_client.download_blob().readall()
        
        # Load into pandas DataFrame
        df = pd.read_csv(io.BytesIO(data))
        
        print("\n=== VERIFICATION SUCCESSFUL ===")
        print(f"Dataset Shape: {df.shape}")
        print(f"Total Carbon Footprint: {df['co2e_kg'].sum():,.4f} kg CO2e")
        print("\nEmissions by Region:")
        region_emissions = df.groupby('region')['co2e_kg'].sum().sort_values(ascending=False)
        for region, emissions in region_emissions.items():
            print(f" - {region}: {emissions:,.4f} kg CO2e")
            
    except Exception as e:
        print(f"An error occurred while connecting or downloading: {e}")

if __name__ == "__main__":
    main()
