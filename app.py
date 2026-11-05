import streamlit as st
import json
import urllib.request
import urllib.error
import datetime
import time

# -----------------------------------------------------------------------------
# APP CONFIGURATION & STATE INITIALIZATION
# -----------------------------------------------------------------------------
st.set_page_config(
    page_title="Adaptive Athletic Load Copilot",
    page_icon="⚡",
    layout="wide"
)

# Persistent Session State Setup
if "onboarding_complete" not in st.session_state:
    st.session_state.onboarding_complete = False
if "onboarding_step" not in st.session_state:
    st.session_state.onboarding_step = 1
if "user_profile" not in st.session_state:
    st.session_state.user_profile = {}
if "activity_slots" not in st.session_state:
    st.session_state.activity_slots = ["Football / Soccer", "Gym / Strength Training"]
if "custom_workouts" not in st.session_state:
    st.session_state.custom_workouts = {
        "Push Split": ["Bench Press (4x8)", "Overhead DB Press (3x10)", "Tricep Dips (3x12)"],
        "Leg Day & Lower Body": ["Barbell Squats (4x6)", "Romanian Deadlifts (3x8)", "Leg Press (3x10)"]
    }
if "calendar_events" not in st.session_state:
    today_str = str(datetime.date.today())
    match_day_str = str(datetime.date.today() + datetime.timedelta(days=2))
    st.session_state.calendar_events = {
        today_str: {"type": "Gym / Strength Training", "workout_name": "Leg Day & Lower Body", "color": "🔵", "is_anchor": False},
        match_day_str: {"type": "Football / Soccer", "workout_name": "League Match Fixture (90 mins)", "color": "🔴", "is_anchor": True}
    }
if "temp_exercise_list" not in st.session_state:
    st.session_state.temp_exercise_list = ["Barbell Squats (4x6)", "Romanian Deadlifts (3x8)"]

ALL_ACTIVITIES = [
    "Football / Soccer", "Gym / Strength Training", "Running & Cardio", 
    "Swimming", "Rugby", "Hyrox / Functional Fitness", "Cycling", 
    "Basketball", "Tennis / Racket Sports", "Combat Sports", "Custom Activity"
]

