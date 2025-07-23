import streamlit as st
import pyrebase

def initialize_firebase():
    firebaseConfig = {
        "apiKey": "AIzaSyDfC1y3dw-hBnsjm9gxq5CA5nceomzVU2o",
        "authDomain": "workout-62645.firebaseapp.com",
        "databaseURL": "https://workout-62645-default-rtdb.firebaseio.com/",
        "projectId": "workout-62645",
        "storageBucket": "workout-62645.firebasestorage.app",
        "messagingSenderId": "1044171265401",
        "appId": "1:1044171265401:web:601910b05fc4f9ac7a8ba8"
    }
    firebase = pyrebase.initialize_app(firebaseConfig)
    return firebase.auth(), firebase.database()

def login_signup_ui():
    auth, _ = initialize_firebase()

    if "logged_in" not in st.session_state:
        st.session_state["logged_in"] = False
    if "user_email" not in st.session_state:
        st.session_state["user_email"] = ""
    if "login_error" not in st.session_state:
        st.session_state["login_error"] = False

    if not st.session_state["logged_in"]:
        st.title("🔐 Gym Workout Planner - Login")
        tabs = st.tabs(["Login", "Sign Up"])

        with tabs[0]:
            st.subheader("Login")
            login_email = st.text_input("Email", key="login_email")
            login_password = st.text_input("Password", type="password", key="login_password")

            if "login_error" in st.session_state and (st.session_state.get("login_error") and (login_email or login_password)):
                st.session_state["login_error"] = False

            if st.button("Login", key="login_button"):
                try:
                    user = auth.sign_in_with_email_and_password(login_email, login_password)
                    st.session_state["logged_in"] = True
                    st.session_state["user_email"] = login_email
                    st.session_state["login_error"] = False
                    st.rerun()
                except Exception as e:
                    st.session_state["login_error"] = True

            if st.session_state.get("login_error"):
                st.error("Login failed. Please check your credentials.")

        with tabs[1]:
            st.subheader("Sign Up")
            signup_email = st.text_input("Email", key="signup_email")
            signup_password = st.text_input("Password", type="password", key="signup_password")
            if st.button("Sign Up"):
                try:
                    auth.create_user_with_email_and_password(signup_email, signup_password)
                    st.success("Account created! Please log in.")
                    st.rerun()
                except Exception as e:
                    st.error("Signup failed: " + str(e))
        st.stop()
    else:
        st.sidebar.success(f"Logged in as {st.session_state['user_email']}")
        if st.sidebar.button("Logout"):
            st.session_state["logged_in"] = False
            st.session_state["user_email"] = ""
            st.session_state["login_error"] = False
            st.rerun()
    return True 