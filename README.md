# Sales Data ETL Pipeline

A small, beginner-level Data Engineering portfolio project that takes a
messy, raw sales CSV file, cleans it, loads it into a SQLite database,
and answers business questions with SQL.

## What this project does

This project builds a simple **ETL (Extract, Transform, Load) pipeline**:

```
RAW CSV  →  EXTRACT  →  CLEAN & TRANSFORM  →  LOAD INTO SQLITE  →  SQL ANALYSIS
```

1. **Extract** — read a raw sales CSV file (`data/raw_sales.csv`) with pandas.
2. **Explore** — look at the raw data to understand what's wrong with it.
3. **Transform** — clean the data: remove duplicates, fix missing values,
   standardise categories and dates, fix number formats, and calculate a
   new `total_amount` column.
4. **Load** — save the cleaned data into a SQLite database (`sales.db`).
5. **Analyse** — run SQL queries against the database to answer business
   questions (revenue, top products, monthly trends, etc.).

## Purpose of an ETL pipeline

Almost no real-world data arrives clean and ready to analyse. An ETL
pipeline is the standard pattern data engineers use to reliably turn
messy raw data into a trustworthy, structured format that other people
(analysts, dashboards, other systems) can depend on. Doing this as a
repeatable script (rather than manual one-off spreadsheet edits) means
the same process can be run again on new data, and produces the same
result every time.

## Technologies used

- **Python** — the scripting language used to write the pipeline.
- **Pandas** — used to load, explore, and clean the tabular data.
- **SQLite** — a simple, file-based relational database. No server
  setup required, which makes it perfect for a beginner project.
- **SQL** — used to query the cleaned data and answer business questions.
- **CSV** — the raw and cleaned data file format.
- **Git/GitHub** — for version control and sharing the project.

No cloud services, containers, or big-data frameworks are used — this
is intentionally kept small and beginner-friendly.

## Data quality problems in the raw data

`data/raw_sales.csv` was generated with these realistic issues on purpose,
so the cleaning step has something real to fix:

- **Duplicate rows** — the same order appearing more than once.
- **Missing values** — blank `customer_name`, `category`, `quantity`, or
  `unit_price` fields.
- **Inconsistent category capitalization** — e.g. `Electronics`,
  `electronics`, `ELECTRONICS `.
- **Multiple date formats** — e.g. `2024-01-05`, `05/01/2024`, `05 Jan 2024`.
- **Numbers stored as text** — e.g. `" 3 "` for quantity or `"$10.36 "`
  for unit_price, which cannot be used in maths until converted.

## Data cleaning performed

All of the cleaning logic lives in the `transform()` function in
`pipeline.py`:

1. Removed exact duplicate rows.
2. Standardised `category` values to a consistent Title Case format
   (e.g. `ELECTRONICS ` → `Electronics`).
3. Converted `quantity` and `unit_price` from text to real numbers,
   stripping stray spaces and `$` signs first.
4. Parsed every date format explicitly (rather than letting pandas
   guess) and converted all dates to a single consistent
   `YYYY-MM-DD` format.
5. Filled missing `customer_name` values with `"Unknown Customer"` and
   missing `category` values with `"Uncategorized"`, and dropped rows
   still missing a required numeric value (`quantity`, `unit_price`) or
   a valid `order_date`, since those rows can't be reliably calculated
   or analysed.
6. Calculated a new column: `total_amount = quantity * unit_price`.

The cleaned result is saved to `data/cleaned_sales.csv`.

## Database structure

A single SQLite database, `sales.db`, with one table:

```sql
CREATE TABLE sales (
    order_id       INTEGER PRIMARY KEY,
    order_date     TEXT NOT NULL,
    customer_name  TEXT NOT NULL,
    product        TEXT NOT NULL,
    category       TEXT NOT NULL,
    quantity       INTEGER NOT NULL,
    unit_price     REAL NOT NULL,
    total_amount   REAL NOT NULL
);
```