# -----------------------------------------------------------------------------
# GUIDED MULTI-STEP ONBOARDING WIZARD
# -----------------------------------------------------------------------------
if not st.session_state.onboarding_complete:
    st.title("⚡ Welcome to Athletic Load Copilot")
    st.caption("Democratized Sports Science & Dynamic Workout Adjustments for Athletes")

    progress_val = st.session_state.onboarding_step / 4.0
    st.progress(progress_val)
    st.caption(f"Step {st.session_state.onboarding_step} of 4")

    # STEP 1: ACCOUNT CREATION
    if st.session_state.onboarding_step == 1:
        st.subheader("Step 1: Account Setup")
        col_a, col_b = st.columns(2)
        with col_a:
            name = st.text_input("First Name", value=st.session_state.user_profile.get("name", "Alex"))
            email = st.text_input("Email Address", value=st.session_state.user_profile.get("email", "athlete@example.com"))
        with col_b:
            password = st.text_input("Password", type="password", value="password123")
        
        if st.button("Next: Activity Hierarchy ➡️", type="primary"):
            if name and email and password:
                st.session_state.user_profile["name"] = name
                st.session_state.user_profile["email"] = email
                st.session_state.onboarding_step = 2
                st.rerun()
            else:
                st.error("Please fill in all account details.")

    # STEP 2: ACTIVITY HIERARCHY
    elif st.session_state.onboarding_step == 2:
        st.subheader("Step 2: Activity Hierarchy Setup")
        st.write("Your **Primary Activity** acts as your immovable anchor that the AI adapts everything else around.")

        updated_activities = []
        for idx, act_val in enumerate(st.session_state.activity_slots):
            label = "🏆 Activity 1 (Primary Anchor - Immovable)" if idx == 0 else f"🥈 Activity {idx + 1}"
            default_idx = ALL_ACTIVITIES.index(act_val) if act_val in ALL_ACTIVITIES else 0
            selected_act = st.selectbox(label, ALL_ACTIVITIES, index=default_idx, key=f"ob_act_{idx}")
            updated_activities.append(selected_act)

        st.session_state.activity_slots = updated_activities

        col_act1, col_act2 = st.columns([1, 3])
        with col_act1:
            if st.button("➕ Add Activity"):
                st.session_state.activity_slots.append("Running & Cardio")
                st.rerun()
        with col_act2:
            if len(st.session_state.activity_slots) > 2:
                if st.button("➖ Remove Activity"):
                    st.session_state.activity_slots.pop()
                    st.rerun()

        st.markdown("---")
        col_nav1, col_nav2 = st.columns(2)
        if col_nav1.button("⬅️ Back"):
            st.session_state.onboarding_step = 1
            st.rerun()
        if col_nav2.button("Next: Add Primary Anchor Dates ➡️", type="primary"):
            st.session_state.user_profile["primary_anchor"] = st.session_state.activity_slots[0]
            st.session_state.user_profile["activities"] = st.session_state.activity_slots
            st.session_state.onboarding_step = 3
            st.rerun()

    # STEP 3: LOG PRIMARY ANCHOR FIXTURES / DATES
    elif st.session_state.onboarding_step == 3:
        primary_act = st.session_state.user_profile.get("primary_anchor", "Primary Sport")
        st.subheader(f"Step 3: Add Known {primary_act} Fixtures & Dates")
        st.write(f"Log any upcoming matches, race days, or training sessions you currently know for **{primary_act}**.")

        with st.form("add_anchor_fixture_form"):
            fixture_date = st.date_input("Fixture Date", datetime.date.today() + datetime.timedelta(days=2))
            fixture_desc = st.text_input("Event Description", value=f"Competitive {primary_act} Fixture")
            submit_fixture = st.form_submit_button("📌 Add Fixture to Calendar")

            if submit_fixture:
                st.session_state.calendar_events[str(fixture_date)] = {
                    "type": primary_act,
                    "workout_name": fixture_desc,
                    "color": "🔴",
                    "is_anchor": True
                }
                st.success(f"Added 🔴 {fixture_desc} on {fixture_date}!")

        st.markdown("### Currently Logged Anchor Events:")
        for d_str, ev in list(st.session_state.calendar_events.items()):
            if ev.get("is_anchor"):
                st.markdown(f"- 🔴 **{d_str}**: {ev['workout_name']}")

        st.markdown("---")
        col_nav1, col_nav2 = st.columns(2)
        if col_nav1.button("⬅️ Back"):
            st.session_state.onboarding_step = 2
            st.rerun()
        if col_nav2.button("Next: Custom Workout Splits ➡️", type="primary"):
            st.session_state.onboarding_step = 4
            st.rerun()

    # STEP 4: CUSTOM WORKOUT SPLITS SETUP
    elif st.session_state.onboarding_step == 4:
        st.subheader("Step 4: Set Up Your Custom Workout Splits")
        st.write("Create your secondary gym splits or training routines (e.g., Push, Pull, Legs, Swimming Laps).")

        routine_title = st.text_input("Routine Title", value="Push Split", key="ob_routine_title")
        st.write("**Exercises:**")

        updated_ex_list = []
        for idx, ex_val in enumerate(st.session_state.temp_exercise_list):
            new_ex = st.text_input(f"Exercise #{idx + 1}", value=ex_val, key=f"ob_ex_{idx}")
            updated_ex_list.append(new_ex)
        st.session_state.temp_exercise_list = updated_ex_list

        col_ex1, col_ex2 = st.columns([1, 3])
        with col_ex1:
            if st.button("➕ Add Exercise"):
                st.session_state.temp_exercise_list.append("")
                st.rerun()
        with col_ex2:
            if len(st.session_state.temp_exercise_list) > 1:
                if st.button("➖ Remove Exercise"):
                    st.session_state.temp_exercise_list.pop()
                    st.rerun()

        if st.button("💾 Save Routine", key="ob_save_routine"):
            clean_exs = [e.strip() for e in st.session_state.temp_exercise_list if e.strip()]
            if routine_title and clean_exs:
                st.session_state.custom_workouts[routine_title] = clean_exs
                st.success(f"Saved '{routine_title}'!")

        st.markdown("---")
        col_nav1, col_nav2 = st.columns(2)
        if col_nav1.button("⬅️ Back"):
            st.session_state.onboarding_step = 3
            st.rerun()
        if col_nav2.button("🚀 Finish Setup & Enter Dashboard", type="primary"):
            st.session_state.onboarding_complete = True
            st.rerun()

    st.stop()

# -----------------------------------------------------------------------------
# MAIN DASHBOARD (LOADS DIRECTLY AFTER ONBOARDING)
# -----------------------------------------------------------------------------
profile = st.session_state.user_profile
st.sidebar.title(f"⚡ {profile.get('name', 'Athlete')}")
st.sidebar.markdown(f"**Primary Anchor:** 🔴 {profile.get('primary_anchor', 'Primary')}")

