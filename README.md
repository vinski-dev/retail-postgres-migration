Retail Data Warehouse & Headless Semantic Layer

An end-to-end ELT data pipeline and governed semantic layer built for a retail dataset. This project transforms raw operational data into analytics-ready dimensional models using a Medallion architecture and exposes governed business metrics via a headless semantic layer.

🏗️ Architecture Overview

The pipeline implements a strict Medallion Architecture to progressively structure and enrich the data:

Bronze (Staging): Lightly cleansed raw data. Handles column renaming, data type casting, and null value standardization.

Silver (Intermediate): Business logic application. Resolves source anomalies, specifically utilizing window functions to deduplicate product names and maintain referential integrity.

Gold (Marts): Kimball-style dimensional modeling. Exposes a highly optimized Star Schema for downstream BI consumption.

Semantic Layer: Governed metric definitions (e.g., Total Sales, Profit Margin) built on top of the Gold layer using dbt-metricflow to ensure consistent aggregations across any BI tool.

🛠️ Tech Stack

Database: PostgreSQL

Transformation & Modeling: dbt (Data Build Tool) v1.12.6

Semantic Layer: dbt MetricFlow

Environment: Python (venv), Git Bash

📊 Data Modeling & Quality

The Gold layer resolves into a strict Star Schema to support multidimensional analysis:

fact_sales: Transactional order line-items.

dim_customers: Unique customer attributes.

dim_products: Distinct product catalog details.

metricflow_time_spine: A continuous calendar table supporting precise time-series aggregations in the semantic layer.

Data Quality: Enforced strictly via schema.yml configurations, validating uniqueness, non-null constraints, and referential integrity between the fact and dimension tables.

 (Note: Generate this via dbt docs serve and place the screenshot in an images folder)

🚀 Local Execution & Setup

1. Environment Configuration

Clone the repository and install the required dependencies:

git clone https://github.com/yourusername/retail-postgres-migration.git
cd retail-postgres-migration/dbt_retail
python -m venv venv
source venv/Scripts/activate
pip install -r requirements.txt


2. Profile Setup

Create a local profiles.yml file in the dbt_retail directory to connect to your PostgreSQL instance. (Ensure profiles.yml is added to your .gitignore!)

dbt_retail:
  target: dev
  outputs:
    dev:
      type: postgres
      host: localhost
      user: postgres
      pass: <your_password>
      port: 5432
      dbname: postgres
      schema: analytics
      threads: 4


3. Build the Data Warehouse

Run the dbt pipeline to materialize the tables and execute data quality tests:

dbt build


4. Query the Semantic Layer

Point MetricFlow to the local profile and query governed business metrics directly from the terminal:

# Export the local profile directory (required for Git Bash)
export DBT_PROFILES_DIR="."

# View monthly total sales
mf query --metrics total_sales --group-by metric_time__month

# Analyze multiple metrics by dimension
mf query --metrics total_sales,profit_margin --group-by ship_mode


🐛 Troubleshooting

Issue: MetricFlow Cannot Find Profile in Git Bash (Windows)

Error Message:
dbt.exceptions.DbtProjectError: Runtime Error Could not find profile named 'dbt_retail'

Context:
When working in Git Bash on Windows, standard dbt commands (e.g., dbt parse, dbt run) execute successfully, but mf query commands fail, stating the profile cannot be found.

Root Cause:
This occurs because Python .exe wrappers (like the mf CLI) running inside a virtual environment on Git Bash often drop inline environment variables (e.g., DBT_PROFILES_DIR="." mf query ...). When the variable is dropped, MetricFlow defaults to looking in the global Windows user directory (C:\Users\<User>\.dbt\profiles.yml) instead of the local project directory.

Resolution:
Do not pass the directory path as an inline variable. Instead, explicitly export the DBT_PROFILES_DIR variable to lock it into the active terminal session before running the MetricFlow command.

# 1. Export the path explicitly on its own line
export DBT_PROFILES_DIR="."

# 2. Run the MetricFlow command normally
mf query --metrics total_sales --group-by metric_time__month
