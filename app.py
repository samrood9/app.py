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

    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key={api_key}"

    prompt = f"""
    You are an elite sports scientist and adaptive S&C coach.
    
    INPUT DATA:
    - Scheduled Today: {scheduled['name']}
    - Default Target Exercises: {json.dumps(scheduled['exercises'])}
    - Planned Duration: {scheduled['duration']} mins
    - User Available Time Today: {time_avail} mins
    - User Systemic Energy Score: {energy}/10
    - Flagged Soreness/Joint Tightness: {json.dumps(flagged)}
    - Days Until Next Match/Race Anchor: {match_in_days} days

    LOGIC RULES:
    1. TIER 0 (Green Light): High energy (>=7), no flagged areas, match >48h out -> Keep scheduled session intact.
    2. TIER 1 (Micro-Swap/Taper): Flagged joint/muscle strain OR match 24-48h away -> Swap high-impact/high-shear lifts for safer alternatives (e.g. Heavy Back Squat -> Leg Press/Hack Squat if knees flagged; Plyos -> Isometrics), reduce volume by 20-30%.
    3. TIER 2 (Schedule Pivot): Energy <= 3 OR match <24h away -> Shift lower body/high-impact work away, replace today with upper body pump, joint mobility, or light active recovery.

    OUTPUT INSTRUCTIONS:
    Return ONLY a raw JSON object (no markdown surrounding ticks) matching this structure:
    {{
        "tier_applied": "TIER_0" | "TIER_1" | "TIER_2",
        "status_headline": "Short 1-sentence headline summarizing today's change",
        "rationale": "Clear sports science explanation behind the adaptations",
        "adapted_workout": [
            {{"exercise": "Exercise Name", "sets_reps": "3 sets x 8 reps", "notes": "Why modified or kept", "is_modified": true/false}}
        ]
    }}
    """

    payload = {
        "contents": [{"parts": [{"text": prompt}]}],
        "generationConfig": {"response_mime_type": "application/json"}
    }

    req = urllib.request.Request(
        url,
        data=json.dumps(payload).encode("utf-8"),
        headers={"Content-Type": "application/json"}
    )

    try:
        with urllib.request.urlopen(req) as response:
            res_body = response.read().decode("utf-8")
            res_json = json.loads(res_body)
            raw_text = res_json["candidates"][0]["content"]["parts"][0]["text"]
            return json.loads(raw_text)
    except Exception as e:
        return {"error": str(e)}

# -----------------------------------------------------------------------------
# OUTPUT DISPLAY
# -----------------------------------------------------------------------------
with col_output:
    st.header("🎯 Session Advisory & Workout Output")
    
    if btn_generate:
        with st.spinner("Connecting to Sports Science AI Engine..."):
            ai_data = get_ai_recommendation(
                scheduled_today, energy_score, flagged_all, available_time, fixture_days
            )
        
        if "error" in ai_data:
            st.error(f"API Error: {ai_data['error']}")
        else:
            tier = ai_data.get("tier_applied", "TIER_0")
            
            if tier == "TIER_0":
                st.success(f"🟢 **{tier}: Green Light - Full Session Approved**")
            elif tier == "TIER_1":
                st.warning(f"⚠️ **{tier}: Micro-Swap & Taper Triggered**")
            else:
                st.error(f"🚨 **{tier}: Schedule Pivot Triggered**")

            st.subheader(ai_data.get("status_headline", ""))
            st.write(f"**Sports Science Rationale:** {ai_data.get('rationale', '')}")
            
            st.divider()
            st.markdown(f"### 📋 Today's Session Plan ({available_time} Mins)")

            workout_list = ai_data.get("adapted_workout", [])
            for idx, item in enumerate(workout_list, 1):
                mod_badge = " `[MODIFIED]`" if item.get("is_modified") else ""
                st.
