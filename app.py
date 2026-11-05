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

# Initialize persistent session state
if "user_authenticated" not in st.session_state:
    st.session_state.user_authenticated = False
if "user_profile" not in st.session_state:
    st.session_state.user_profile = {}
if "custom_workouts" not in st.session_state:
    st.session_state.custom_workouts = {
        "Lower Body Power": ["Barbell Back Squat (4x6)", "Romanian Deadlift (3x8)", "Depth Box Jumps (3x5)", "Walking Lunges (3x12)"],
        "Upper Body Push": ["Bench Press (4x8)", "Overhead DB Press (3x10)", "Incline DB Flyes (3x12)", "Tricep Dips (3x12)"],
        "Pull & Core": ["Deadlift (4x5)", "Lat Pulldowns (3x10)", "Seated Rows (3x10)", "Hanging Leg Raises (3x15)"],
        "Tempo Run": ["6km Outdoor Run @ Target Pace"]
    }
if "calendar_events" not in st.session_state:
    today_str = str(datetime.date.today())
    next_sat_str = str(datetime.date.today() + datetime.timedelta(days=(5 - datetime.date.today().weekday()) % 7))
    st.session_state.calendar_events = {
        today_str: {"type": "Gym", "workout_name": "Lower Body Power", "color": "🔵"},
        next_sat_str: {"type": "Match", "workout_name": "Competitive Pitch Match (90 mins)", "color": "🔴"}
    }

# -----------------------------------------------------------------------------
# 1. ONBOARDING & SIGN-UP FLOW
# -----------------------------------------------------------------------------
if not st.session_state.user_authenticated:
    st.title("⚡ Welcome to Athletic Load Copilot")
    st.caption("Democratized Sports Science & Dynamic Workout Adjustments for Athletes")

    st.subheader("Step 1: Account Setup")
    with st.form("onboarding_form"):
        name = st.text_input("First Name")
        email = st.text_input("Email Address")
        sport = st.selectbox("Primary Sport / Focus", ["Football / Soccer", "Rugby", "Hyrox / Functional Fitness", "Running", "General Strength"])
        
        st.markdown("---")
        st.subheader("Step 2: Define Your Initial Custom Workouts")
        st.write("Set up at least one default workout you like to do in the gym:")
        workout_title = st.text_input("Workout Name (e.g., Heavy Leg Day)", value="My Primary Gym Split")
        ex1 = st.text_input("Exercise 1", value="Barbell Squat (4x6)")
        ex2 = st.text_input("Exercise 2", value="Romanian Deadlift (3x8)")
        ex3 = st.text_input("Exercise 3", value="Leg Press (3x10)")

        submit_onboarding = st.form_submit_button("Create Account & Enter Dashboard", type="primary")

        if submit_onboarding:
            if email and name:
                st.session_state.user_profile = {"name": name, "email": email, "sport": sport}
                st.session_state.custom_workouts[workout_title] = [e for e in [ex1, ex2, ex3] if e]
                st.session_state.user_authenticated = True
                st.rerun()
            else:
                st.error("Please provide both a name and an email address to continue.")
    st.stop()

# -----------------------------------------------------------------------------
# 2. MAIN APPLICATION (AUTHENTICATED)
# -----------------------------------------------------------------------------
st.sidebar.title(f"⚡ Hello, {st.session_state.user_profile.get('name', 'Athlete')}!")
st.sidebar.caption(f"Sport Focus: {st.session_state.user_profile.get('sport', 'General')}")

if st.sidebar.button("Log Out / Reset Account"):
    st.session_state.user_authenticated = False
    st.rerun()

tab_checkin, tab_calendar, tab_library = st.tabs([
    "⚡ Today's Dynamic Check-In", 
    "📅 Dynamic Calendar & Fixtures", 
    "⚙️ Custom Workout Library"
])

