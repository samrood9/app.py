import streamlit as st

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

# Week selector for the 14-day rolling cycle
current_week = st.sidebar.radio("Active Week", ["Week 1", "Week 2"])
day_of_week = st.sidebar.selectbox(
    "Day of Week",
    ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
)

# Mock Default Database for 14-Day Cycle
DEFAULT_SCHEDULE = {
    "Week 1": {
        "Monday": {"name": "Push (Chest/Shoulders/Triceps)", "type": "Gym", "duration": 60},
        "Tuesday": {"name": "Lower Body Power & Plyos", "type": "Gym", "duration": 60},
        "Wednesday": {"name": "Rest & Active Recovery", "type": "Rest", "duration": 30},
        "Thursday": {"name": "Pull & Core", "type": "Gym", "duration": 60},
        "Friday": {"name": "Tempo Run (6km @ 4:45/km)", "type": "Run", "duration": 45},
        "Saturday": {"name": "Pitch Match Day (90 mins)", "type": "Match", "duration": 90},
        "Sunday": {"name": "Full Body Flush & Mobility", "type": "Recovery", "duration": 45},
    },
    "Week 2": {
        "Monday": {"name": "Upper Body Hypertrophy", "type": "Gym", "duration": 60},
        "Tuesday": {"name": "Lower Body Hypertrophy", "type": "Gym", "duration": 60},
        "Wednesday": {"name": "Pitch Training Session", "type": "Match", "duration": 75},
        "Thursday": {"name": "Push / Pull Combo", "type": "Gym", "duration": 60},
        "Friday": {"name": "Pre-Match Shakeout Run", "type": "Run", "duration": 30},
        "Saturday": {"name": "Pitch Match Day (90 mins)", "type": "Match", "duration": 90},
        "Sunday": {"name": "Rest Day", "type": "Rest", "duration": 0},
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

    # 1. Energy & Systemic Recovery
    energy_score = st.slider(
        "1. Systemic Energy & Recovery Score (1 = Battered, 10 = Peak Performance)",
        min_value=1,
        max_value=10,
        value=6
    )

    # 2. Expanded Body Area Selection
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

    # 3. Available Time
    available_time = st.slider(
        "3. Available Time Today (Minutes)",
        min_value=15,
        max_value=120,
        value=45,
        step=15
    )

    btn_generate = st.button("⚡ Generate Today's Adapted Session", type="primary", use_container_width=True)

with col_output:
    st.header("🎯 Session Advisory & Workout Output")
    
    if btn_generate:
        # Mock Decision Engine logic to test UI behavior before connecting Gemini API
        st.subheader("Status & Action Plan")
        
        if energy_score <= 3 or fixture_days < 1.0:
            st.error("🚨 **TIER 2: Schedule Pivot Triggered**")
            st.write("**Reason:** High systemic fatigue or match day within <24h.")
            st.markdown("""
            * **Default Scheduled:** Lower Body Heavy Session
            * **AI Recommendation:** Shift heavy lower body work to post-fixture window. Today is converted to an upper body active pump & joint mobility circuit.
            """)
        elif len(flagged_all) > 0 or fixture_days <= 2.0:
            st.warning("⚠️ **TIER 1: Micro-Swap & Taper Triggered**")
            st.write(f"**Reason:** Strain flagged in **{', '.join(flagged_all) if flagged_all else 'None'}** with a fixture in {fixture_days} days.")
            
            st.markdown("### Today's Modified Session Plan")
            st.markdown(f"⏱️ **Target Duration:** {available_time} Minutes")
            
            st.markdown("""
            1. **Hack Squat / Leg Press (Machine)**  
               *3 sets x 8 reps* *(Swapped from Heavy Barbell Squats to reduce knee shear & lumbar load)* `[MODIFIED]`
            2. **Romanian Deadlifts (RDL)**  
               *2 sets x 8 reps* *(Reduced volume by 1 set for 36h match taper)* `[MODIFIED]`
            3. **Seated Calf Raises & Knee Isometrics**  
               *3 sets x 45s holds* *(Replaced explosive depth jumps to soothe patellar strain)* `[MODIFIED]`
            """)
        else:
            st.success("🟢 **TIER 0: Green Light - Full Session Approved**")
            st.write("**Reason:** High readiness, no joint warnings, match day >48h out.")
            st.write(f"Proceed with default session: **{scheduled_today['name']}**")

        st.divider()
        
        # Action Buttons: Preservation of User Autonomy
        col_btn1, col_btn2 = st.columns(2)
        with col_btn1:
            st.button("✅ Accept AI Adaptation", use_container_width=True)
        with col_btn2:
            st.button("⚠️ Override & Do Default", use_container_width=True)
    else:
        st.info("Complete the 3-step check-in on the left and click **Generate Today's Adapted Session** to see the engine in action.")
