from sqlalchemy import create_engine, text
from config import *
import pandas as pd

def get_engine():
    """Create database connection engine"""
    try:
        conn_str = f"postgresql+psycopg2://{DB_CONFIG['user']}:{DB_CONFIG['password']}@{DB_CONFIG['host']}:{DB_CONFIG['port']}/{DB_CONFIG['database']}"
        engine = create_engine(conn_str)
        return engine

    except Exception as e:
        print(f"[{get_timestamp()}] ❌ Failed to create database engine: {e}")
    raise
def get_snowflake_engine():
    """Create snowflake connection engine"""
    try:
        conn = f"snowflake://{SF_CONFIG['user']}:{SF_CONFIG['password']}@{SF_CONFIG['account']}/{SF_CONFIG['database']}/{SF_CONFIG['schema']}?warehouse={SF_CONFIG['warehouse']}&role={SF_CONFIG['role']}"
        engine = create_engine(conn)
        return engine
    except Exception as e:
        print(f"[{get_timestamp()}] ❌ Failed to create database engine: {e}")
        raise

def create_table_if_not_exists(engine):
    """Create the sales_data table if it doesn't exist"""
    create_table_query = """
    CREATE TABLE IF NOT EXISTS sales_data (
        OrderID BIGINT PRIMARY KEY,
        Date DATE,
        Product VARCHAR(255),
        Category VARCHAR(100),
        Quantity FLOAT,
        Amount FLOAT,
        CustomerID VARCHAR(50),
        Region VARCHAR(100),
        Total_Amount FLOAT,
        Year INTEGER,
        Month INTEGER,
        Day INTEGER,
        Sales_Category VARCHAR(50)
    );
    """
    try:
        with engine.connect() as conn:
            conn.execute(text(create_table_query))
            conn.commit()
        print(f"[{get_timestamp()}] ✅ Table 'sales_data' is ready")
    except Exception as e:
        print(f"[{get_timestamp()}] ⚠️  Could not create table: {e}")

def load_to_postgres(df,table_name="sales_data"):
    """
        Load transformed DataFrame into PostgreSQL database
    """
    try:
        engine = get_engine()

        # Create table if it doesn't exist
        create_table_if_not_exists(engine)
        # Read existing OrderIDs
        query = 'SELECT "OrderID" FROM sales_data'

        existing_ids = pd.read_sql(query, engine)

        # Keep only new records
        new_df = df[
            ~df['OrderID'].isin(existing_ids['OrderID'])
        ]
        if new_df.empty:
            print("⚠️ No new records to insert.")
            return

        # Load data into database
        new_df.to_sql(
            name=table_name,
            con=engine,
            if_exists='append',
            index=False,
            method='multi'  # Faster loading for multiple rows
        )
        print(f"[{get_timestamp()}] ✅ Successfully loaded {len(df)} records into '{table_name}' table")
        with engine.connect() as conn:
            result = conn.execute(text(f"SELECT COUNT(*) FROM {table_name}"))
            total_records = result.scalar()
            print(f"   Total records in database now: {total_records}")
    except Exception as e:
        print(f"[{get_timestamp()}] ❌ Load failed: {e}")
        raise

def load_to_snowflake(df,table_name="sales_data"):
    """
           Load transformed DataFrame into PostgreSQL database
    """
    try:

        engine = get_snowflake_engine()
        print("Connected to database")
        # Create table if it doesn't exist
        create_table_if_not_exists(engine)
        # Read existing OrderIDs
        query = 'SELECT "ORDERID" FROM SALES_DATA'

        existing_ids = pd.read_sql(query, engine)

        # Keep only new records
        new_df = df[
            ~df['OrderID'].isin(existing_ids.iloc[:, 0])
        ]
        if new_df.empty:
            print("⚠️ No new records to insert.")
            return

        new_df.columns = [col.upper() for col in new_df.columns]
        # Load data into database
        new_df.to_sql(
            name=table_name,
            con=engine,
            if_exists='append',
            index=False,
            method='multi'  # Faster loading for multiple rows
        )
        print(f"[{get_timestamp()}] ✅ Successfully loaded {len(df)} records into '{table_name}' table")
        with engine.connect() as conn:
            result = conn.execute(text(f"SELECT COUNT(*) FROM {table_name}"))
            total_records = result.scalar()
            print(f"   Total records in database now: {total_records}")
    except Exception as e:
        print(f"[{get_timestamp()}] ❌ Load failed: {e}")
        raise


