import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
from PIL import Image
import os

# Set page config
st.set_page_config(page_title="Sedai Flex Dashboard", layout="wide")

# Title
st.title("📊 Sedai Flex Dashboard")

# Logo with fallback
logo_path = "assets/flex_logo.png"
if os.path.exists(logo_path):
    image = Image.open(logo_path)
    st.image(image, use_container_width=True)
else:
    st.warning("⚠️ Logo not found at 'assets/flex_logo.png'. Please check the path or upload the image.")

# Sample data
df = pd.DataFrame({
    "Month": ["Jan", "Feb", "Mar", "Apr", "May"],
    "Cost": [1200, 1100, 980, 1500, 1300],
    "Savings": [200, 150, 180, 300, 250]
})

# Line chart
fig = px.line(df, x="Month", y=["Cost", "Savings"], markers=True, title="Monthly Cost vs Savings")
st.plotly_chart(fig, use_container_width=True)

# Data table
st.subheader("📋 Raw Data")
st.dataframe(df, use_container_width=True)

# Footer
st.markdown("---")
st.caption("© 2025 Sedai Flex Dashboard | Powered by Streamlit")

