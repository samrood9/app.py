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

# Persistent Session State
if "user_authenticated" not in st.session_state:
    st.session_state.user_authenticated = False
if "user_profile" not in st.session_state:
    st.session_state.user_profile = {}
if "custom_workouts" not in st.session_state:
    st.session_state.custom_workouts = {
        "Leg Day & Lower Body": ["Barbell Squats (4x6)", "Romanian Deadlifts (3x8)", "Leg Press (3x10)"],
        "Push Split (Upper Body)": ["Bench Press (4x8)", "Overhead DB Press (3x10)", "Tricep Dips (3x12)"],
        "Pull & Core": ["Deadlifts (4x5)", "Lat Pulldowns (3x10)", "Seated Cable Rows (3x10)"],
        "Tempo Run": ["6km Outdoor Run @ Target Pace"]
    }
if "calendar_events" not in st.session_state:
    today_str = str(datetime.date.today())
    match_day_str = str(datetime.date.today() + datetime.timedelta(days=2))
    st.session_state.calendar_events = {
        today_str: {"type": "Gym", "workout_name": "Leg Day & Lower Body", "color": "🔵", "tier_level": "Secondary"},
        match_day_str: {"type": "Match", "workout_name": "League Match Fixture (90 mins)", "color": "🔴", "tier_level": "Primary Anchor"}
    }

# -----------------------------------------------------------------------------
# 1. ONBOARDING & HIERARCHY SELECTION
# -----------------------------------------------------------------------------
if not st.session_state.user_authenticated:
    st.title("⚡ Welcome to Athletic Load Copilot")
    st.caption("Democratized Sports Science & Dynamic Workout Adjustments for Athletes")

    st.subheader("Step 1: Account Setup & Activity Hierarchy")
    st.write("Define your training priority so the AI knows what to adapt around.")
    
    with st.form("onboarding_hierarchy_form"):
        name = st.text_input("First Name", value="Alex")
        email = st.text_input("Email Address", value="athlete@example.com")
        
        st.markdown("---")
        st.markdown("### 🏆 Activity Hierarchy Setup")
        
        primary_anchor = st.selectbox(
            "1. Primary Anchor (Non-Negotiable - Matches/Races take top priority)",
            ["Football / Soccer Match", "Rugby Fixture", "Hyrox Event / Race", "Marathon / Running Race", "Competitive Sport"]
        )
        
        secondary_exercise = st.selectbox(
            "2. Secondary Exercise Focus (Adapts around your Primary Anchor)",
            ["Gym / Strength Training", "Functional Fitness", "Resistance Training"]
        )
        
        tertiary_exercise = st.selectbox(
            "3. Tertiary Exercise Focus (Fills open training slots)",
            ["Running & Cardio", "Active Recovery / Swimming", "Mobility & Stretch", "None"]
        )

        st.markdown("---")
        st.subheader("Step 2: Define Your Initial Custom Gym Split")
        w_title = st.text_input("Custom Workout Name", value="Leg Day & Lower Body")
        ex1 = st.text_input("Exercise 1", value="Barbell Squats (4x6)")
        ex2 = st.text_input("Exercise 2", value="Romanian Deadlifts (3x8)")
        ex3 = st.text_input("Exercise 3", value="Leg Press (3x10)")

        submit_onboarding = st.form_submit_button("Create Account & Access Dashboard", type="primary")

        if submit_onboarding:
            if email and name:
                st.session_state.user_profile = {
                    "name": name, 
                    "email": email, 
                    "primary_anchor": primary_anchor,
                    "secondary": secondary_exercise,
                    "tertiary": tertiary_exercise
                }
                st.session_state.custom_workouts[w_title] = [e for e in [ex1, ex2, ex3] if e]
                st.session_state.user_authenticated = True
                st.rerun()
            else:
                st.error("Please provide both a name and an email address.")
    st.stop()

# -----------------------------------------------------------------------------
# 2. MAIN APPLICATION (AUTHENTICATED)
# -----------------------------------------------------------------------------
profile = st.session_state.user_profile
st.sidebar.title(f"⚡ {profile.get('name', 'Athlete')}")
st.sidebar.markdown(f"**Primary Anchor:** 🔴 {profile.get('primary_anchor', 'Match')}")
st.sidebar.markdown(f"**Secondary:** 🔵 {profile.get('secondary', 'Gym')}")
st.sidebar.markdown(f"**Tertiary:** 🟢 {profile.get('tertiary', 'Cardio')}")

if st.sidebar.button("Log Out / Reset Profile"):
    st.session_state.user_authenticated = False
    st.rerun()

