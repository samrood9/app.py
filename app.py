import streamlit as st
import json
import urllib.request
import urllib.error

# -----------------------------------------------------------------------------
# APP CONFIGURATION & STYLING
# -----------------------------------------------------------------------------
st.set_page_config(
    page_title="Adaptive Athletic Load Copilot",
    page_icon="⚡",
    layout="wide"
)

st.title("⚡ Adaptive Load Copilot")
st.caption("Democratized Sports Science & Dynamic Workout Adjustments for Athletes")

# -----------------------------------------------------------------------------
# SIDEBAR: 2-WEEK ROLLING SCHEDULE & ANCHOR MANAGEMENT
# -----------------------------------------------------------------------------
st.sidebar.header("🗓️ 2-Week Routine & Match Anchors")
st.sidebar.write("Set your default schedule and fixed fixtures below.")

current_week = st.sidebar.radio("Active Week", ["Week 1", "Week 2"])
day_of_week = st.sidebar.selectbox(
    "Day of Week",
    ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
)

DEFAULT_SCHEDULE = {
    "Week 1": {
        "Monday": {"name": "Push (Chest/Shoulders/Triceps)", "type": "Gym", "duration": 60, "exercises": ["Barbell Bench Press (4x8)", "Overhead DB Press (3x10)", "Incline DB Flyes (3x12)", "Tricep Dips (3x12)"]},
        "Tuesday": {"name": "Lower Body Power & Plyos", "type": "Gym", "duration": 60, "exercises": ["Heavy Barbell Back Squat (4x6)", "Depth Box Jumps (3x5)", "Romanian Deadlift (3x8)", "Walking Lunges (3x12)"]},
        "Wednesday": {"name": "Rest & Active Recovery", "type": "Rest", "duration": 30, "exercises": ["Light Foam Rolling & Stretching"]},
        "Thursday": {"name": "Pull & Core", "type": "Gym", "duration": 60, "exercises": ["Barbell Deadlift (4x5)", "Lat Pulldowns (3x10)", "Seated Cable Rows (3x10)", "Hanging Leg Raises (3x15)"]},
        "Friday": {"name": "Tempo Run (6km @ 4:45/km)", "type": "Run", "duration": 45, "exercises": ["6km Outdoor Tempo Run"]},
        "Saturday": {"name": "Pitch Match Day (90 mins)", "type": "Match", "duration": 90, "exercises": ["Competitive Match Play"]},
        "Sunday": {"name": "Full Body Flush & Mobility", "type": "Recovery", "duration": 45, "exercises": ["Low-Intensity Bike & Hip Mobility"]},
    },
    "Week 2": {
        "Monday": {"name": "Upper Body Hypertrophy", "type": "Gym", "duration": 60, "exercises": ["Incline Barbell Bench (4x8)", "Pull-ups (4xMax)", "DB Shoulder Press (3x10)", "Face Pulls (3x15)"]},
        "Tuesday": {"name": "Lower Body Hypertrophy", "type": "Gym", "duration": 60, "exercises": ["Leg Press (4x10)", "Bulgarian Split Squats (3x8/leg)", "Hamstring Curls (3x12)", "Calf Raises (4x15)"]},
        "Wednesday": {"name": "Pitch Training Session", "type": "Match", "duration": 75, "exercises": ["Team Tactical Drills & Small-Sided Games"]},
        "Thursday": {"name": "Push / Pull Combo", "type": "Gym", "duration": 60, "exercises": ["Dumbbell Bench Press (3x10)", "Bent Over Rows (3x10)", "Cable Lateral Raises (3x15)", "Bicep Curls (3x12)"]},
        "Friday": {"name": "Pre-Match Shakeout Run", "type": "Run", "duration": 30, "exercises": ["3km Light Shakeout + Strides"]},
        "Saturday": {"name": "Pitch Match Day (90 mins)", "type": "Match", "duration": 90, "exercises": ["Competitive Match Play"]},
        "Sunday": {"name": "Rest Day", "type": "Rest", "duration": 0, "exercises": ["Complete Rest"]},
    }
}

scheduled_today = DEFAULT_SCHEDULE[current_week][day_of_week]

st.sidebar.subheader("📍 Upcoming Fixture Anchor")
fixture_days = st.sidebar.slider("Days Until Next Match/Race:", 0.0, 7.0, 1.5, step=0.5)

# -----------------------------------------------------------------------------
# MAIN INTERFACE: 2-COLUMN LAYOUT
# -----------------------------------------------------------------------------
col_input, col_output = st.columns([1, 1], gap="large")

with col_input:
    st.header("📝 Daily 30-Second Check-In")
    st.info(f"**Scheduled Today ({current_week} - {day_of_week}):** {scheduled_today['name']} ({scheduled_today['duration']} mins)")

    energy_score = st.slider(
        "1. Systemic Energy & Recovery Score (1 = Battered, 10 = Peak Performance)",
        min_value=1,
        max_value=10,
        value=6
    )

    st.write("2. Flag Localized Joint & Muscle Strain (Select any affected areas)")
    
    lower_body_areas = [
        "Knees / Patellar", "Hamstrings", "Quadriceps", 
        "Calves / Achilles", "Groin / Adductors", "Shins", "Ankles", "Glutes / Hips"
    ]
    upper_body_areas = [
        "Shoulders / Rotator Cuff", "Upper Back / Lats", "Low Back", 
        "Chest", "Triceps / Biceps", "Forearms / Elbows", "Core / Abs"
    ]

    flagged_lower = st.multiselect("Lower Body & Joints", lower_body_areas)
    flagged_upper = st.multiselect("Upper Body & Core", upper_body_areas)
    flagged_all = flagged_lower + flagged_upper

    available_time = st.slider(
        "3. Available Time Today (Minutes)",
        min_value=15,
        max_value=120,
        value=45,
        step=15
    )

    btn_generate = st.button("⚡ Generate Today's Adapted Session", type="primary", use_container_width=True)

# -----------------------------------------------------------------------------
# GEMINI API INTEGRATION FUNCTION
# -----------------------------------------------------------------------------
def get_ai_recommendation(scheduled, energy, flagged, time_avail, match_in_days):
    api_key = st.secrets.get("GEMINI_API_KEY", "")
    if not api_key:
        return {"error": "GEMINI_API_KEY is missing from Streamlit Secrets."}

    url = f"
