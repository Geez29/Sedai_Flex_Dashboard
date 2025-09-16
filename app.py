import streamlit as st
import pandas as pd
import plotly.express as px
from PIL import Image
import os

# Set page config
st.set_page_config(page_title="Sedai Flex Dashboard", layout="wide")

# Logo from repo root, resized and centered
logo_path = "flex_logo.png"
if os.path.exists(logo_path):
    image = Image.open(logo_path)
    st.image(image, width=200, caption="Sedai Flex Logo")
else:
    st.warning("⚠️ Logo not found at 'flex_logo.png'. Please upload it to the repo root.")

# Title
st.markdown("<h1 style='text-align: center;'>📊 Sedai Flex Dashboard</h1>", unsafe_allow_html=True)

# Load data from Excel
excel_path = "sedai_execution_report_sample_v4.xlsx"
df = pd.read_excel(excel_path, sheet_name=0, engine="openpyxl")

# Filter for latest Sprint
latest_sprint = df['Sprint'].dropna().sort_values().iloc[-1]
df_latest = df[df['Sprint'] == latest_sprint]

# Aggregate cost and savings
summary = df_latest[['Current Monthly Cost ($)', 'Est. Monthly Cost ($)', 'Cost Savings in $']].sum().reset_index()
summary.columns = ['Metric', 'Amount']

# Bar chart for cost and savings
fig = px.bar(summary, x='Metric', y='Amount', title=f"Cost Summary for {latest_sprint}", text_auto=True)
st.plotly_chart(fig, use_container_width=True)

# Data table
st.subheader("📋 Raw Data for Latest Sprint")
st.dataframe(df_latest, use_container_width=True)

# Footer
st.markdown("---")
st.caption("© 2025 Sedai Flex Dashboard | FinOps")
