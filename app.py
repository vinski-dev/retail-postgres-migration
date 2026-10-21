import streamlit as st
import subprocess
import pandas as pd
import os

st.title("Retail Performance Dashboard")
st.markdown("Powered by dbt & MetricFlow Semantic Layer")

# 1. Let the user choose how to slice the metrics
dimension = st.selectbox("Slice Total Sales By:", ("metric_time__year", "order_id__ship_mode"))

csv_filename = "temp_metrics.csv"
csv_path = os.path.join("dbt_retail", csv_filename)

with st.spinner(f"Querying MetricFlow for {dimension}..."):
    cmd = ["mf", "query", "--metrics", "total_sales", "--group-by", dimension, "--csv", csv_filename]

    # 2. Force the MetricFlow subprocess to use UTF-8 internally
    custom_env = os.environ.copy()
    custom_env["PYTHONIOENCODING"] = "utf-8"

    # 3. Run the command with the custom environment
    result = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8", cwd="dbt_retail", env=custom_env)

# 4. Render the results
if result.returncode == 0 and os.path.exists(csv_path):
    df = pd.read_csv(csv_path)

    col1, col2 = st.columns(2)

    with col1:
        st.subheader("Semantic Layer Output")
        st.dataframe(df, hide_index=True, use_container_width=True)

    with col2:
        st.subheader("Visualization")
        st.bar_chart(data=df, x=dimension, y="total_sales")

    # Clean up the temporary file
    os.remove(csv_path)

else:
    st.error("Semantic Layer Error:")
    st.code(result.stderr or result.stdout)