st.sidebar.markdown("**Your Activity Hierarchy:**")
for i, act in enumerate(profile.get("activities", []), 1):
    icon = "🔴 (Anchor)" if i == 1 else "🔵"
    st.sidebar.markdown(f"{i}. {icon} {act}")

if st.sidebar.button("Log Out / Re-run Setup"):
    st.session_state.onboarding_complete = False
    st.session_state.onboarding_step = 1
    st.rerun()

tab_checkin, tab_calendar, tab_library = st.tabs(
    ["⚡ Daily Check-In", "📅 Calendar & Scheduling", "⚙️ Custom Workout Builder"]
)

today_date = datetime.date.today()
today_key = str(today_date)
upcoming_anchors = []
for d_str, ev in st.session_state.calendar_events.items():
    ev_date = datetime.datetime.strptime(d_str, "%Y-%m-%d").date()
    if ev.get("is_anchor") and ev_date >= today_date:
        days_diff = (ev_date - today_date).days
        upcoming_anchors.append(days_diff)

nearest_anchor_days = min(upcoming_anchors) if upcoming_anchors else 99.0

# -----------------------------------------------------------------------------
# TAB 1: DAILY CHECK-IN (DEFAULT PAGE FOR RETURNING USERS)
# -----------------------------------------------------------------------------
with tab_checkin:
    col_input, col_output = st.columns([1, 1], gap="large")
    today_event = st.session_state.calendar_events.get(today_key, {"type": "Rest", "workout_name": "Rest & Recovery", "color": "⚪", "is_anchor": False})

    with col_input:
        st.header("📝 Daily 30-Second Check-In")
        st.info(f"**Scheduled Today ({today_key}):** {today_event['color']} {today_event['workout_name']}")
        
        if 0.0 < nearest_anchor_days <= 2.0:
            st.warning(f"⚡ **Taper Zone Active:** {profile.get('primary_anchor')} scheduled in {nearest_anchor_days:.1f} days.")
        elif nearest_anchor_days == 0.0:
            st.error(f"🔴 **PRIMARY ANCHOR DAY TODAY ({profile.get('primary_anchor')}):** Focus on performance and recovery!")
        else:
            st.caption(f"📍 No primary {profile.get('primary_anchor')} anchors detected in the next 48 hours.")

        energy_score = st.slider("1. Systemic Energy Score (1 = Battered, 10 = Peak)", 1, 10, 6)
        
        st.write("2. Flag Localized Soreness / Joint Tightness")
        lower_body_areas = ["Knees / Patellar", "Hamstrings", "Quadriceps", "Calves / Achilles", "Groin / Adductors", "Shins", "Ankles", "Glutes / Hips"]
        upper_body_areas = ["Shoulders / Rotator Cuff", "Upper Back / Lats", "Low Back", "Chest", "Triceps / Biceps", "Forearms / Elbows", "Core / Abs"]
        
        flagged_lower = st.multiselect("Lower Body & Joints", lower_body_areas)
        flagged_upper = st.multiselect("Upper Body & Core", upper_body_areas)
        flagged_all = flagged_lower + flagged_upper

        available_time = st.slider("3. Available Time Today (Minutes)", 15, 120, 45, step=15)
        btn_generate = st.button("⚡ Generate Today's Adapted Session", type="primary", use_container_width=True)

    with col_output:
        st.header("🎯 AI Sports Science Output")
        if btn_generate:
            if today_event["type"] == "Rest":
                st.success("⚪ **REST DAY SCHEDULED**")
                st.write("Enjoy active recovery today. Maintain hydration and mobility!")
            else:
                current_exercises = st.session_state.custom_workouts.get(today_event['workout_name'], [today_event['workout_name']])
                
                api_key = st.secrets.get("GEMINI_API_KEY", "").strip()
                if not api_key:
                    st.error("GEMINI_API_KEY is missing from Streamlit Secrets.")
                else:
                    # Valid active models
                    models_to_try = ["gemini-2.5-flash", "gemini-2.0-flash"]
                    
                    prompt = (
                        "You are an elite sports scientist and adaptive S&C coach.\n"
                        f"PRIMARY ANCHOR SPORT: {profile.get('primary_anchor')}\n"
                        f"SCHEDULED TODAY: {today_event['workout_name']}\n"
                        f"TARGET EXERCISES: {json.dumps(current_exercises)}\n"
                        f"AVAILABLE TIME: {available_time} mins\n"
                        f"ENERGY SCORE: {energy_score}/10\n"
                        f"FLAGGED SORE
