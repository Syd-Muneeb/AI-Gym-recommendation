import streamlit as st
import pandas as pd
import datetime
# Removed: from dotenv import load_dotenv # No longer needed here

# Import functions from your modules
from auth import login_signup_ui, initialize_firebase
from dataload import load_data, initialize_model # <--- Changed from src.data_loader to dataload
from groqAI import analyze_routine_with_groq       # <--- Changed from src.groq_integration to groq
from workout_logic import recommend_workout, suggest_sets_reps, generate_routine
# Set page configuration
st.set_page_config(page_title="Gym Workout Planner", layout="wide")

st.markdown("""
<style>
/* App Background */
[data-testid="stAppViewContainer"] {
    background-color: #f4f4f5;
}

/* Sidebar */
[data-testid="stSidebar"] * {
    color: white;
}

/* Header (fix white-on-white issue) */
h1, h2, h3, .stMarkdown h1, .stMarkdown h2, .stMarkdown h3 {
    color: #1f2937 !important;
}

/* Tabs: Login / Sign Up */
.stTabs [role="tab"] {
    background-color: #e0e7ff;
    color: #1e3a8a;
    padding: 6px 16px;
    margin-right: 6px;
    border-radius: 6px 6px 0 0;
    font-weight: 500;
    font-size: 14px;
}
.stTabs [role="tab"][aria-selected="true"] {
    background-color: #3b82f6;
    color: white;
    font-weight: 600;
}

/* Tab Panel Container */
.stTabs [data-baseweb="tab-panel"] {
    background-color: white;
    border-radius: 0 8px 8px 8px;
    padding: 20px;
    box-shadow: 0 1px 6px rgba(0, 0, 0, 0.08);
}

/* Form Containers */
.stForm {
    background-color: white;
    border-radius: 10px;
    padding: 24px;
    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

/* Input Fields */
input, textarea, select {
    background-color: white !important;
    border-radius: 6px !important;
    border: 1px solid #d1d5db !important;
    padding: 10px !important;
    color: #111827 !important;
    font-size: 14px;
}

/* Password field fix: eye icon & field radius */
input[type="password"] {
    padding-right: 40px !important;
}
[data-testid="textInput"] > div {
    border-radius: 6px !important;
}

/* Eye Icon Button */
[data-testid="textInput"] button {
    background-color: #3b82f6 !important;
    color: white !important;
    border-top-right-radius: 6px !important;
    border-bottom-right-radius: 6px !important;
}
[data-testid="textInput"] button:hover {
    background-color: #2563eb !important;
}

/* Labels */
label {
    font-weight: 500;
    color: #374151 !important;
    font-size: 14px;
}

/* Action Buttons (Login / Sign up) */
button[kind="primary"] {
    background-color: #3b82f6 !important;
    color: white !important;
    border-radius: 6px !important;
    padding: 10px 18px !important;
    font-weight: 600 !important;
    font-size: 14px;
}
button[kind="primary"]:hover {
    background-color: #2563eb !important;
}

/* Download Button Variant */
.stDownloadButton button {
    background-color: #10b981 !important;
}
.stDownloadButton button:hover {
    background-color: #059669 !important;
}

/* Errors */
[data-testid="stError"] {
    background-color: #fee2e2 !important;
    color: #991b1b !important;
    border-radius: 6px;
    padding: 12px;
}
div[data-testid="stAlert"] > div {
    color: black !important;
}

/* Dropdown (selectbox and multiselect) */
div[data-baseweb="select"] {
    background-color: white !important;
    border-radius: 6px !important;
    border: 1px solid #d1d5db !important;
}
div[data-baseweb="select"] > div {
    background-color: white !important;
    color: #111827 !important;
}
div[data-baseweb="select"] span {
    color: #111827 !important;
}
div[data-baseweb="popover"] {
    background-color: white !important;
    border: 1px solid #d1d5db !important;
    border-radius: 6px !important;
    box-shadow: 0 4px 10px rgba(0, 0, 0, 0.1) !important;
}
div[data-baseweb="popover"] [role="option"] {
    color: #1f2937 !important;
    background-color: white !important;
}
div[data-baseweb="popover"] [role="option"]:hover {
    background-color: #e0e7ff !important;
}

/* DataFrame/Table Styling (Workout Routine and Exercise Library) */
[data-testid="stDataFrame"] table {
    background-color: white !important;
    border-radius: 6px !important;
    border: 1px solid #d1d5db !important;
    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1) !important;
    width: 100% !important;
}
[data-testid="stDataFrame"] table thead th {
    background-color: #3b82f6 !important;
    color: white !important;
    font-weight: 600 !important;
    padding: 10px !important;
    border-bottom: 2px solid #d1d5db !important;
}
[data-testid="stDataFrame"] table tbody td {
    background-color: white !important;
    color: #1f2937 !important;
    padding: 8px !important;
    border-bottom: 1px solid #d1d5db !important;
}
[data-testid="stDataFrame"] table tbody tr:nth-child(even) {
    background-color: #e0e7ff !important;
}

/* Markdown content */
.stMarkdown p, .stMarkdown div {
    color: #1f2937 !important;
}

div[data-testid="stCheckbox"] label > div {
        color: black !important;
    }
    /* Also target the span inside for safety */
    div[data-testid="stCheckbox"] label > div > span {
        color: black !important;
    }

</style>
""", unsafe_allow_html=True)


