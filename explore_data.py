import pandas as pd
from pipeline import extract, explore, RAW_CSV_PATH

if __name__ == "__main__":
    df = extract(RAW_CSV_PATH)
    explore(df)
