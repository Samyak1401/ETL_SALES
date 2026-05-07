import os
import pandas as pd
from config import *

def extract_from_csv(filename):
    """
        Extract data from a CSV file in the data folder
    """
    filepath = os.path.join(DATA_FOLDER, filename)
    try:
        if not os.path.exists(filepath):
            raise FileNotFoundError(f"File not found: {filepath}")

        # Read the CSV file
        df = pd.read_csv(filepath)
        print(f"[{get_timestamp()}] ✅ Extracted {len(df)} records from {filename}")
        print(f"   Columns: {list(df.columns)}")
        return df
    except Exception as e:
        print(e)
        raise

def extract_all_files():
    """
        Extract data from all CSV files in the data folder
    """
    try:
        # Get all CSV files
        csv_files = [f for f in os.listdir(DATA_FOLDER) if f.endswith('.csv')]

        if not csv_files:
            print(f"[{get_timestamp()}] ⚠️  No CSV files found in '{DATA_FOLDER}' folder")
            return []

        print(f"[{get_timestamp()}] Found {len(csv_files)} CSV file(s)")

        extracted_files = []
        for files in csv_files:
            df=extract_from_csv(files)
            extracted_files.append((files, df))
        return extracted_files
    except Exception as e:
        print(e)
        raise
