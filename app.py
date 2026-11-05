import streamlit as st
import json
import urllib.request
import datetime

# -----------------------------------------------------------------------------
# APP CONFIGURATION & STATE INITIALIZATION
# -----------------------------------------------------------------------------
st.set_page_config(
    page_title="Adaptive Athletic Load Copilot",
    page_icon="⚡",
    layout="wide"
)

# Persistent Session State Setup
if "user_authenticated" not in st.session_state:
    st.session_state.user_authenticated = False
if "user_profile" not in st.session_state:
    st.session_state.user_profile = {}
if "activity_slots" not in st.session_state:
    st.session_state.activity_slots = ["Football / Soccer", "Gym / Strength Training"]
if "custom_workouts" not in st.session_state:
    st.session_state.custom_workouts = {
        "Leg Day & Lower Body": ["Barbell Squats (4x6)", "Romanian Deadlifts (3x8)", "Leg Press (3x10)", "Calf Raises (4x15)"],
        "Push Split": ["Bench Press (4x8)", "Overhead DB Press (3x10)", "Tricep Dips (3x12)"],
        "Swim Technique & Laps": ["400m Warm-up", "8x50m Interval Sprints", "200m Cool-down"],
        "Tempo Run": ["6km Outdoor Run @ Target Pace"]
    }
if "temp_exercise_list" not in st.session_state:
    st.session_state.temp_exercise_list = ["Barbell Squats (4x6)", "Romanian Deadlifts (3x8)"]
if "calendar_events" not in st.session_state:
    today_str = str(datetime.date.today())
    match_day_str = str(datetime.date.today() + datetime.timedelta(days=2))
    st.session_state.calendar_events = {
        today_str: {"type": "Gym", "workout_name": "Leg Day & Lower Body", "color": "🔵", "is_anchor": False},
        match_day_str: {"type": "Match/Fixture", "workout_name": "Competitive Fixture (90 mins)", "color": "🔴", "is_anchor": True}
    }

ALL_ACTIVITIES = [
    "Football / Soccer", "Gym / Strength Training", "Running & Cardio", 
    "Swimming", "Rugby", "Hyrox / Functional Fitness", "Cycling", 
    "Basketball", "Tennis / Racket Sports", "Combat Sports", "Custom Activity"
]

# -----------------------------------------------------------------------------
# 1. ONBOARDING & DYNAMIC ACTIVITY SETUP
# -----------------------------------------------------------------------------
if not st.session_state.user_authenticated:
    st.title("⚡ Welcome to Athletic Load Copilot")
    st.caption("Democratized Sports Science & Dynamic Workout Adjustments for Athletes")

    st.subheader("Step 1: Account Setup")
    col_a, col_b = st.columns(2)
    with col_a:
        name = st.text_input("First Name", value="Alex")
        email = st.text_input("Email Address", value="athlete@example.com")
    with col_b:
        password = st.text_input("Create Password", type="password", value="password123")

    st.markdown("---")
    st.subheader("Step 2: Activity Hierarchy Setup")
    st.write("Select your training activities. Your **Primary Activity** acts as the immovable anchor that the AI adapts everything else around.")

    updated_activities = []
    for idx, act_val in enumerate(st.session_state.activity_slots):
        label = "🏆 Activity 1 (Primary Anchor - Immovable)" if idx == 0 else f"🥈 Activity {idx + 1}"
        default_idx = ALL_ACTIVITIES.index(act_val) if act_val in ALL_ACTIVITIES else 0
        selected_act = st.selectbox(label, ALL_ACTIVITIES, index=default_idx, key=f"act_slot_{idx}")
        updated_activities.append(selected_act)

    st.session_state.activity_slots = updated_activities

    col_act1, col_act2 = st.columns([1, 3])
    with col_act1:
        if st.button("➕ Add Another Activity"):
            st.session_state.activity_slots.append("Running & Cardio")
            st.rerun()
    with col_act2:
        if len(st.session_state.activity_slots) > 2:
            if st.button("➖ Remove Last Activity"):
                st.session_state.activity_slots.pop()
                st.rerun()

    st.markdown("---")
    if st.button("Create Account & Access Dashboard", type="primary", use_container_width=True):
        if email and name and password:
            st.session_state.user_profile = {
                "name": name, 
                "email": email, 
                "primary_anchor": st.session_state.activity_slots[0],
                "activities": st.session_state.activity_slots
            }
            st.session_state.user_authenticated = True
            st.rerun()
        else:
            st.error("Please complete all account fields.")
    st.stop()

# -----------------------------------------------------------------------------
# 2. MAIN APPLICATION (AUTHENTICATED)
# -----------------------------------------------------------------------------
profile = st.session_state.user_profile
st.sidebar.title(f"⚡ {profile.get('name', 'Athlete')}")
st.sidebar.markdown(f"**Primary Anchor:** 🔴 {profile.get('primary_anchor', 'Primary')}")

st.sidebar.markdown("**Your Activity Hierarchy:**")
for i, act in enumerate(profile.get("activities", []), 1):
    icon = "🔴 (Anchor)" if i == 1 else "🔵"
    st.sidebar.markdown(f"{i}. {icon} {act}")

if st.sidebar.button("Log Out / Reset Account"):
    st.session_state.user_authenticated = False
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
# TAB 1: TODAY'S CHECK-IN
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
