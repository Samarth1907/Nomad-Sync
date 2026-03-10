import streamlit as st
import requests
import os

st.set_page_config(page_title="Nomad-Sync", layout="wide")

if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False

# ═══════════════════════════════════════════════════════════════
# GLOBAL CSS — shared by both login and dashboard
# ═══════════════════════════════════════════════════════════════
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Playfair+Display:wght@600;700&family=Inter:wght@300;400;500;600&display=swap');

/* Reset */
.block-container { padding:0 !important; max-width:100% !important; }
header { visibility:hidden; }
[data-testid="stAppViewContainer"] { background:transparent !important; }
[data-testid="stHeader"] { background:transparent !important; }
.stApp { background:transparent !important; }
[data-testid="collapsedControl"] { display:none; }
section[data-testid="stSidebar"] { display:none; }

/* ── LOGIN SLIDESHOW ── */
#bg-slideshow {
    position:fixed; top:0; left:0; width:100vw; height:100vh; z-index:-2;
}
.slide {
    position:absolute; width:100%; height:100%;
    background-size:cover; background-position:center;
    opacity:0; animation:fadeSlide 30s infinite;
}
.slide:nth-child(1){ background-image:url("https://images.unsplash.com/photo-1507525428034-b723cf961d3e?q=80&w=2000"); animation-delay:0s; }
.slide:nth-child(2){ background-image:url("https://images.unsplash.com/photo-1476514525535-07fb3b4ae5f1?q=80&w=2000"); animation-delay:5s; }
.slide:nth-child(3){ background-image:url("https://images.unsplash.com/photo-1506929113675-b55f9d393543?q=80&w=2000"); animation-delay:10s; }
.slide:nth-child(4){ background-image:url("https://images.unsplash.com/photo-1469854523086-cc02fe5d8800?q=80&w=2000"); animation-delay:15s; }
.slide:nth-child(5){ background-image:url("https://images.unsplash.com/photo-1530789253388-582c481c54b0?q=80&w=2000"); animation-delay:20s; }
.slide:nth-child(6){ background-image:url("https://images.unsplash.com/photo-1504150558240-0b4fd8946624?q=80&w=2000"); animation-delay:25s; }

@keyframes fadeSlide {
    0%{opacity:0;} 5%{opacity:1;} 16%{opacity:1;} 21%{opacity:0;} 100%{opacity:0;}
}

.overlay { position:fixed; top:0; left:0; width:100vw; height:100vh; background:rgba(0,0,0,0.35); z-index:-1; }

/* ── LOGIN FORM ── */
[data-testid="stForm"] {
    background:rgba(255,255,255,0.12);
    backdrop-filter:blur(14px); -webkit-backdrop-filter:blur(14px);
    padding:55px 45px; border-radius:16px;
    max-width:460px; margin:12vh auto;
    border:1px solid rgba(255,255,255,0.25);
    box-shadow: 0 10px 40px rgba(0,0,0,0.35), inset 0 1px 1px rgba(255,255,255,0.3);
    text-align:center;
}
.hero-title { font-family:'Playfair Display',serif; font-size:3.2rem; color:white; margin-bottom:6px; }
.subtitle { color:rgba(255,255,255,0.75); letter-spacing:3px; font-size:0.75rem; margin-bottom:35px; }
label { color:white !important; font-weight:500; }
.stTextInput>div>div>input {
    background:rgba(255,255,255,0.15) !important;
    border:1px solid rgba(255,255,255,0.35) !important;
    border-radius:8px; padding:10px 12px; color:white !important;
}
input::placeholder { color:rgba(255,255,255,0.6); }