`order_id` is used as the **primary key** because each order has a
unique ID, and a primary key guarantees no two rows can have the same
one — a good fit for uniquely identifying each row/order.

A single flat table is enough for this project's scope. In a larger,
more "real" system you might split this into separate `customers`,
`products`, and `orders` tables (this is called **normalization**), but
that adds complexity that isn't necessary for a small, beginner-level
pipeline like this one.

## SQL analysis

`analysis.sql` contains six queries, each answering a simple business
question:

1. **Total revenue** — `SUM(total_amount)` across all orders.
2. **Total number of orders** — `COUNT(*)` of rows in the table.
3. **Average order value** — `AVG(total_amount)`.
4. **Top-selling product** — the product with the highest total
   `quantity` sold, using `GROUP BY` + `ORDER BY ... DESC LIMIT 1`.
5. **Highest-revenue category** — the category with the highest total
   `total_amount`, using the same `GROUP BY` pattern.
6. **Monthly revenue** — revenue grouped by year and month, using
   `substr(order_date, 1, 7)` to extract the `YYYY-MM` part of each date.

Each query in the file has a comment above it explaining what it does
and why.

## How to run this project

1. Clone the repository and move into the project folder.
2. Install the one dependency:

   ```bash
   pip install -r requirements.txt
   ```

3. (Optional) Look at the raw data first:

   ```bash
   python explore_data.py
   ```

4. Run the whole pipeline (extract → transform → load):

   ```bash
   python pipeline.py
   ```

   This will:
   - Read `data/raw_sales.csv`
   - Clean it and save `data/cleaned_sales.csv`
   - Create/refresh `sales.db` with the cleaned data

5. Explore the results with SQL, e.g. using the built-in `sqlite3`
   command-line tool:

   ```bash
   sqlite3 sales.db
   sqlite> .read analysis.sql
   ```

   Or open `sales.db` in a free GUI tool like
   [DB Browser for SQLite](https://sqlitebrowser.org/).

(Note: `data/raw_sales.csv` is already included in this repo. It was
originally generated by `generate_raw_data.py`, which is included for
transparency but does not need to be re-run.)

## Example results

Running `analysis.sql` against the included data produces results like:

| Question | Example result |
|---|---|
| Total revenue | $34,234.86 |
| Total orders | 346 |
| Average order value | $98.94 |
| Top-selling product | Mechanical Keyboard |
| Highest-revenue category | Home |
| Monthly revenue | Jan: $5,857.86 → Jun: $6,234.76 |

(Exact numbers will differ slightly if you regenerate the raw data.)

## What was learned

- How to structure a small ETL pipeline as clear, separate steps
  (extract, transform, load) rather than one big messy script.
- Why raw, real-world data almost always needs cleaning before it can
  be trusted, and specific techniques for common problems: duplicates,
  missing values, inconsistent text formatting, and numbers stored as
  text.
- Why guessing date formats automatically can be risky (e.g.
  `07/02/2024` could mean 7 February or July 2nd) and why explicitly
  trying known formats is safer.
- How to design a simple relational table and choose a sensible primary
  key.
- How to load a pandas DataFrame into a SQLite database with
  `to_sql()`.
- How to write basic aggregate SQL queries (`SUM`, `COUNT`, `AVG`,
  `GROUP BY`, `ORDER BY`) to answer real business questions.

## Project structure

```
sales-data-pipeline/
│
├── data/
│   ├── raw_sales.csv        # messy raw input data
│   └── cleaned_sales.csv    # cleaned output data
│
├── generate_raw_data.py     # one-off script that created the raw CSV
├── explore_data.py          # Step 1: data exploration (read-only)
├── pipeline.py               # main ETL pipeline (extract, transform, load)
├── analysis.sql              # Step 5: SQL analysis queries
├── sales.db                  # SQLite database (output of the pipeline)
├── requirements.txt
├── README.md
└── .gitignore
```