tab_checkin, tab_calendar, tab_library = st.tabs([
    "⚡ Today's Check-In", 
    "📅 Calendar & Taper Zone", 
    "⚙️ Custom Workout Library"
])

# Helper: Find nearest upcoming match anchor
today_date = datetime.date.today()
today_key = str(today_date)
upcoming_matches = []
for d_str, ev in st.session_state.calendar_events.items():
    ev_date = datetime.datetime.strptime(d_str, "%Y-%m-%d").date()
    if ev["type"] == "Match" and ev_date >= today_date:
        days_diff = (ev_date - today_date).days
        upcoming_matches.append(days_diff)

nearest_match_days = min(upcoming_matches) if upcoming_matches else 99.0

# -----------------------------------------------------------------------------
# TAB 1: TODAY'S CHECK-IN
# -----------------------------------------------------------------------------
with tab_checkin:
    col_input, col_output = st.columns([1, 1], gap="large")
    today_event = st.session_state.calendar_events.get(today_key, {"type": "Rest", "workout_name": "Rest & Recovery", "color": "⚪"})

    with col_input:
        st.header("📝 Daily 30-Second Check-In")
        
        st.info(f"**Scheduled Today ({today_key}):** {today_event['color']} {today_event['workout_name']}")
        
        # Subtle Taper Notification Banner
        if 0.0 < nearest_match_days <= 2.0:
            st.warning(f"⚡ **Taper Zone Active:** {profile.get('primary_anchor', 'Match')} in {nearest_match_days:.1f} days.")
        elif nearest_match_days == 0.0:
            st.error("🔴 **MATCH DAY TODAY:** Prioritize fuel, warm-up, and match performance!")
        else:
            st.caption("📍 No primary match anchors detected within the next 48 hours.")

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
                st.write("Enjoy your active recovery day. Maintain hydration and low-impact movement!")
            else:
                current_exercises = st.session_state.custom_workouts.get(today_event['workout_name'], [today_event['workout_name']])
                
                api_key = st.secrets.get("GEMINI_API_KEY", "")
                if not api_key:
                    st.error("GEMINI_API_KEY is missing from Streamlit Secrets.")
                else:
                    endpoint = "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent"
                    url = f"{endpoint}?key={api_key}"
                    
                    prompt = (
                        "You are an elite sports scientist and adaptive S&C coach.\n"
                        f"PRIMARY ANCHOR SPORT: {profile.get('primary_anchor')}\n"
                        f"SCHEDULED WORKOUT TODAY: {today_event['workout_name']}\n"
                        f"TARGET EXERCISES: {json.dumps(current_exercises)}\n"
                        f"AVAILABLE TIME: {available_time} mins\n"
                        f"ENERGY SCORE: {energy_score}/10\n"
                        f"FLAGGED SORENESS: {json.dumps(flagged_all)}\n"
                        f"DAYS UNTIL NEXT PRIMARY ANCHOR: {nearest_match_days} days\n\n"
                        "LOGIC:\n"
                        "Tier 0 = Green Light (High energy, no joint issues, match >48h out).\n"
                        "Tier 1 = Micro-Swap/Taper (Joint strain or match 24-48h away -> Reduce volume 20-30%, swap high-shear lifts).\n"
                        "Tier 2 = Session Pivot (Energy <=3 or match <24h away -> Pivot to upper pump or active mobility).\n"
                        "Return ONLY raw JSON with keys: tier_applied, status_headline, rationale, adapted_workout (list of objects with exercise, sets_reps, notes, is_modified)."
                    )
                    
                    payload = {
                        "contents": [{"parts": [{"text": prompt}]}],
                        "generationConfig": {"response_mime_type": "application/json"}
                    }
                    
                    req = urllib.request.Request(url, data=json.dumps(payload).encode("utf-8"), headers={"Content-Type": "application/json"})
                    
                    with st.spinner("Calculating joint strain & anchor taper window..."):
                        try:
                            with urllib.request.urlopen(req) as resp:
                                res_json = json.loads(resp.read().decode("utf-8"))
                                raw_text = res_json["candidates"][0]["content"]["parts"][0]["text"]
                                ai_data = json.loads(raw_text)
                                
                                tier = ai_data.get("tier_applied", "TIER_0")
                                if tier == "TIER_0":
                                    st.success(f"🟢 **{tier}: Green Light - Session Approved**")
                                elif tier == "TIER_1":
                                    st.warning(f"⚠️ **{tier}: Micro-Swap & Taper Active**")
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
            st.info("Complete the check-in on the left to generate today's session.")

