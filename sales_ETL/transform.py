import pandas as pd
from datetime import datetime
import os
from config import *

def transform_data(df):
    """
        Clean, validate, and transform the raw sales data
    """
    try:
        print(f"[{get_timestamp()}] 🔄 Starting data transformation...")

        # Make a copy to avoid modifying original data
        df_copy = df.copy()
        # === 1. Basic Cleaning ===
        # Remove completely empty rows
        df_copy.dropna(how='all', axis=1, inplace=True)

        # Remove duplicate rows
        initial_rows = len(df)
        df_copy.drop_duplicates(inplace=True)
        print(f"   Removed {initial_rows - len(df_copy)} duplicate rows")

        # === 2. Data Type Conversion ===
        # Convert Date to datetime
        df_copy['Date'] = pd.to_datetime(df_copy['Date'])

        df_copy['Quantity'] = pd.to_numeric(df_copy['Quantity'])
        df_copy['Amount'] = pd.to_numeric(df_copy['Amount'])

        # === 3. Handle Missing Values ===
        # Fill missing Quantity and Amount with median
        df_copy['Quantity'] = df_copy['Quantity'].fillna(
            df_copy['Quantity'].median()
        )

        df_copy['Amount'] = df_copy['Amount'].fillna(
            df_copy['Amount'].median()
        )

        # Drop rows where Date is missing (critical field)
        df_copy.dropna(subset=['Date'], inplace=True)

        # === 4. Feature Engineering ===
        # Create new useful columns
        df_copy['Total_Amount'] = df_copy['Quantity'] * df_copy['Amount']
        df_copy['Year'] = df_copy['Date'].dt.year
        df_copy['Month'] = df_copy['Date'].dt.month
        df_copy['Day'] = df_copy['Date'].dt.day

        # Create Sales Category
        df_copy['Sales_Category'] = df_copy['Total_Amount'].apply(
            lambda x: 'High' if x > 50000 else
            'Medium' if x > 10000 else 'Low'
        )

        # === 5. Final Validation ===
        print(f"[{get_timestamp()}] ✅ Transformation completed!")
        print(f"   Final records: {len(df_copy)}")
        print(f"   Columns: {list(df_copy.columns)}")

        return df_copy

    except Exception as e:
        print(f"[{get_timestamp()}] ❌ Transformation failed: {e}")
        raise
