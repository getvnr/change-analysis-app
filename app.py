import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime, timedelta

st.set_page_config(page_title="Weekend Change Analyzer", page_icon="🧭", layout="wide")

st.title("🧭 Middleware Weekend Change Analyzer")
st.write("Upload your CSV or Excel file (copied from Excel) to analyze change activities for this weekend.")

# Upload CSV/Excel file
uploaded_file = st.file_uploader("📂 Upload CSV or Excel", type=["csv", "xlsx"])

if uploaded_file:
    # Read data
    if uploaded_file.name.endswith(".csv"):
        df = pd.read_csv(uploaded_file, sep=None, engine="python")
    else:
        df = pd.read_excel(uploaded_file)

    # Clean column names
    df.columns = [col.strip() for col in df.columns]

    # Convert Start and End Date columns
    for col in ["Start Date", "End Date"]:
        df[col] = pd.to_datetime(df[col], errors="coerce", dayfirst=True)

    # Show raw data
    st.subheader("📋 Raw Change Data")
    st.dataframe(df)

    # Add calculated fields
    df["Duration (hrs)"] = (df["End Date"] - df["Start Date"]).dt.total_seconds() / 3600
    df["Day"] = df["Start Date"].dt.day_name()

    # --- Filter: Changes for upcoming weekend ---
    today = datetime.now()
    next_friday = today + timedelta((4 - today.weekday()) % 7)
    next_monday = next_friday + timedelta(days=2)

    weekend_df = df[
        (df["Start Date"].dt.date >= next_friday.date())
        & (df["Start Date"].dt.date <= next_monday.date())
    ]

    st.subheader(f"🗓️ Changes Scheduled for Weekend ({next_friday.strftime('%b %d')} - {next_monday.strftime('%b %d')})")
    if weekend_df.empty:
        st.warning("No changes found for this weekend.")
    else:
        st.dataframe(weekend_df)

    # --- Summary: Number of Changes per Customer ---
    st.subheader("📊 Number of Changes per Customer")
    customer_summary = df.groupby("Customer")["Change"].nunique().reset_index()
    customer_summary.columns = ["Customer", "Number of Changes"]
    st.dataframe(customer_summary)

    fig, ax = plt.subplots()
    ax.bar(customer_summary["Customer"], customer_summary["Number of Changes"], color="skyblue")
    ax.set_xlabel("Customer")
    ax.set_ylabel("Number of Changes")
    ax.set_title("Changes by Customer")
    st.pyplot(fig)

    # --- Summary: Changes by Status ---
    st.subheader("📈 Changes by Status")
    status_summary = df.groupby("Status")["Change"].nunique().reset_index()
    status_summary.columns = ["Status", "Number of Changes"]
    st.dataframe(status_summary)

    # --- Duration Summary ---
    st.subheader("⏱️ Average Duration per Customer (in Hours)")
    duration_summary = df.groupby("Customer")["Duration (hrs)"].mean().reset_index()
    duration_summary.columns = ["Customer", "Avg Duration (hrs)"]
    st.dataframe(duration_summary)

else:
    st.info("👆 Upload your file to begin analysis.")