# -----------------------------------------------------------------------------
# TAB 2: CALENDAR & SUBTLE TAPER BANNER
# -----------------------------------------------------------------------------
with tab_calendar:
    st.header("📅 Dynamic Schedule & Calendar Hub")
    st.caption(f"Primary Anchor: **🔴 {profile.get('primary_anchor', 'Match Day')}** (Highest Priority)")

    col_cal_left, col_cal_right = st.columns([1, 1], gap="large")

    with col_cal_left:
        st.subheader("Add / Edit Event")
        selected_date = st.date_input("Select Date", datetime.date.today())
        date_str = str(selected_date)

        event_type = st.selectbox(
            "Event Category",
            [f"Primary Anchor ({profile.get('primary_anchor', 'Match')})", "Secondary (Gym Workout)", "Tertiary (Run / Cardio)", "Rest / Recovery"]
        )
        
        if "Primary Anchor" in event_type:
            e_type, e_color = "Match", "🔴"
            workout_choice = st.text_input("Match Details", value=f"Competitive {profile.get('primary_anchor', 'Match')}")
        elif "Secondary" in event_type:
            e_type, e_color = "Gym", "🔵"
            workout_choice = st.selectbox("Select Custom Gym Split", list(st.session_state.custom_workouts.keys()))
        elif "Tertiary" in event_type:
            e_type, e_color = "Run", "🟢"
            workout_choice = st.text_input("Cardio Details", value="Tempo Run / Conditioning")
        else:
            e_type, e_color = "Rest", "⚪"
            workout_choice = "Rest & Active Recovery"

        if st.button("📌 Add to Calendar", type="primary"):
            st.session_state.calendar_events[date_str] = {
                "type": e_type,
                "workout_name": workout_choice,
                "color": e_color
            }
            st.success(f"Added {e_color} {workout_choice} on {date_str}!")
            st.rerun()

    with col_cal_right:
        st.subheader("Logged Schedule & Taper Sub-Labels")
        if not st.session_state.calendar_events:
            st.write("No events logged.")
        else:
            sorted_events = sorted(st.session_state.calendar_events.items(), key=lambda x: x[0])
            
            # Find all match dates for calculation
            match_dates = [
                datetime.datetime.strptime(d_s, "%Y-%m-%d").date() 
                for d_s, ev in st.session_state.calendar_events.items() if ev["type"] == "Match"
            ]

            for d_str, ev in sorted_events:
                ev_d = datetime.datetime.strptime(d_str, "%Y-%m-%d").date()
                
                # Check if this day is within 48h (1 or 2 days prior) of a match date
                is_taper_zone = False
                hours_to_match = 0
                for m_d in match_dates:
                    diff_days = (m_d - ev_d).days
                    if 0 < diff_days <= 2:
                        is_taper_zone = True
                        hours_to_match = diff_days * 24
                        break

                c1, c2, c3 = st.columns([2, 4, 1])
                c1.write(f"**{d_str}**")
                
                # Render event title + subtle bank-holiday style sub-label
                taper_subtitle = f"\n*⚡ Taper Zone ({hours_to_match}h to {profile.get('primary_anchor', 'Match')})*" if is_taper_zone else ""
                c2.markdown(f"{ev['color']} **{ev['workout_name']}**{taper_subtitle}")
                
                if c3.button("🗑️", key=f"del_{d_str}"):
                    del st.session_state.calendar_events[d_str]
                    st.rerun()

# -----------------------------------------------------------------------------
# TAB 3: CUSTOM WORKOUT LIBRARY
# -----------------------------------------------------------------------------
with tab_library:
    st.header("⚙️ Custom Workout Library")
    st.write("Manage your secondary gym splits and tertiary cardio routines.")

    for w_name, ex_list in list(st.session_state.custom_workouts.items()):
        with st.expander(f"🏋️ {w_name}", expanded=False):
            st.write("**Exercises Included:**")
            for ex in ex_list:
                st.markdown(f"- {ex}")
            if st.button(f"Delete '{w_name}'", key=f"del_w_{w_name}"):
                del st.session_state.custom_workouts[w_name]
                st.rerun()

    st.markdown("---")
    st.subheader("➕ Add New Custom Routine")
    with st.form("new_w_form"):
        new_name = st.text_input("Routine Name")
        new_exs = st.text_area("Exercises (One per line)", value="Leg Press (3x10)\nHamstring Curls (3x12)\nCalf Raises (4x15)")
        if st.form_submit_button("Save Routine") and new_name:
            lines = [l.strip() for l in new_exs.split("\n") if l.strip()]
            st.session_state.custom_workouts[new_name] = lines
            st.success(f"Added '{new_name}' to library!")
            st.rerun()
