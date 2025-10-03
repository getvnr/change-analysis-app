import streamlit as st
import pandas as pd
import plotly.express as px
from io import BytesIO

st.set_page_config(page_title="Change Analysis Dashboard", layout="wide")

st.title("📊 Customer Change Analysis Dashboard")

# File upload
uploaded_file = st.file_uploader("Upload Changes.xlsx", type=["xlsx"])

if uploaded_file:
    df = pd.read_excel(uploaded_file, sheet_name="Sheet1")
    df["Start Date"] = pd.to_datetime(df["Start Date"])
    df["End Date"] = pd.to_datetime(df["End Date"])
    df["Day"] = df["Start Date"].dt.day_name()
    df["Weekend"] = df["Day"].isin(["Saturday", "Sunday"])

    # Sidebar filters
    customers = st.sidebar.multiselect("Select Customers", options=df["customer"].unique(), default=df["customer"].unique())
    start_date = st.sidebar.date_input("Start Date", value=df["Start Date"].min().date())
    end_date = st.sidebar.date_input("End Date", value=df["Start Date"].max().date())

    # Filter data
    mask = (
        df["customer"].isin(customers)
        & (df["Start Date"] >= pd.to_datetime(start_date))
        & (df["Start Date"] <= pd.to_datetime(end_date))
    )
    filtered_df = df[mask]

    st.subheader("Filtered Data Preview")
    st.dataframe(filtered_df.head(20))

    # Download button for filtered data
    def to_excel(df):
        output = BytesIO()
        with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
            df.to_excel(writer, index=False, sheet_name='Filtered_Data')
        return output.getvalue()

    excel_data = to_excel(filtered_df)
    st.download_button(
        label="Download Filtered Data as Excel",
        data=excel_data,
        file_name="filtered_changes.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )

    # Weekend vs Weekday Pie Chart
    weekend_counts = filtered_df["Weekend"].value_counts().rename({True: "Weekend", False: "Weekday"})
    fig1 = px.pie(values=weekend_counts.values, names=weekend_counts.index, title="Weekend vs Weekday Changes")
    st.plotly_chart(fig1, use_container_width=True)

    # Customer-wise Pie Chart (Status breakdown)
    st.subheader("Customer Status Breakdown")
    for cust in customers:
        cust_df = filtered_df[filtered_df["customer"] == cust]
        if not cust_df.empty:
            status_counts = cust_df["Status"].value_counts()
            fig2 = px.pie(values=status_counts.values, names=status_counts.index, title=f"{cust} - Status Breakdown")
            st.plotly_chart(fig2, use_container_width=True)

    # Time Trend of Changes
    st.subheader("Changes Over Time")
    time_trend = filtered_df.groupby(filtered_df["Start Date"].dt.date).size().reset_index(name="Counts")
    fig3 = px.bar(time_trend, x="Start Date", y="Counts", title="Daily Changes Trend")
    st.plotly_chart(fig3, use_container_width=True)

else:
    st.info("👆 Please upload the Changes.xlsx file to start analysis.")
