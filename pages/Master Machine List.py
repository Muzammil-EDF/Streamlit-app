# pages/2_📘_Master_Machine_List.py
import streamlit as st
import pandas as pd

GOOGLE_SHEET_CSV = "https://docs.google.com/spreadsheets/d/11WppySSOEDKbcAAtqJjvnfU8vxcuQJPh5ZcTv_9e2I4/export?format=csv"

def run_user2_page():
    st.title("📘 Master Machine List")
    try:
        df = pd.read_csv(GOOGLE_SHEET_CSV)
        with st.expander("🔍 Filter Machine List", expanded=True):
            filters = {}
            for col in df.columns:
                filters[col] = st.text_input(f"Search in '{col}'")
        filtered_df = df.copy()
        for col, val in filters.items():
            if val:
                filtered_df = filtered_df[filtered_df[col].astype(str).str.contains(val, case=False, na=False)]
        st.dataframe(filtered_df, use_container_width=True)
    except Exception as e:
        st.error(f"Error loading sheet: {e}")

# Run when page loaded
if st.session_state.get("logged_in") and st.session_state.username == "user2":
    run_user2_page()
