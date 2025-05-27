# pages/1_🛠️_Preventive_Maintenance.py
import streamlit as st
import pandas as pd
from datetime import datetime

EXCEL_PATH = "pm_backend.xlsx"
OPERATIONS_PATH = "operations.xlsx"

def run_user1_page():
    st.title("🧑‍🔧 Preventive Maintenance")

    if "selected_date" not in st.session_state:
        st.session_state.selected_date = None
    if "show_operations" not in st.session_state:
        st.session_state.show_operations = False
    if "selected_asset" not in st.session_state:
        st.session_state.selected_asset = None
    if "selected_assets" not in st.session_state:
        st.session_state.selected_assets = []

    # Date input
    col1, col2 = st.columns([2, 1])
    with col1:
        st.text_input("Date (auto-filled)", value=str(st.session_state.selected_date or ""), disabled=True)
    with col2:
        if st.button("📅 Extract Today’s Date"):
            st.session_state.selected_date = datetime.today().date()
            st.session_state.show_operations = False

    # Filter assets
    if st.session_state.selected_date:
        try:
            df_assets = pd.read_excel(EXCEL_PATH)
            df_assets['Date'] = pd.to_datetime(df_assets['Date']).dt.date
            filtered_df = df_assets[df_assets['Date'] == st.session_state.selected_date]
            if not filtered_df.empty:
                asset_options = filtered_df['Asset Number'].dropna().unique()
                available_assets = [a for a in asset_options if a not in st.session_state.selected_assets]
                if available_assets:
                    selected_asset = st.selectbox("Select Asset", available_assets)
                    if st.button("➡️ Proceed"):
                        st.session_state.selected_asset = selected_asset
                        st.session_state.show_operations = True
                        st.session_state.selected_assets.append(selected_asset)
                else:
                    st.info("✅ All assets for today have been selected.")
            else:
                st.warning("No assets found for selected date.")
        except Exception as e:
            st.error(f"Error reading asset file: {e}")
    else:
        st.info("Extract today’s date to continue.")

    # Checklist operations
    if st.session_state.show_operations and st.session_state.selected_asset:
        st.markdown("---")
        st.subheader(f"🛠️ Operations for Asset: {st.session_state.selected_asset}")
        try:
            df_ops = pd.read_excel(OPERATIONS_PATH)
            operations = df_ops["Operation"].dropna().tolist()
            checked_ops = [op for op in operations if st.checkbox(op, key=op)]
            if st.button("✅ Submit"):
                if checked_ops:
                    try:
                        df_assets = pd.read_excel(EXCEL_PATH)
                        df_assets['Date'] = pd.to_datetime(df_assets['Date']).dt.date
                        mask = (
                            (df_assets['Date'] == st.session_state.selected_date) &
                            (df_assets['Asset Number'] == st.session_state.selected_asset)
                        )
                        df_assets.loc[mask, 'Operations'] = ', '.join(checked_ops)
                        df_assets.loc[mask, 'Remarks'] = "Done"
                        df_assets.to_excel(EXCEL_PATH, index=False)
                        st.success("✅ Submitted.")
                        st.write("Checked:", checked_ops)
                        st.session_state.show_operations = False
                    except Exception as e:
                        st.error(f"Error saving file: {e}")
                else:
                    st.warning("Select at least one operation.")
        except Exception as e:
            st.error(f"Error reading operations: {e}")

# Run when page loaded
if st.session_state.get("logged_in") and st.session_state.username == "user1":
    run_user1_page()
