import pandas as pd
from sqlalchemy import create_engine, text
import kagglehub
import os
import shutil
import uuid
from dotenv import load_dotenv  # <-- Add this

# Load environment variables from the .env file automatically
load_dotenv()


# ---------------------------------------------------------
# 1. Structural Helper
# ---------------------------------------------------------
def clean_column_names(df: pd.DataFrame) -> pd.DataFrame:
    df.columns = (
        df.columns.str.strip()
        .str.lower()
        .str.replace(r"[^a-z0-9_]", "_", regex=True)
        .str.replace(r"_+", "_", regex=True)
    )
    return df


# ---------------------------------------------------------
# 2. Main Execution
# ---------------------------------------------------------
def main():
    db_url = os.getenv("POSTGRES_URL", "postgresql://user:pass@localhost:5432/retail_db")
    engine = create_engine(db_url)

    # --- NEW: Ensure Schema Exists Automatically ---
    with engine.connect() as conn:
        conn.execute(text("CREATE SCHEMA IF NOT EXISTS raw_data;"))
        conn.commit()
    print("Verified 'raw_data' schema exists.")

    input_dir = "input"
    os.makedirs(input_dir, exist_ok=True)

    batch_id = str(uuid.uuid4())
    loaded_at = pd.Timestamp.utcnow()
    print(f"Starting ingestion run. Batch ID: {batch_id}")

    print("Extracting Superstore dataset from Kaggle...")
    dataset_path = kagglehub.dataset_download("vivek468/superstore-dataset-final")

    csv_files = [f for f in os.listdir(dataset_path) if f.endswith(".csv")]
    if not csv_files:
        raise FileNotFoundError("No CSV files found.")

    raw_cached_path = os.path.join(dataset_path, csv_files[0])
    raw_local_path = os.path.join(input_dir, "raw_superstore.csv")
    shutil.copy(raw_cached_path, raw_local_path)

    print("Applying structural types and audit metadata...")
    raw_orders = (
        pd.read_csv(raw_local_path, encoding="unicode_escape")
        .pipe(clean_column_names)
        .assign(
            order_date=lambda x: pd.to_datetime(x["order_date"], format="mixed", errors="coerce"),
            ship_date=lambda x: pd.to_datetime(x["ship_date"], format="mixed", errors="coerce"),
            sales=lambda x: pd.to_numeric(x["sales"], errors="coerce"),
            quantity=lambda x: pd.to_numeric(x["quantity"], errors="coerce"),
            _batch_id=batch_id,
            _loaded_at=loaded_at,
        )
    )

    clean_local_path = os.path.join(input_dir, "db_ready_superstore.csv")
    raw_orders.to_csv(clean_local_path, index=False)

    print(f"Loading {raw_orders.shape[0]} raw rows to PostgreSQL...")
    try:
        raw_orders.to_sql(
            name="raw_superstore_orders",
            con=engine,
            schema="raw_data",
            if_exists="replace",
            index=False,
            method="multi",
            chunksize=10000,
        )
        print("Successfully landed 1:1 raw data into PostgreSQL 'raw_data' schema.")

    except Exception as e:
        print(f"Failed to load data to PostgreSQL: {e}")


if __name__ == "__main__":
    main()