# -----------------------------------------------------------------------------
# TAB 1: TODAY'S DYNAMIC CHECK-IN
# -----------------------------------------------------------------------------
with tab_checkin:
    col_input, col_output = st.columns([1, 1], gap="large")
    
    today_date = datetime.date.today()
    today_key = str(today_date)
    today_event = st.session_state.calendar_events.get(today_key, {"type": "Rest", "workout_name": "Rest & Active Recovery", "color": "⚪"})

    # Auto-calculate distance to nearest upcoming MATCH anchor on calendar
    upcoming_matches = []
    for d_str, ev in st.session_state.calendar_events.items():
        ev_date = datetime.datetime.strptime(d_str, "%Y-%m-%d").date()
        if ev["type"] == "Match" and ev_date >= today_date:
            days_diff = (ev_date - today_date).days
            upcoming_matches.append(days_diff)
    
    nearest_match_days = min(upcoming_matches) if upcoming_matches else 99.0

    with col_input:
        st.header("📝 Daily 30-Second Check-In")
        
        st.info(f"**Scheduled Today ({today_key}):** {today_event['color']} {today_event['workout_name']}")
        if nearest_match_days < 99:
            st.caption(f"📍 **Detected Match Anchor:** Pitch Fixture scheduled in **{nearest_match_days} days**")
        else:
            st.caption("📍 **Detected Match Anchor:** No upcoming pitch fixtures logged on calendar.")

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
                st.write("You have a rest day scheduled on your calendar today. Take time for hydration and recovery!")
            else:
                current_exercises = st.session_state.custom_workouts.get(today_event['workout_name'], [today_event['workout_name']])
                
                # API Call Function
                api_key = st.secrets.get("GEMINI_API_KEY", "")
                if not api_key:
                    st.error("GEMINI_API_KEY missing from Streamlit Secrets.")
                else:
                    endpoint = "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent"
                    url = f"{endpoint}?key={api_key}"
                    
                    prompt = (
                        "You are an elite sports scientist and adaptive S&C coach.\n"
                        f"USER WORKOUT TODAY: {today_event['workout_name']}\n"
                        f"USER CUSTOM EXERCISES: {json.dumps(current_exercises)}\n"
                        f"AVAILABLE TIME: {available_time} mins\n"
                        f"ENERGY SCORE: {energy_score}/10\n"
                        f"FLAGGED SORENESS: {json.dumps(flagged_all)}\n"
                        f"DAYS UNTIL NEXT PITCH MATCH ANCHOR: {nearest_match_days} days\n\n"
                        "LOGIC: Tier 0 = Green Light (High energy, no issues). Tier 1 = Micro-swaps (flagged joints or match 24-48h out). Tier 2 = Session Pivot (energy <=3 or match <24h out).\n"
                        "Return ONLY a raw JSON object with keys: tier_applied, status_headline, rationale, adapted_workout (list of objects with exercise, sets_reps, notes, is_modified)."
                    )
                    
                    payload = {
                        "contents": [{"parts": [{"text": prompt}]}],
                        "generationConfig": {"response_mime_type": "application/json"}
                    }
                    
                    req = urllib.request.Request(url, data=json.dumps(payload).encode("utf-8"), headers={"Content-Type": "application/json"})
                    
                    with st.spinner("Analyzing joint readiness & fixture proximity..."):
                        try:
                            with urllib.request.urlopen(req) as resp:
                                res_json = json.loads(resp.read().decode("utf-8"))
                                raw_text = res_json["candidates"][0]["content"]["parts"][0]["text"]
                                ai_data = json.loads(raw_text)
                                
                                tier = ai_data.get("tier_applied", "TIER_0")
                                if tier == "TIER_0":
                                    st.success(f"🟢 **{tier}: Green Light - Full Session Approved**")
                                elif tier == "TIER_1":
                                    st.warning(f"⚠️ **{tier}: Micro-Swap & Taper Triggered**")
                                else:
                                    st.error(f"🚨 **{tier}: Schedule Pivot Triggered**")
                                
                                st.subheader(ai_data.get("status_headline", ""))
                                st.write(f"**Rationale:** {ai_data.get('rationale', '')}")
                                st.divider()
                                
                                st.markdown(f"### 📋 Adapted Session Plan ({available_time} Mins)")
                                for idx, item in enumerate(ai_data.get("adapted_workout", []), 1):
                                    badge = " `[MODIFIED]`" if item.get("is_modified") else ""
                                    st.markdown(f"**{idx}. {item.get('exercise')}{badge}**")
                                    st.markdown(f"* {item.get('sets_reps')} — *{item.get('notes')}*")
                                
                                st.divider()
                                col_b1, col_b2 = st.columns(2)
                                col_b1.button("✅ Accept AI Adaptation", use_container_width=True)
                                col_b2.button("⚠️ Override & Do Default", use_container_width=True)
                        except Exception as e:
                            st.error(f"Error connecting to AI engine: {str(e)}")
        else:
            st.info("Complete the check-in on the left to analyze today's session.")

# -----------------------------------------------------------------------------
# TAB 2: DYNAMIC CALENDAR &
