import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from io import StringIO
from datetime import datetime, timedelta

st.set_page_config(page_title="Weekend Change Analyzer", page_icon="🧭", layout="wide")
st.title("🧭 Middleware Weekend Change Analyzer")
st.write("Paste your change records below and click **Analyze**.")

user_input = st.text_area("📋 Paste your data here (tab or space separated):", height=250)

if st.button("🔍 Analyze"):
    if not user_input.strip():
        st.warning("Please paste your data first.")
    else:
        try:
            # Normalize and clean text
            cleaned = user_input.replace('\r', '').replace('\n\n', '\n').strip()
            lines = [line.strip() for line in cleaned.splitlines() if line.strip()]

            # Split header
            headers = [h.strip() for h in lines[0].split('\t') if h.strip()]
            if len(headers) < 8:
                headers = [h.strip() for h in lines[0].split() if h.strip()]

            data = []
            for line in lines[1:]:
                parts = [p.strip() for p in line.split('\t') if p.strip()]
                if len(parts) < len(headers):
                    # Try splitting by spaces if tabs missing
                    parts = [p.strip() for p in line.split('  ') if p.strip()]
                # Truncate or pad to correct length
                while len(parts) < len(headers):
                    parts.append("")
                while len(parts) > len(headers):
                    parts = parts[:len(headers)]
                data.append(parts)

            df = pd.DataFrame(data, columns=headers)

            # Parse date columns safely
            for col in ["Start Date", "End Date"]:
                df[col] = pd.to_datetime(df[col], errors="coerce", dayfirst=True)

            df["Duration (hrs)"] = (df["End Date"] - df["Start Date"]).dt.total_seconds() / 3600
            df["Day"] = df["Start Date"].dt.day_name()

            st.subheader("📄 Parsed Change Data")
            st.dataframe(df)

            # Weekend range
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

            st.subheader("📊 Changes per Customer")
            customer_summary = df.groupby("Customer")["Change"].nunique().reset_index()
            customer_summary.columns = ["Customer", "Number of Changes"]
            st.dataframe(customer_summary)

            fig, ax = plt.subplots()
            ax.bar(customer_summary["Customer"], customer_summary["Number of Changes"], color="lightblue")
            ax.set_xlabel("Customer")
            ax.set_ylabel("Number of Changes")
            ax.set_title("Changes by Customer")
            st.pyplot(fig)

            st.subheader("📈 Changes by Status")
            status_summary = df.groupby("Status")["Change"].nunique().reset_index()
            status_summary.columns = ["Status", "Number of Changes"]
            st.dataframe(status_summary)

            st.subheader("⏱️ Avg Duration (hrs) per Customer")
            duration_summary = df.groupby("Customer")["Duration (hrs)"].mean().reset_index()
            duration_summary.columns = ["Customer", "Avg Duration (hrs)"]
            st.dataframe(duration_summary)

        except Exception as e:
            st.error(f"⚠️ Error while parsing data: {e}")
else:
    st.info("Paste your table above and click **Analyze**.")
