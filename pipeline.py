"""

This is the main ETL (Extract, Transform, Load) pipeline for the
Sales Data project.

Running this single file end-to-end does three things:

1. EXTRACT  - read the raw, messy sales data from data/raw_sales.csv
2. TRANSFORM - clean it and save the result to data/cleaned_sales.csv
3. LOAD     - load the cleaned data into a SQLite database (sales.db)

Run it from the project's root folder with:

    python pipeline.py

Each step below is written as its own function and explained with
comments, so you can read this file top-to-bottom like a tutorial.
"""

import sqlite3
import pandas as pd


RAW_CSV_PATH = "data/raw_sales.csv"
CLEANED_CSV_PATH = "data/cleaned_sales.csv"
DATABASE_PATH = "sales.db"

def extract(csv_path: str) -> pd.DataFrame:
    """
    Reads the raw CSV file into a pandas DataFrame.

    WHY: Extraction is the first stage of any ETL pipeline. Before we can
    clean or analyse anything, we need to load the raw data into memory
    in a structure we can work with — a pandas DataFrame is basically a
    table (rows and columns) that lives in Python.
    """
    print(f"[EXTRACT] Reading raw data from '{csv_path}'...")
    df = pd.read_csv(csv_path)
    print(f"[EXTRACT] Loaded {len(df)} rows and {len(df.columns)} columns.")
    return df

def explore(df: pd.DataFrame) -> None:
    """
    Prints a quick summary of the DataFrame: shape, missing values,
    duplicates, and data types.

    WHY: Before cleaning data, a data engineer always inspects it first.
    You cannot write good cleaning logic until you understand what is
    actually wrong with the data.
    """
    print("\n--- First 5 rows ---")
    print(df.head())

    print("\n--- Shape (rows, columns) ---")
    print(df.shape)

    print("\n--- Missing values per column ---")
    print(df.isnull().sum())

    print("\n--- Duplicate rows ---")
    print(f"{df.duplicated().sum()} duplicate rows found")

    print("\n--- Data types ---")
    print(df.dtypes)

    print("\n--- Summary statistics ---")
    print(df.describe(include="all"))

def transform(df: pd.DataFrame) -> pd.DataFrame:
    """
    Cleans the raw DataFrame and returns a new, clean DataFrame.

    WHY: Raw data almost always has quality problems (duplicates, missing
    values, inconsistent formatting). If we load dirty data straight into
    a database, every query and report built on top of it will be wrong.
    Cleaning is where a data engineer adds most of their value.
    """
    print("\n[TRANSFORM] Cleaning data...")

    clean_df = df.copy()

 
    before = len(clean_df)
    clean_df = clean_df.drop_duplicates()
    print(f"  - Removed {before - len(clean_df)} duplicate rows.")

    clean_df["category"] = (
        clean_df["category"]
        .astype(str)
        .str.strip()
        .str.title()
    )

    clean_df["category"] = clean_df["category"].replace("Nan", pd.NA)

    clean_df["quantity"] = (
        clean_df["quantity"]
        .astype(str)
        .str.strip()
        .str.replace("$", "", regex=False)
    )
    clean_df["quantity"] = pd.to_numeric(clean_df["quantity"], errors="coerce")

    clean_df["unit_price"] = (
        clean_df["unit_price"]
        .astype(str)
        .str.strip()
        .str.replace("$", "", regex=False)
    )
    clean_df["unit_price"] = pd.to_numeric(clean_df["unit_price"], errors="coerce")

   
    known_date_formats = ["%Y-%m-%d", "%d/%m/%Y", "%m-%d-%Y", "%d %b %Y"]

    def parse_known_date(value):
        for fmt in known_date_formats:
            parsed = pd.to_datetime(value, format=fmt, errors="coerce")
            if pd.notna(parsed):
                return parsed
        return pd.NaT

    clean_df["order_date"] = clean_df["order_date"].apply(parse_known_date)
    clean_df["order_date"] = clean_df["order_date"].dt.strftime("%Y-%m-%d")

    
    clean_df["customer_name"] = clean_df["customer_name"].fillna("Unknown Customer")


    clean_df["category"] = clean_df["category"].fillna("Uncategorized")

    before = len(clean_df)
    clean_df = clean_df.dropna(subset=["quantity", "unit_price", "order_date"])
    print(f"  - Dropped {before - len(clean_df)} rows with missing "
          f"quantity, unit_price, or order_date.")

  
    clean_df["quantity"] = clean_df["quantity"].astype(int)

   
    clean_df["total_amount"] = (clean_df["quantity"] * clean_df["unit_price"]).round(2)

    clean_df = clean_df.reset_index(drop=True)

    print(f"[TRANSFORM] Cleaning complete. {len(clean_df)} clean rows remain.")
    return clean_df

