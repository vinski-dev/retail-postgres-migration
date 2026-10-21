import os
import kagglehub
from kagglehub import KaggleDatasetAdapter
import pandas as pd
import kagglehub
from sqlalchemy import create_engine, text
from sqlalchemy.engine import URL  # <-- Import the URL builder
from dotenv import load_dotenv

# Load variables from the .env file
load_dotenv()

# Safely construct the URL (handles special characters in passwords)
db_url = URL.create(
    drivername="postgresql",
    username=os.getenv("DB_USER"),
    password=os.getenv("DB_PASSWORD"),
    host=os.getenv("DB_HOST"),
    port=os.getenv("DB_PORT"),
    database=os.getenv("DB_NAME"),
)

engine = create_engine(db_url)


def setup_database():
    """Ensure the raw_data schema exists before loading."""
    with engine.connect() as conn:
        conn.execute(text("CREATE SCHEMA IF NOT EXISTS raw_data;"))
        conn.commit()
    print("Database schema 'raw_data' is ready.")


# 2. Superstore Ingestion Module
def ingest_superstore():
    """Ingest the original Superstore dataset from a local file."""
    # Update this path to where your Superstore CSV actually lives
    superstore_path = "data/superstore.csv"
    table_name = "raw_superstore_orders"

    if os.path.exists(superstore_path):
        print(f"Ingesting Superstore into raw_data.{table_name}...")
        df = pd.read_csv(superstore_path)

        # Standardize column names (optional but recommended before dbt)
        df.columns = [col.lower().replace(" ", "_").replace("-", "_") for col in df.columns]

        df.to_sql(name=table_name, con=engine, schema="raw_data", if_exists="replace", index=False, chunksize=10000)
    else:
        print(f"Skipped: Superstore file not found at {superstore_path}")


# 3. Olist Kaggle Ingestion Module
def ingest_olist():
    """Download and ingest the Brazilian E-Commerce dataset directly."""
    print("Downloading dataset to local cache...")
    dataset_path = kagglehub.dataset_download("olistbr/brazilian-ecommerce")

    files_to_load = {
        "olist_orders_dataset.csv": "olist_orders",
        "olist_order_reviews_dataset.csv": "olist_reviews",
        "olist_order_items_dataset.csv": "olist_order_items",
        "olist_products_dataset.csv": "olist_products",
        "olist_customers_dataset.csv": "olist_customers",
    }

    # Search the cache for the exact files
    found_files = {}
    for root, dirs, files in os.walk(dataset_path):
        for file in files:
            if file in files_to_load:
                found_files[file] = os.path.join(root, file)

    for file_name, table_name in files_to_load.items():
        if file_name in found_files:
            file_path = found_files[file_name]
            print(f"Ingesting {file_name} into raw_data.{table_name}...")
            try:
                # Engine='python' and on_bad_lines='skip' prevent the tokenizing crash
                df = pd.read_csv(file_path, engine="python", on_bad_lines="skip", encoding="utf-8")

                df.to_sql(
                    name=table_name, con=engine, schema="raw_data", if_exists="replace", index=False, chunksize=10000
                )
            except Exception as e:
                print(f"Failed to load {file_name}: {e}")
        else:
            print(f"Skipped: {file_name} not found.")


if __name__ == "__main__":
    print("Starting data ingestion pipeline...")
    setup_database()
    ingest_olist()
    print("Pipeline complete. Raw data is safely loaded in the raw_data schema.")

# 4. Main Pipeline Execution
if __name__ == "__main__":
    print("Starting data ingestion pipeline...")
    setup_database()

    # Run the ingestion modules sequentially
    # ingest_superstore()
    ingest_olist()

    print("Pipeline complete. All raw data is safely loaded in the raw_data schema.")
