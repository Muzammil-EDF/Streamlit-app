import streamlit as st
import pandas as pd
from datetime import datetime
from streamlit_gsheets import GSheetsConnection



# Path to the backend Excel file and operations file
EXCEL_PATH = "pm_backend.xlsx"
OPERATIONS_PATH = "operations.xlsx"

# ----------------------------
# USER CREDENTIALS
# ----------------------------
USER_CREDENTIALS = {
    "user1": "pass1"
}

# ----------------------------
# SESSION STATE INITIALIZATION
# ----------------------------
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
    st.session_state.username = ""

# ----------------------------
# LOGIN FUNCTION
# ----------------------------
def login():
    st.title("🔐 Login Page")
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")
    
    if st.button("Login"):
        if username in USER_CREDENTIALS and USER_CREDENTIALS[username] == password:
            st.session_state.logged_in = True
            st.session_state.username = username
            st.success("Login successful!")
            st.experimental_rerun()
        else:
            st.error("Invalid username or password")

# ----------------------------
# USER-SPECIFIC PAGES
# ----------------------------

def user1_page():
    st.title("🧑‍🔧 User 1 Maintenance Page")

    # --- Initialize session state ---
    if "selected_date" not in st.session_state:
        st.session_state.selected_date = None
    if "show_operations" not in st.session_state:
        st.session_state.show_operations = False
    if "selected_asset" not in st.session_state:
        st.session_state.selected_asset = None
    if "selected_assets" not in st.session_state:
        st.session_state.selected_assets = []

    # --- Step 1: Extract today's date ---
    col1, col2 = st.columns([2, 1])
    with col1:
        st.text_input("Date (auto-filled)", value=str(st.session_state.selected_date) if st.session_state.selected_date else "", disabled=True)
    with col2:
        if st.button("📅 Extract Today’s Date"):
            st.session_state.selected_date = datetime.today().date()
            st.session_state.show_operations = False  # Reset when new date is picked

    # --- Step 2: Load and filter asset data ---
    if st.session_state.selected_date:
        try:
            df_assets = pd.read_excel(EXCEL_PATH)
            df_assets['Date'] = pd.to_datetime(df_assets['Date']).dt.date

            filtered_df = df_assets[df_assets['Date'] == st.session_state.selected_date]

            if not filtered_df.empty:
                asset_options = filtered_df['Asset Number'].dropna().unique()

                # Hide already selected assets in this session
                available_assets = [a for a in asset_options if a not in st.session_state.selected_assets]

                if available_assets:
                    selected_asset = st.selectbox("Select Asset", available_assets)

                    if st.button("➡️ Proceed"):
                        st.session_state.selected_asset = selected_asset
                        st.session_state.show_operations = True
                        st.session_state.selected_assets.append(selected_asset)
                else:
                    st.info("✅ All available assets for today have been selected.")

            else:
                st.warning("No assets found for the selected date.")

        except Exception as e:
            st.error(f"Error reading asset file: {e}")

    else:
        st.info("Please extract today's date to continue.")

    # --- Step 3: Show checklist of operations ---
    if st.session_state.show_operations and st.session_state.selected_asset:
        st.markdown("---")
        st.subheader(f"🛠️ Operations for Asset: {st.session_state.selected_asset}")

        try:
            df_ops = pd.read_excel(OPERATIONS_PATH)
            operations = df_ops["Operation"].dropna().tolist()

            checked_ops = []
            for op in operations:
                if st.checkbox(op, key=op):
                    checked_ops.append(op)

            if st.button("✅ Submit"):
                if checked_ops:
                    try:
                        # Load the assets file
                        df_assets = pd.read_excel(EXCEL_PATH)
                        df_assets['Date'] = pd.to_datetime(df_assets['Date']).dt.date

                        # Find the matching row
                        mask = (
                            (df_assets['Date'] == st.session_state.selected_date) &
                            (df_assets['Asset Number'] == st.session_state.selected_asset)
                        )

                        # # Update the Remarks column
                        # df_assets.loc[mask, 'Remarks'] = "Done"
                        # # Format checked operations as bullet points
                        # formatted_ops = "Done:\n" + "\n".join([f"• {op}" for op in checked_ops])

                        # Write to Remarks column
                        # df_assets.loc[mask, 'Remarks'] = formatted_ops
                        
                        df_assets.loc[mask, 'Operations'] = ', '.join(checked_ops)  # Store checked operations
                        df_assets.loc[mask, 'Remarks'] = "Done"

                        # Save back to Excel (overwrite)
                        df_assets.to_excel(EXCEL_PATH, index=False)

                        st.success(f"✅ Operations submitted and marked as 'Done' in schedule for asset {st.session_state.selected_asset}.")
                        st.write("Checked operations:", checked_ops)

                        # Reset view
                        st.session_state.show_operations = False

                    except Exception as e:
                        st.error(f"Error updating backend file: {e}")
                else:
                    st.warning("Please select at least one operation before submitting.")

            # if st.button("✅ Submit"):
            #     if checked_ops:
            #         st.success(f"Operations submitted for asset {st.session_state.selected_asset}:")
            #         st.write(checked_ops)
            #         # You could save these to a log file or sheet here
            #         st.session_state.show_operations = False  # Hide mini-page after submit
            #     else:
            #         st.warning("Please select at least one operation before submitting.")

        except Exception as e:
            st.error(f"Error reading operations file: {e}")


def user2_page():
    st.title("User 2 Portal")
    url= "https://docs.google.com/spreadsheets/d/11WppySSOEDKbcAAtqJjvnfU8vxcuQJPh5ZcTv_9e2I4/edit?gid=0#gid=0"
    conn=st.experimental_connection("gsheets",type=GSheetsConnection)
    data=conn.read(spreadsheet=url, usecols=list(range(3)))
    st.dataframe(data)
    
# ----------------------------
# MAIN PAGE SWITCHER
# ----------------------------
def main_page():
    st.sidebar.title("Navigation")
    st.sidebar.write(f"Logged in as: **{st.session_state.username}**")
    if st.sidebar.button("Logout"):
        st.session_state.logged_in = False
        st.session_state.username = ""
        st.experimental_rerun()

    # Show different page based on user
    if st.session_state.username == "user1":
        user1_page()
    elif st.session_state.username == "user2":
        user2_page()
    elif st.session_state.username == "user3":
        user3_page()
    else:
        st.warning("No page defined for this user.")

# ----------------------------
# MAIN FUNCTION
# ----------------------------
def main():
    if st.session_state.logged_in:
        main_page()
    else:
        login()

if __name__ == "__main__":
    main()