/* Login buttons */
[data-testid="stForm"] button[kind="secondaryFormSubmit"],
[data-testid="stForm"] button[data-testid="stFormSubmitButton"] {
    width:100%; background:linear-gradient(135deg,#d4af37,#f5d76e) !important;
    color:#111 !important; border:none !important; border-radius:8px !important;
    padding:10px 0 !important; font-weight:600; letter-spacing:1px;
    margin-top:15px; transition:all .25s ease;
}
.signup-link {
    color:rgba(255,255,255,0.7); font-size:0.85rem; margin-top:20px; text-align:center;
}
.stButton>button[key^="toggle"] {
    background: transparent !important;
    border: none !important;
    color: #f5d76e !important;
    font-weight: 600 !important;
    padding: 0 !important;
    margin-top: 15px !important;
    box-shadow: none !important;
}
.stButton>button[key^="toggle"]:hover {
    text-decoration: underline !important;
    color: #f5d76e !important;
}
</style>

<div id="bg-slideshow">
    <div class="slide"></div>
    <div class="slide"></div>
    <div class="slide"></div>
    <div class="slide"></div>
    <div class="slide"></div>
    <div class="slide"></div>
</div>
<div class="overlay"></div>
""", unsafe_allow_html=True)


# ═══════════════════════════════════════════════════════════════
# LOGIN / SIGNUP PAGE
# ═══════════════════════════════════════════════════════════════
if 'users' not in st.session_state:
    st.session_state.users = {"admin": "pramana"}
if 'view' not in st.session_state:
    st.session_state.view = "login"

if not st.session_state.logged_in:

    with st.form("auth_form"):
        st.markdown('<h1 class="hero-title">Nomad-Sync</h1>', unsafe_allow_html=True)
        st.markdown('<p class="subtitle">EXECUTIVE TRAVEL PLANNER</p>', unsafe_allow_html=True)

        if st.session_state.view == "login":
            user = st.text_input("Access Key", placeholder="Username (try: admin)")
            passw = st.text_input("Security Token", type="password", placeholder="Password (try: pramana)")
            submitted = st.form_submit_button("AUTHENTICATE")
            
            if submitted:
                if user in st.session_state.users and st.session_state.users[user] == passw:
                    st.session_state.logged_in = True
                    st.rerun()
                else:
                    st.error("Invalid credentials")
        else:
            new_user = st.text_input("Choose an Access Key", placeholder="Username")
            new_passw = st.text_input("Create Security Token", type="password", placeholder="Password")
            confirm_passw = st.text_input("Confirm Security Token", type="password", placeholder="Confirm Password")
            submitted = st.form_submit_button("CREATE ACCOUNT")
            
            if submitted:
                if new_user in st.session_state.users:
                    st.error("Username already exists")
                elif new_passw != confirm_passw:
                    st.error("Passwords do not match")
                elif len(new_user) == 0 or len(new_passw) == 0:
                    st.error("Fields cannot be empty")
                else:
                    st.session_state.users[new_user] = new_passw
                    st.success("Account created! You can now login.")
                    st.session_state.view = "login"
                    st.rerun()

    # Toggle link below the form
    if st.session_state.view == "login":
        if st.button("Don't have an account? Create one now →", key="toggle_signup"):
            st.session_state.view = "signup"
            st.rerun()
    else:
        if st.button("Already have an account? Login here →", key="toggle_login"):
            st.session_state.view = "login"
            st.rerun()

# ═══════════════════════════════════════════════════════════════
# DASHBOARD PAGE
# ═══════════════════════════════════════════════════════════════
else:
    # Override: hide login slideshow, inject dashboard background
    st.markdown("""
    <style>
    #bg-slideshow, .overlay { display:none !important; }

    /* Dashboard hero background */
    .dash-hero {
        position:fixed; top:0; left:0; width:100vw; height:100vh; z-index:-3;
        background-image:url('https://images.unsplash.com/photo-1542332213-9b5a5a3fad35?q=80&w=2000');
        background-size:cover; background-position:center;
    }
    .dash-grad {
        position:fixed; top:0; left:0; width:100vw; height:100vh; z-index:-2;
        background:linear-gradient(to bottom, rgba(0,0,0,0.05) 0%, rgba(0,0,0,0.75) 100%);
    }

    /* Fix all Streamlit containers to be transparent */
    [data-testid="stVerticalBlock"],
    [data-testid="stHorizontalBlock"],
    [data-testid="column"] {
        background:transparent !important;
    }

    /* Dashboard input overrides — dark labels, clean inputs */
    .stTextInput>div>div>input,
    .stNumberInput>div>div>input {
        background:rgba(255,255,255,0.95) !important;
        border:1px solid #ddd !important;
        border-radius:8px !important;
        color:#1a1a1a !important;
        font-weight:500;
    }
    label {
        color:rgba(255,255,255,0.9) !important;
        font-size:0.8rem !important;
        text-transform:uppercase;
        letter-spacing:1px;
        font-weight:600 !important;
    }

    /* EXPLORE NOW button override */
    .stButton>button {
        width:100%;
        background:linear-gradient(135deg,#d4af37,#f5d76e) !important;
        color:#111 !important;
        border:none !important;
        border-radius:50px !important;
        padding:10px 0 !important;
        font-weight:700;
        letter-spacing:1.5px;
        font-size:1rem;
        box-shadow:0 10px 25px rgba(0,0,0,0.3) !important;
        transition:all .25s ease;
    }
    .stButton>button:hover {
        transform:translateY(-2px);
        box-shadow:0 15px 35px rgba(0,0,0,0.4) !important;
    }
    </style>

    <div class="dash-hero"></div>
    <div class="dash-grad"></div>

    <div style="display:flex; justify-content:space-between; align-items:center; padding:30px 50px; color:white;">
        <div style="font-family:'Playfair Display',serif; font-size:2.2rem; font-weight:bold; letter-spacing:2px;">NomadSync</div>
        <div style="display:flex; gap:35px; font-size:0.9rem; font-weight:500; letter-spacing:1.5px;">
            <span>HOME</span>
            <span>DESTINATIONS</span>
            <span>TOURS</span>
            <span>CONTACT</span>
        </div>
    </div>

    <div style="text-align:center; color:white; margin-top:8vh; padding:0 20px;">
        <h1 style="font-size:5.5rem; font-family:'Playfair Display',serif; line-height:1.1; text-shadow:0 8px 30px rgba(0,0,0,0.5); margin-bottom:20px;">
            Let's visit the<br>beauty of the World
        </h1>
        <p style="font-size:1.15rem; text-shadow:0 2px 10px rgba(0,0,0,0.7); max-width:750px; margin:0 auto; line-height:1.7; font-weight:300;">
            Your private AI concierge uses advanced multi-agent reasoning to orchestrate perfect journeys — crafted just for you.
        </p>
    </div>
    """, unsafe_allow_html=True)

    # ── Search bar using native Streamlit columns ──
    st.markdown("<br>", unsafe_allow_html=True)
    c1, c2, c3, c4, c5 = st.columns([2, 1.5, 1, 1, 1.5])

    with c1: start = st.text_input("From & To", "Chennai, Mahabalipuram")
    with c2: interests_str = st.text_input("Themes", "nature, heritage")
    with c3: days = st.number_input("Days", 1, 20, 2)
    with c4: people = st.number_input("Guests", 1, 10, 2)
    with c5: explore_clicked = st.button("EXPLORE NOW")

    # Logout
    _, logout_col = st.columns([12, 1])
    with logout_col:
        if st.button("Logout"):
            st.session_state.logged_in = False
            st.rerun()

    # ── API Call ──
    if explore_clicked:
        interests = [i.strip() for i in interests_str.split(",") if i.strip()]
        parts = [p.strip() for p in start.split(",")]
        origin_val = parts[0] if len(parts) > 0 else "Chennai"
        dest_val = parts[1] if len(parts) > 1 else "Mahabalipuram"

        payload = {
            "origin": origin_val,
            "destination": dest_val,
            "num_days": days,
            "budget": 25000,
            "num_travelers": people,
            "interests": interests
        }

        with st.spinner("AI Agents are architecting your journey..."):
            try:
                backend_url = os.getenv("BACKEND_URL", "http://localhost:8000")
                r = requests.post(f"{backend_url}/api/plan-trip", json=payload)
                r.raise_for_status()
                data = r.json()
                st.success("Journey crafted successfully!")

                trip_id = data.get("trip_id")
                if trip_id:
                    dl1, dl2 = st.columns(2)
                    with dl1:
                        st.markdown(f"<a href='{backend_url}/api/download/{trip_id}/pdf' target='_blank'><button style='background:transparent;color:#d4af37;border:1px solid #d4af37;padding:8px 20px;border-radius:6px;cursor:pointer;'>📄 Download PDF</button></a>", unsafe_allow_html=True)
                    with dl2:
                        st.markdown(f"<a href='{backend_url}/api/download/{trip_id}/ics' target='_blank'><button style='background:transparent;color:#888;border:1px solid #888;padding:8px 20px;border-radius:6px;cursor:pointer;'>📅 Sync Calendar</button></a>", unsafe_allow_html=True)

                st.markdown("<br><hr><br>", unsafe_allow_html=True)

                plan = data.get("plan", {})
                for day in plan.get("days", []):
                    image_query = f"{dest_val},{plan.get('theme', 'nature')}"
                    unsplash_url = f"https://source.unsplash.com/1600x900/?{image_query}"
                    activity_html = "".join([
                        f"<li style='margin-bottom:8px;'><b>{act['time_slot']} - {act['name']}</b>: {act['description']}</li>"
                        for act in day.get("activities", [])
                    ])
                    st.markdown(f"""
                    <div style="background:white; padding:35px; border-radius:10px; margin-bottom:30px; box-shadow:0 10px 25px rgba(0,0,0,0.08);">
                        <p style="color:#d4af37; letter-spacing:2px; font-weight:600; font-size:0.8rem;">DAY {day.get('day_number'):02d} — {day.get('theme','EXPLORATION').upper()}</p>
                        <h2 style="font-family:'Playfair Display',serif; margin-top:0; color:#1a1a1a;">{day.get('title')}</h2>
                        <p style="color:#555; line-height:1.6;">{day.get('summary','Enjoy your curated activities for the day.')}</p>
                        <ul style="color:#333; font-size:0.95rem;">{activity_html}</ul>
                        <img src="{unsplash_url}" style="width:100%; height:350px; object-fit:cover; margin-top:20px; border-radius:6px;">
                    </div>
                    """, unsafe_allow_html=True)

            except requests.exceptions.RequestException as e:
                st.error(f"Error connecting to AI backend: {e}")