# Initialize Firebase (auth and db objects)
auth, db = initialize_firebase()

# Authentication and Login/Signup Flow
if not login_signup_ui():
    st.stop() # Stop execution if not logged in

# Title and description
st.title("🏋‍♂ Gym Workout Planner")
st.markdown("""
Welcome to the Gym Workout Planner! Use the *Workout Routine* tab to get a structured workout plan or the *Exercise Library* tab to browse and filter all exercises.
""")

# Load dataset and initialize models
df = load_data()
tfidf, tfidf_matrix, cosine_sim = initialize_model(df)


# ========================
#       MAIN APP TABS
# ========================
tab1, tab2, tab3 = st.tabs(["Workout Routine", "Exercise Library", "My Workouts"])

# --- 1. Workout Routine Tab ---
with tab1:
    st.subheader("Get Your Personalized Workout Routine")
    with st.form("routine_form"):
        st.subheader("Exercise Preferences")
        col1, col2 = st.columns(2)
        with col1:
            goal = st.selectbox("Fitness Goal", options=sorted(df['Type'].unique()))
            muscle = st.selectbox("Target Muscle Group", options=sorted(df['BodyPart'].unique()))
            equipment = st.selectbox("Available Equipment", options=sorted(df['Equipment'].unique()))
        with col2:
            level = st.selectbox("Experience Level", options=["Beginner", "Intermediate", "Advanced"])
            num_recommendations = st.slider("Number of Exercises", min_value=5, max_value=20, value=10)
            min_rating = st.slider("Minimum Rating", min_value=0.0, max_value=10.0, value=0.0, step=0.1)
            require_description = st.checkbox("Only include exercises with descriptions", value=False)

        st.markdown("---")
        st.subheader("Workout Routine Preferences")
        col3, col4 = st.columns(2)
        with col3:
            days_per_week = st.slider("Days per Week", 1, 7, 3)
        with col4:
            split_type = st.selectbox("Workout Split Type", ["Full Body", "Upper/Lower", "Push/Pull/Legs"])

        submit_routine = st.form_submit_button("Generate Workout Routine")

    # Display saved routine from session_state (if any)
    if 'routine' in st.session_state and 'full_routine_df' in st.session_state:
        st.subheader("Your Workout Routine")
        routine = st.session_state['routine']
        full_routine_df = st.session_state['full_routine_df']

        for day, exercises in routine.items():
            if exercises.empty:
                st.warning(f"{day}: Not enough exercises to generate this day's plan.")
                continue
            st.markdown(f"### {day}")
            routine_table = exercises[['Title', 'Type', 'BodyPart', 'Equipment', 'Level', 'Rating']].copy()
            routine_table["Sets x Reps"] = routine_table.apply(lambda row: suggest_sets_reps(row['Type'], row['Level']), axis=1)
            st.dataframe(routine_table, use_container_width=True)

        csv = full_routine_df.to_csv(index=False)
        st.download_button(
            "Download Workout Routine as CSV",
            data=csv,
            file_name="workout_routine.csv",
            mime="text/csv",
            key=f"download_routine_saved_{st.session_state['user_email']}_{st.session_state.get('split_type', '')}_{st.session_state.get('days_per_week', '')}"
        )

        # --- SAVE BUTTON (after generating routine) ---
        if st.button(
            "Save Workout Routine",
            key=f"save_routine_saved_{st.session_state['user_email']}_{st.session_state.get('split_type','')}_{st.session_state.get('days_per_week','')}"
        ):
            user_email_safe = st.session_state["user_email"].replace(".", "-")
            dt_string = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
            save_data = {
                "date": dt_string,
                "routine": full_routine_df.to_dict(orient="records"),
                "split_type": st.session_state.get('split_type', ''),
                "days_per_week": st.session_state.get('days_per_week', '')
            }
            db.child("users").child(user_email_safe).child("workouts").push(save_data)
            st.success("Workout routine saved to your account!")

    # Original routine generation block
    if submit_routine:
        recommendations, num_matches = recommend_workout(df, tfidf, tfidf_matrix, goal, muscle, equipment, level, num_recommendations, min_rating, require_description)

        # Save split_type and days_per_week for saving to Firebase later
        st.session_state['split_type'] = split_type
        st.session_state['days_per_week'] = days_per_week

        if not recommendations.empty:
            st.success(f"Found {num_matches} matching exercises. Generating a {split_type} routine over {days_per_week} day(s).")
            routine = generate_routine(recommendations, days=days_per_week, split=split_type)

            full_routine_df = pd.DataFrame()
            for day, exercises in routine.items():
                if exercises.empty:
                    st.warning(f"{day}: Not enough exercises to generate this day's plan.")
                    continue
                st.markdown(f"### {day}")
                routine_table = exercises[['Title', 'Type', 'BodyPart', 'Equipment', 'Level', 'Rating']].copy()
                routine_table["Sets x Reps"] = routine_table.apply(lambda row: suggest_sets_reps(row['Type'], row['Level']), axis=1)
                st.dataframe(routine_table, use_container_width=True)
                full_routine_df = pd.concat([full_routine_df, routine_table])

            if not full_routine_df.empty:
                st.session_state['routine'] = routine
                st.session_state['full_routine_df'] = full_routine_df
                csv = full_routine_df.to_csv(index=False)
                st.download_button(
                    "Download Workout Routine as CSV",
                    data=csv,
                    file_name="workout_routine.csv",
                    mime="text/csv",
                    key=f"download_routine_new_{st.session_state['user_email']}_{split_type}_{days_per_week}"
                )
                if st.button(
                    "Save Workout Routine",
                    key=f"save_routine_new_{st.session_state['user_email']}_{split_type}_{days_per_week}"
                ):
                    user_email_safe = st.session_state["user_email"].replace(".", "-")
                    dt_string = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
                    save_data = {
                        "date": dt_string,
                        "routine": full_routine_df.to_dict(orient="records"),
                        "split_type": split_type,
                        "days_per_week": days_per_week
                    }
                    db.child("users").child(user_email_safe).child("workouts").push(save_data)
                    st.success("Workout routine saved to your account!")
        else:
            st.warning("No exercises found for your routine. Try adjusting preferences.")

    if 'full_routine_df' in st.session_state:
        if st.button("Analyze Routine with Groq AI", key="analyze_groq_button"):
            with st.spinner("Analyzing routine using Groq's AI..."):
                feedback = analyze_routine_with_groq(st.session_state['full_routine_df'])
                st.subheader("🧠 Groq AI Feedback")
                st.markdown(feedback)
    else:
        st.info("Generate a workout routine first to analyze it.")

