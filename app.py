import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from io import StringIO
from datetime import datetime, timedelta

st.set_page_config(page_title="Weekend Change Analyzer", page_icon="🧭", layout="wide")
st.title("🧭 Middleware Weekend Change Analyzer")
st.write("Paste your change records below and click **Analyze**. The tool will detect weekend changes automatically.")

# Text area for pasted data
user_input = st.text_area("📋 Paste your data here (use tab-separated or space-separated format):", height=250)

if st.button("🔍 Analyze"):
    if not user_input.strip():
        st.warning("Please paste your data first.")
    else:
        try:
            # Convert text input into DataFrame
            df = pd.read_csv(StringIO(user_input), sep=r'\s{2,}|\t', engine='python')
            df.columns = [col.strip() for col in df.columns]

            # Parse datetime columns
            for col in ["Start Date", "End Date"]:
                df[col] = pd.to_datetime(df[col], errors="coerce", dayfirst=True)

            # Add derived columns
            df["Duration (hrs)"] = (df["End Date"] - df["Start Date"]).dt.total_seconds() / 3600
            df["Day"] = df["Start Date"].dt.day_name()

            # Display raw data
            st.subheader("📄 Parsed Change Data")
            st.dataframe(df)

            # Weekend filter
            today = datetime.now()
            next_friday = today + timedelta((4 - today.weekday()) % 7)
            next_monday = next_friday + timedelta(days=2)
            weekend_df = df[
                (df["Start Date"].dt.date >= next_friday.date()) &
                (df["Start Date"].dt.date <= next_monday.date())
            ]

            st.subheader(f"🗓️ Changes for Weekend ({next_friday.strftime('%b %d')} - {next_monday.strftime('%b %d')})")
            if weekend_df.empty:
                st.warning("No changes found for this weekend.")
            else:
                st.dataframe(weekend_df)

            # Summary by Customer
            st.subheader("📊 Changes per Customer")
            customer_summary = df.groupby("Customer")["Change"].nunique().reset_index()
            customer_summary.columns = ["Customer", "Number of Changes"]
            st.dataframe(customer_summary)

            fig, ax = plt.subplots()
            ax.bar(customer_summary["Customer"], customer_summary["Number of Changes"], color="skyblue")
            ax.set_xlabel("Customer")
            ax.set_ylabel("Number of Changes")
            ax.set_title("Changes by Customer")
            st.pyplot(fig)

            # Summary by Status
            st.subheader("📈 Changes by Status")
            status_summary = df.groupby("Status")["Change"].nunique().reset_index()
            status_summary.columns = ["Status", "Number of Changes"]
            st.dataframe(status_summary)

            # Duration summary
            st.subheader("⏱️ Average Duration (hrs) per Customer")
            duration_summary = df.groupby("Customer")["Duration (hrs)"].mean().reset_index()
            duration_summary.columns = ["Customer", "Avg Duration (hrs)"]
            st.dataframe(duration_summary)

        except Exception as e:
            st.error(f"Error while parsing data: {e}")
else:
    st.info("Paste your table above and click **Analyze**.")
