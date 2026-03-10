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
@import url('https://fonts.googleapis.com/css2?family=Playfair+Display:wght@500;600;700;800&family=Inter:wght@300;400;500;600&display=swap');

/* Reset and specific fixes */
.block-container { padding:0 !important; max-width:100% !important; }
header { visibility:hidden; }
[data-testid="stAppViewContainer"] { background:transparent !important; font-family: 'Inter', sans-serif; }
[data-testid="stHeader"] { background:transparent !important; }
.stApp { background:transparent !important; }
[data-testid="collapsedControl"] { display:none; }
section[data-testid="stSidebar"] { display:none; }
p, li, span, div { font-family: 'Inter', sans-serif; }

/* ── LOGIN SLIDESHOW ── */
#bg-slideshow {
    position:fixed; top:0; left:0; width:100vw; height:100vh; z-index:-2;
}
.slide {
    position:absolute; width:100%; height:100%;
    background-size:cover; background-position:center;
    opacity:0; animation:fadeSlide 36s infinite;
}
.slide:nth-child(1){ background-image:url("https://images.unsplash.com/photo-1507525428034-b723cf961d3e?q=80&w=2000"); animation-delay:0s; }
.slide:nth-child(2){ background-image:url("https://images.unsplash.com/photo-1476514525535-07fb3b4ae5f1?q=80&w=2000"); animation-delay:6s; }
.slide:nth-child(3){ background-image:url("https://images.unsplash.com/photo-1506929113675-b55f9d393543?q=80&w=2000"); animation-delay:12s; }
.slide:nth-child(4){ background-image:url("https://images.unsplash.com/photo-1469854523086-cc02fe5d8800?q=80&w=2000"); animation-delay:18s; }
.slide:nth-child(5){ background-image:url("https://images.unsplash.com/photo-1530789253388-582c481c54b0?q=80&w=2000"); animation-delay:24s; }
.slide:nth-child(6){ background-image:url("https://images.unsplash.com/photo-1504150558240-0b4fd8946624?q=80&w=2000"); animation-delay:30s; }

@keyframes fadeSlide {
    0%{opacity:0;} 5%{opacity:1;} 16%{opacity:1;} 21%{opacity:0;} 100%{opacity:0;}
}

.overlay { position:fixed; top:0; left:0; width:100vw; height:100vh; background: linear-gradient(135deg, rgba(15, 23, 42, 0.7) 0%, rgba(2, 6, 23, 0.85) 100%); z-index:-1; }

