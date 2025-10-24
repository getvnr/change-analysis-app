import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

st.set_page_config(page_title="Weekend Change Analyzer", page_icon="🧭", layout="wide")

st.title("🧭 Middleware Change Analyzer")
st.write("Upload a CSV or Excel file with your change data to analyze weekend activities.")

# File upload
uploaded_file = st.file_uploader("📂 Upload CSV or Excel file", type=["csv", "xlsx"])

if uploaded_file:
    # Read CSV or Excel
    if uploaded_file.name.endswith(".csv"):
        df = pd.read_csv(uploaded_file, sep=None, engine="python")
    else:
        df = pd.read_excel(uploaded_file)

    # Clean column names
    df.columns = [c.strip() for c in df.columns]

    # Convert Start and End Dates
    for col in ["Start Date", "End Date"]:
        df[col] = pd.to_datetime(df[col], errors="coerce", dayfirst=True)

    # Show full dataset
    st.subheader("📋 Raw Data")
    st.dataframe(df)

    # Duration calculation
    df["Duration (hrs)"] = (df["End Date"] - df["Start Date"]).dt.total_seconds() / 3600

    # Weekend filter
    df["Start Day"] = df["Start Date"].dt.day_name()
    weekend_df = df[df["Start Day"].isin(["Friday", "Saturday", "Sunday"])]

    st.subheader("🗓️ Weekend Changes (Fri–Sun)")
    st.dataframe(weekend_df)

    # --- Number of changes per Customer ---
    st.subheader("📊 Changes per Customer")
    customer_summary = df.groupby("Customer")["Change"].nunique().reset_index()
    customer_summary.columns = ["Customer", "Number of Changes"]
    st.dataframe(customer_summary)

    # Plot: Changes by Customer
    fig, ax = plt.subplots()
    ax.bar(customer_summary["Customer"], customer_summary["Number of Changes"])
    ax.set_xlabel("Customer")
    ax.set_ylabel("Number of Changes")
    ax.set_title("Changes by Customer")
    st.pyplot(fig)

    # --- Status Summary ---
    st.subheader("📈 Changes by Status")
    status_summary = df.groupby("Status")["Change"].nunique().reset_index()
    status_summary.columns = ["Status", "Number of Changes"]
    st.dataframe(status_summary)

    # --- Duration Summary ---
    st.subheader("⏱️ Average Duration per Customer (hrs)")
    duration_summary = df.groupby("Customer")["Duration (hrs)"].mean().reset_index()
    duration_summary.columns = ["Customer", "Avg Duration (hrs)"]
    st.dataframe(duration_summary)

    # Weekend count summary
    weekend_count = weekend_df.groupby("Customer")["Change"].nunique().reset_index()
    weekend_count.columns = ["Customer", "Weekend Changes"]
    st.subheader("🪴 Weekend Change Count")
    st.dataframe(weekend_count)

else:
    st.info("👆 Please upload a CSV or Excel file to begin.")
