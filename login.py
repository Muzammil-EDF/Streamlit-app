# main.py
import streamlit as st
from utils.auth import login

# ----------------------------
# SESSION STATE INIT
# ----------------------------
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
    st.session_state.username = ""

# ----------------------------
# LOGIN PAGE
# ----------------------------
def main():
    if st.session_state.logged_in:
        st.sidebar.title("Navigation")
        st.sidebar.write(f"👤 Logged in as: **{st.session_state.username}**")
        if st.sidebar.button("🚪 Logout"):
            st.session_state.logged_in = False
            st.session_state.username = ""
            st.experimental_rerun()
        st.title("📊 Maintenance Dashboard")
        st.info("Use the left sidebar to access pages.")
    else:
        login()

if __name__ == "__main__":
    main()