/* ── LOGIN FORM ── */
[data-testid="stForm"] {
    background:rgba(255,255,255,0.08); /* Lighter, more transparent */
    backdrop-filter: blur(20px) saturate(180%); -webkit-backdrop-filter: blur(20px) saturate(180%);
    padding:60px 50px; border-radius:24px;
    max-width:480px; margin:10vh auto;
    border: 1px solid rgba(255, 255, 255, 0.2);
    box-shadow: 0 30px 60px rgba(0,0,0,0.5), inset 0 1px 1px rgba(255,255,255,0.4);
    text-align:center;
}
.hero-title { font-family:'Playfair Display',serif; font-size:3.5rem; font-weight:800; color:#fff; margin-bottom:8px; text-shadow: 0 4px 15px rgba(0,0,0,0.4); tracking: -1px; }
.subtitle { color:#d4af37; letter-spacing:4px; font-size:0.8rem; font-weight: 600; margin-bottom:40px; text-transform: uppercase; }
[data-testid="stForm"] label { color:rgba(255,255,255,0.95) !important; font-weight:600; font-size: 0.85rem; letter-spacing: 0.5px; }
[data-testid="stForm"] .stTextInput>div>div>input {
    background:rgba(0, 0, 0, 0.25) !important;
    border:1px solid rgba(255,255,255,0.2) !important;
    border-radius:12px; padding:12px 16px; color:white !important;
    transition: all 0.3s ease;
}
[data-testid="stForm"] .stTextInput>div>div>input:focus {
    background:rgba(0, 0, 0, 0.45) !important;
    border-color: #d4af37 !important;
    box-shadow: 0 0 0 2px rgba(212, 175, 55, 0.3) !important;
}
input::placeholder { color:rgba(255,255,255,0.4); }

/* Login buttons */
[data-testid="stForm"] button[kind="secondaryFormSubmit"],
[data-testid="stForm"] button[data-testid="stFormSubmitButton"] {
    width:100%; height: 50px;
    background:linear-gradient(135deg, #dfc059 0%, #f9e28e 50%, #d4af37 100%) !important;
    background-size: 200% auto !important;
    color:#0a0a0a !important; border:none !important; border-radius:12px !important;
    padding:0 !important; font-weight:700; letter-spacing:2px; font-size:1rem;
    margin-top:25px; transition:all .4s cubic-bezier(0.4, 0, 0.2, 1);
    box-shadow: 0 8px 25px rgba(212, 175, 55, 0.3), inset 0 2px 2px rgba(255,255,255,0.6);
}
[data-testid="stForm"] button[data-testid="stFormSubmitButton"]:hover {
    transform:translateY(-3px);
    background-position: right center !important;
    box-shadow: 0 15px 35px rgba(212, 175, 55, 0.5), inset 0 2px 2px rgba(255,255,255,0.6);
}
[data-testid="stForm"] button[data-testid="stFormSubmitButton"]:active {
    transform:translateY(1px);
    box-shadow: 0 5px 15px rgba(212, 175, 55, 0.3);
}

.signup-link {
    color:rgba(255,255,255,0.6); font-size:0.9rem; margin-top:25px; text-align:center;
}
.stButton>button[key^="toggle"] {
    background: transparent !important;
    border: none !important;
    color: #dfc059 !important;
    font-weight: 500 !important;
    padding: 0 !important;
    margin-top: 20px !important;
    box-shadow: none !important;
    transition: color 0.3s ease;
}
.stButton>button[key^="toggle"]:hover {
    text-decoration: underline !important;
    color: #f9e28e !important;
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
            user = st.text_input("Access Key", placeholder="Username")
            passw = st.text_input("Security Token", type="password", placeholder="Password")
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

/* ── DASHBOARD ENHANCEMENTS ── */
    /* Dashboard input overrides — better padding, rounded, modern shadows */
    .stTextInput>div>div>input,
    .stNumberInput>div>div>input {
        background:rgba(255,255,255,0.85) !important;
        backdrop-filter: blur(10px);
        border:1px solid rgba(255,255,255,0.3) !important;
        border-radius:12px !important;
        color:#000000 !important;
        font-weight:600;
        padding: 14px 16px !important;
        box-shadow: inset 0 2px 5px rgba(0,0,0,0.05), 0 4px 15px rgba(0,0,0,0.1) !important;
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
    }
    .stTextInput>div>div>input:focus,
    .stNumberInput>div>div>input:focus {
        background: #ffffff !important;
        box-shadow: 0 4px 20px rgba(223, 192, 89, 0.4) !important;
        border-color: #dfc059 !important;
        transform: translateY(-1px);
    }
    label {
        color:rgba(255,255,255,0.95) !important;
        font-size:0.8rem !important;
        text-transform:uppercase;
        letter-spacing:1.5px;
        font-weight:700 !important;
        margin-bottom: 8px !important;
        text-shadow: 0 2px 4px rgba(0,0,0,0.5);
    }

    /* EXPLORE NOW button override - ultra premium */
    .stButton>button {
        width:100%;
        height: 54px;
        background:linear-gradient(135deg, #dfc059 0%, #f9e28e 50%, #d4af37 100%) !important;
        background-size: 200% auto !important;
        color:#0a0a0a !important;
        border:none !important;
        border-radius:12px !important;
        padding:0 24px !important;
        font-weight:800;
        letter-spacing:2px;
        font-size:1.05rem;
        box-shadow: 0 8px 25px rgba(212, 175, 55, 0.3), inset 0 2px 2px rgba(255,255,255,0.6) !important;
        transition:all .4s cubic-bezier(0.4, 0, 0.2, 1);
        display: flex;
        justify-content: center;
        align-items: center;
        margin-top: 31px !important; /* aligns button with inputs */
    }
    .stButton>button:hover {
        transform:translateY(-3px);
        background-position: right center !important;
        box-shadow: 0 15px 35px rgba(212, 175, 55, 0.5), inset 0 2px 2px rgba(255,255,255,0.6) !important;
    }
    .stButton>button:active {
        transform:translateY(1px);
        box-shadow: 0 5px 15px rgba(212, 175, 55, 0.3) !important;
    }
    </style>

<div class="dash-hero"></div>
<div class="dash-grad"></div>

<div style="display:flex; justify-content:space-between; align-items:center; padding:30px 50px; color:white;">
    <div style="font-family:'Playfair Display',serif; font-size:2.2rem; font-weight:800; letter-spacing:2px; text-shadow: 0 2px 10px rgba(0,0,0,0.6);">NomadSync</div>
    <div style="display:flex; gap:35px; font-size:0.9rem; font-weight:600; letter-spacing:1.5px; text-shadow: 0 1px 5px rgba(0,0,0,0.5);">
        <span style="cursor:pointer; transition: color 0.3s;" onmouseover="this.style.color='#f9e28e'" onmouseout="this.style.color='white'">HOME</span>
        <span style="cursor:pointer; transition: color 0.3s;" onmouseover="this.style.color='#f9e28e'" onmouseout="this.style.color='white'">DESTINATIONS</span>
        <span style="cursor:pointer; transition: color 0.3s;" onmouseover="this.style.color='#f9e28e'" onmouseout="this.style.color='white'">TOURS</span>
        <span style="cursor:pointer; transition: color 0.3s;" onmouseover="this.style.color='#f9e28e'" onmouseout="this.style.color='white'">CONTACT</span>
    </div>
</div>

<div style="text-align:center; color:white; margin-top:8vh; padding:0 20px;">
    <h1 style="font-size:5.5rem; font-family:'Playfair Display',serif; line-height:1.1; text-shadow:0 10px 40px rgba(0,0,0,0.6); margin-bottom:20px; font-weight: 800;">
        Let's visit the<br>beauty of the World
    </h1>
    <p style="font-size:1.25rem; text-shadow:0 4px 20px rgba(0,0,0,0.8); max-width:800px; margin:0 auto; line-height:1.7; font-weight:500; letter-spacing: 0.5px; color: rgba(255,255,255,0.95);">
        Your private AI concierge uses advanced multi-agent reasoning to orchestrate perfect journeys — crafted just for you.
    </p>
</div>
    """, unsafe_allow_html=True)

    # ── Search bar using native Streamlit columns with refined widths ──
    st.markdown("<br><br>", unsafe_allow_html=True)
    
    # Wrap inputs in a slightly tinted container row so they pop against the background
    st.markdown("""
        <div style="background: rgba(0,0,0,0.3); backdrop-filter: blur(10px); -webkit-backdrop-filter: blur(10px); 
                    border-radius: 20px; padding: 20px 30px; border: 1px solid rgba(255,255,255,0.1); 
                    box-shadow: 0 20px 40px rgba(0,0,0,0.4); max-width: 1400px; margin: 0 auto;">
    """, unsafe_allow_html=True)

    c1, c2, c3, c4, c5 = st.columns([2.5, 2, 1, 1, 1.5], gap="medium")

    with c1: start = st.text_input("From & To", "Chennai, Mahabalipuram", placeholder="E.g., Paris, Rome")
    with c2: interests_str = st.text_input("Themes", "nature, heritage", placeholder="E.g., art, food, culture")
    with c3: days = st.number_input("Days", 1, 20, 2)
    with c4: people = st.number_input("Guests", 1, 10, 2)
    with c5: explore_clicked = st.button("EXPLORE NOW")

    st.markdown("</div>", unsafe_allow_html=True)

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

        # Add a custom loading overlay style just before spinning
        st.markdown("""
        <style>
        .stSpinner > div > div {
            border-top-color: #dfc059 !important;
            border-left-color: #dfc059 !important;
        }
        .stSpinner {
            margin-top: 40px;
            backdrop-filter: blur(8px);
            padding: 20px;
            border-radius: 16px;
            background: rgba(0,0,0,0.5);
            color: #fff;
            font-weight: 500;
            letter-spacing: 1px;
            border: 1px solid rgba(255,255,255,0.1);
        }
        </style>
        """, unsafe_allow_html=True)

        with st.spinner("AI Agents are architecting your journey..."):
            try:
                backend_url = os.getenv("BACKEND_URL", "http://localhost:8000")
                r = requests.post(f"{backend_url}/api/plan-trip", json=payload)
                r.raise_for_status()
                data = r.json()
                
                # Replace success message with a styled banner
                st.markdown("""
                <div style="background: linear-gradient(135deg, rgba(223,192,89,0.2) 0%, rgba(249,226,142,0.1) 100%); 
                            backdrop-filter: blur(10px); -webkit-backdrop-filter: blur(10px);
                            border-left: 5px solid #dfc059; padding: 25px 30px; border-radius: 12px; 
                            margin: 40px 0 30px 0; display:flex; align-items:center;
                            box-shadow: 0 10px 30px rgba(0,0,0,0.2), inset 0 1px 1px rgba(255,255,255,0.2);
                            border: 1px solid rgba(255,255,255,0.1);">
                    <div style="font-size: 2.2rem; margin-right: 20px;">✨</div>
                    <div>
                        <h3 style="margin:0; color:white; font-family:'Playfair Display',serif; font-size:1.6rem; font-weight:700;">Journey Crafted Successfully</h3>
                        <p style="margin:6px 0 0 0; color:rgba(255,255,255,0.85); font-size:1rem;">Your personalized <b>%s-day</b> itinerary is ready to explore.</p>
                    </div>
                </div>
                """ % (days), unsafe_allow_html=True)

                trip_id = data.get("trip_id")
                if trip_id:
                    dl1, dl2 = st.columns(2)
                    with dl1:
                        st.markdown(f"<a href='{backend_url}/api/download/{trip_id}/pdf' target='_blank'><button style='background:transparent;color:#d4af37;border:1px solid #d4af37;padding:8px 20px;border-radius:6px;cursor:pointer;'>📄 Download PDF</button></a>", unsafe_allow_html=True)
                    with dl2:
                        st.markdown(f"<a href='{backend_url}/api/download/{trip_id}/ics' target='_blank'><button style='background:transparent;color:#888;border:1px solid #888;padding:8px 20px;border-radius:6px;cursor:pointer;'>📅 Sync Calendar</button></a>", unsafe_allow_html=True)

                st.markdown("<br><hr style='border: 1px solid rgba(255,255,255,0.15)'><br>", unsafe_allow_html=True)

                plan = data.get("plan", {})
                for day in plan.get("days", []):
                    image_query = f"{dest_val},{plan.get('theme', 'nature')}"
                    unsplash_url = f"https://source.unsplash.com/1600x900/?{image_query}"
                    activity_html = "".join([
                        f"<li style='margin-bottom:16px; font-size:1.05rem; display:flex; align-items:flex-start;'><span style='min-width:115px; font-weight:700; color:#dfc059; margin-right:15px; text-transform:uppercase; letter-spacing:1px; font-size:0.9rem; padding-top:2px;'>{act['time_slot']}</span> <span style='flex:1; background:rgba(0,0,0,0.03); padding:15px 20px; border-radius:10px; border-left:3px solid rgba(223,192,89,0.3); transition:all 0.3s;' onmouseover=\"this.style.background='rgba(0,0,0,0.05)';this.style.borderLeftColor='#dfc059'\" onmouseout=\"this.style.background='rgba(0,0,0,0.03)';this.style.borderLeftColor='rgba(223,192,89,0.3)'\"><b style='color:#111; font-size:1.15rem;'>{act['name']}</b><br><span style='color:#555; font-size:0.95rem; line-height:1.5; display:inline-block; margin-top:6px;'>{act['description']}</span></span></li>"
                        for act in day.get("activities", [])
                    ])
                    st.markdown(f"""
                    <div style="background:rgba(255,255,255,0.95); backdrop-filter:blur(15px); -webkit-backdrop-filter:blur(15px); padding:50px; border-radius:20px; margin-bottom:50px; box-shadow:0 20px 40px rgba(0,0,0,0.2), inset 0 1px 1px rgba(255,255,255,1); border:1px solid rgba(255,255,255,0.6); transform: translateY(0); transition: all 0.4s cubic-bezier(0.165, 0.84, 0.44, 1);" onmouseover="this.style.transform='translateY(-6px)'; this.style.boxShadow='0 30px 60px rgba(0,0,0,0.3), inset 0 1px 1px rgba(255,255,255,1)'" onmouseout="this.style.transform='translateY(0)'; this.style.boxShadow='0 20px 40px rgba(0,0,0,0.2), inset 0 1px 1px rgba(255,255,255,1)'">
                        <div style="display:flex; justify-content:space-between; border-bottom: 2px solid rgba(0,0,0,0.05); padding-bottom: 25px; margin-bottom: 30px;">
                            <div>
                                <p style="color:#dfc059; letter-spacing:3px; font-weight:800; font-size:0.9rem; margin-bottom:10px; display:inline-block; border-bottom: 2px solid #dfc059; padding-bottom: 6px;">DAY {day.get('day_number'):02d} — {day.get('theme','EXPLORATION').upper()}</p>
                                <h2 style="font-family:'Playfair Display',serif; margin-top:15px; color:#111; font-size:3rem; font-weight:800; letter-spacing: -0.5px; line-height: 1.1;">{day.get('title')}</h2>
                            </div>
                        </div>
                        <p style="color:#333; line-height:1.8; font-size: 1.2rem; margin-bottom: 40px; border-left: 4px solid #dfc059; padding-left: 24px; font-style: italic; font-weight: 400;">{day.get('summary','Enjoy your curated activities for the day.')}</p>
                        <ul style="color:#333; list-style-type: none; padding-left: 0;">{activity_html}</ul>
                        <div style="overflow: hidden; border-radius:14px; margin-top:40px; box-shadow: 0 15px 35px rgba(0,0,0,0.25);">
                            <img src="{unsplash_url}" style="width:100%; height:450px; object-fit:cover; transition: transform 0.8s ease;" onmouseover="this.style.transform='scale(1.04)'" onmouseout="this.style.transform='scale(1)'">
                        </div>
                    </div>
                    """, unsafe_allow_html=True)

            except requests.exceptions.RequestException as e:
                st.error(f"Error connecting to AI backend: {e}")