# --- 2. Exercise Library Tab ---
with tab2:
    st.subheader("Browse Exercise Library")
    st.markdown("Filter and search the full exercise library (2,918 exercises).")

    with st.form("library_form"):
        col3, col4 = st.columns(2)
        with col3:
            search_query = st.text_input("Search Exercises", placeholder="Enter keywords (e.g., bench press)", help="Search by exercise title or description.")
            type_filter = st.multiselect("Filter by Type", options=sorted(df['Type'].unique()), help="Select exercise types to filter.")
            bodypart_filter = st.multiselect("Filter by Body Part", options=sorted(df['BodyPart'].unique()), help="Select target muscle groups.")

        with col4:
            equipment_filter = st.multiselect("Filter by Equipment", options=sorted(df['Equipment'].unique()), help="Select equipment types.")
            level_filter = st.multiselect("Filter by Level", options=["Beginner", "Intermediate", "Advanced"], help="Select experience levels.")
            sort_by = st.selectbox("Sort By", options=["Title", "Rating", "Type", "BodyPart", "Equipment", "Level"], help="Sort the exercise list.")

        submit_filters = st.form_submit_button("Apply Filters")

    filtered_df = df.copy()
    if submit_filters or st.session_state.get('filters_applied', False):
        if 'filters_applied' not in st.session_state:
            st.session_state.filters_applied = True
        if search_query:
            filtered_df = filtered_df[filtered_df['Title'].str.contains(search_query, case=False, na=False) |
                                     filtered_df['Desc'].str.contains(search_query, case=False, na=False)]
        if type_filter:
            filtered_df = filtered_df[filtered_df['Type'].isin(type_filter)]
        if bodypart_filter:
            filtered_df = filtered_df[filtered_df['BodyPart'].isin(bodypart_filter)]
        if equipment_filter:
            filtered_df = filtered_df[filtered_df['Equipment'].isin(equipment_filter)]
        if level_filter:
            filtered_df = filtered_df[filtered_df['Level'].isin(level_filter)]

        filtered_df = filtered_df.sort_values(by=sort_by, ascending=True)

        st.write(f"Showing {len(filtered_df)} exercises:")
        st.dataframe(filtered_df[['Title', 'Type', 'BodyPart', 'Equipment', 'Level', 'Rating', 'Desc']], use_container_width=True)
        csv = filtered_df[['Title', 'Type', 'BodyPart', 'Equipment', 'Level', 'Rating', 'Desc']].to_csv(index=False)
        st.download_button("Download Filtered Exercises CSV", data=csv, file_name="filtered_exercises.csv", mime="text/csv", key="filtered_exercises_download")
    else:
        st.info("Use the filters above and click 'Apply Filters' to browse exercises.")

# --- 3. My Workouts Tab ---
with tab3:
    st.subheader("📋 My Saved Workouts")

    user_email_safe = st.session_state["user_email"].replace(".", "-")
    try:
        saved_workouts = db.child("users").child(user_email_safe).child("workouts").get()
        if saved_workouts.val():
            for w in saved_workouts.each():
                workout = w.val()
                st.markdown(f"### Routine saved on {workout['date']} ({workout.get('split_type','')}, {workout.get('days_per_week','')} days/week)")
                df_saved = pd.DataFrame(workout['routine'])
                st.dataframe(df_saved, use_container_width=True)
                csv_saved = df_saved.to_csv(index=False)
                st.download_button("Download This Routine (CSV)", data=csv_saved, file_name=f"workout_{workout['date']}.csv", mime="text/csv", key=workout['date'])
        else:
            st.info("You have no saved workout routines yet. Save one from the Workout Routine tab!")
    except Exception as e:
        st.info("You have no saved workout routines yet. Save one from the Workout Routine tab!")