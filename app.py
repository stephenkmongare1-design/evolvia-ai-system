"""
Evolvia Africa - AI-Powered Company Operating System
Production-ready Streamlit application
"""

import streamlit as st
import pandas as pd
import base64
from io import BytesIO
from datetime import datetime, timedelta
import database as db
from agents import (
    whatsapp_agent,
    trainer_manager,
    accountant,
    hr_agent,
    data_analyst
)

# ============================================================
# PAGE CONFIG & THEME
# ============================================================

st.set_page_config(
    page_title="Evolvia Africa | AI Operating System",
    page_icon="🔷",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ---- Evolvia brand palette (from the logo) ----
# ---- Evolvia brand palette — Navy & Blue (Bitrix24-inspired) ----
DARK = "#0f172a"        # near-black navy (headers, wordmark)
DARK2 = "#1e3a5f"        # deep navy blue
MID = "#2563eb"          # primary indigo-blue
BRIGHT = "#3b82f6"        # bright blue accent
BRIGHT2 = "#60a5fa"      # light sky-blue accent
CREAM = "#f8fafc"        # cool near-white background

# Custom CSS - Evolvia modern green theme (matching the logo)
st.markdown(f"""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Poppins:wght@400;500;600;700;800&display=swap');

    html, body, [class*="css"] {{
        font-family: 'Poppins', sans-serif;
    }}

    /* Main background */
    .stApp {{
        background: linear-gradient(180deg, {CREAM} 0%, #ffffff 55%);
    }}

    /* Sidebar — light, clean, Bitrix24-style */
    [data-testid="stSidebar"] {{
        background: #ffffff;
        border-right: 1px solid #e2e8f0;
        box-shadow: 2px 0 12px rgba(11,47,28,0.03);
    }}
    [data-testid="stSidebar"] * {{
        color: #334155 !important;
    }}
    [data-testid="stSidebar"] hr {{
        border-color: #e2e8f0 !important;
        margin: 10px 0 !important;
    }}
    [data-testid="stSidebar"] .stRadio > label {{ display:none; }}
    [data-testid="stSidebar"] [role="radiogroup"] {{
        gap: 3px;
    }}
    [data-testid="stSidebar"] [role="radiogroup"] label {{
        padding: 11px 14px;
        border-radius: 10px;
        margin-bottom: 1px;
        transition: background 0.15s, border-color 0.15s, color 0.15s;
        cursor: pointer;
        border-left: 3px solid transparent;
        font-size: 0.93rem;
        font-weight: 500;
        color: #475569 !important;
    }}
    [data-testid="stSidebar"] [role="radiogroup"] label:hover {{
        background: #eff6ff;
    }}
    [data-testid="stSidebar"] [role="radiogroup"] label:has(input:checked) {{
        background: #dbeafe;
        border-left: 3px solid {BRIGHT};
        font-weight: 700;
    }}
    [data-testid="stSidebar"] [role="radiogroup"] label:has(input:checked) p {{
        color: {DARK} !important;
    }}
    [data-testid="stSidebar"] [role="radiogroup"] label div:first-child {{
        display: none;
    }}

    /* Brand header inside sidebar */
    .evolvia-brand {{
        display: flex;
        align-items: center;
        gap: 12px;
        padding: 4px 2px 16px 2px;
        border-bottom: 1px solid #e2e8f0;
        margin-bottom: 14px;
    }}
    .evolvia-logo-badge {{
        width: 42px; height: 42px;
        border-radius: 12px;
        background: linear-gradient(135deg, {BRIGHT2}, {MID} 60%, {DARK});
        display: flex; align-items: center; justify-content: center;
        font-weight: 800; font-size: 20px; color: white;
        box-shadow: 0 3px 10px rgba(11,47,28,0.25);
        flex-shrink: 0;
    }}
    .evolvia-brand-text h2 {{
        margin: 0; font-size: 1.1rem; font-weight: 800; color: {DARK} !important;
        letter-spacing: 0.2px;
    }}
    .evolvia-brand-text span {{
        font-size: 0.72rem; color: #64748b !important;
    }}

    /* Sidebar admin badge */
    .sidebar-admin-badge {{
        background: #f8fafc;
        border: 1px solid #e2e8f0;
        border-radius: 10px;
        padding: 9px 12px;
        font-size: 0.8rem;
        margin-top: 8px;
        color: #334155 !important;
    }}
    .sidebar-admin-badge b {{ color: {DARK} !important; }}

    /* Sidebar section caption (small gray labels) */
    [data-testid="stSidebar"] .stCaption, [data-testid="stSidebar"] small {{
        color: #94a3b8 !important;
    }}

    /* Logout button in sidebar: outline style instead of the loud gradient */
    [data-testid="stSidebar"] .stButton > button {{
        background: #ffffff !important;
        color: {DARK} !important;
        border: 1px solid #cbd5e1 !important;
        box-shadow: none !important;
        font-weight: 600;
    }}
    [data-testid="stSidebar"] .stButton > button:hover {{
        background: #eff6ff !important;
        border-color: {BRIGHT} !important;
        transform: none !important;
    }}

    /* Headers */
    h1, h2, h3 {{
        color: {DARK} !important;
        font-weight: 800 !important;
    }}

    /* Top page banner */
    .evolvia-page-header {{
        background: linear-gradient(120deg, {DARK} 0%, {MID} 100%);
        border-radius: 18px;
        padding: 26px 30px;
        margin-bottom: 22px;
        box-shadow: 0 8px 24px rgba(11,47,28,0.25);
    }}
    .evolvia-page-header h1 {{
        color: white !important;
        margin: 0 0 4px 0;
        font-size: 1.9rem;
    }}
    .evolvia-page-header p {{
        color: #dbeafe;
        margin: 0;
        font-size: 0.95rem;
    }}

    /* Metric cards */
    [data-testid="stMetric"] {{
        background: white;
        padding: 18px 20px;
        border-radius: 14px;
        border-left: 5px solid {BRIGHT};
        box-shadow: 0 3px 14px rgba(11,47,28,0.08);
    }}
    [data-testid="stMetricLabel"] {{ color: #4b5563 !important; font-weight: 600; }}
    [data-testid="stMetricValue"] {{ color: {DARK} !important; font-weight: 800; }}

    /* Buttons */
    .stButton > button, .stFormSubmitButton > button {{
        background: linear-gradient(90deg, {DARK2}, {BRIGHT});
        color: white;
        border: none;
        border-radius: 10px;
        font-weight: 600;
        padding: 0.55rem 1.3rem;
        transition: all 0.2s;
        box-shadow: 0 2px 8px rgba(11,47,28,0.15);
    }}
    .stButton > button:hover, .stFormSubmitButton > button:hover {{
        background: linear-gradient(90deg, {DARK}, {MID});
        box-shadow: 0 6px 16px rgba(31,122,61,0.35);
        transform: translateY(-1px);
    }}

    /* Success / Info boxes */
    .stSuccess, .stInfo, .stWarning, .stError {{
        border-radius: 12px;
    }}

    /* Dataframes */
    .stDataFrame {{
        border-radius: 12px;
        overflow: hidden;
        border: 1px solid #e5e7eb;
    }}

    /* Tabs */
    .stTabs [data-baseweb="tab-list"] {{
        gap: 8px;
    }}
    .stTabs [data-baseweb="tab"] {{
        border-radius: 10px 10px 0 0;
        background: #eff6ff;
        color: {DARK};
        font-weight: 600;
    }}
    .stTabs [aria-selected="true"] {{
        background: {DARK} !important;
        color: white !important;
    }}

    /* Custom card */
    .evolvia-card {{
        background: white;
        padding: 1.5rem;
        border-radius: 14px;
        border: 1px solid #dbeafe;
        box-shadow: 0 3px 14px rgba(11,47,28,0.06);
        margin-bottom: 1rem;
    }}

    /* Status pill */
    .status-pill {{
        display: inline-block;
        padding: 5px 14px;
        border-radius: 999px;
        font-weight: 700;
        font-size: 0.82rem;
    }}
    .status-connected {{ background: #dbeafe; color: #1d4ed8; }}
    .status-disconnected {{ background: #fee2e2; color: #991b1b; }}

    /* Chat bubbles */
    .bubble-user {{
        background: #ffffff; border: 1px solid #e5e7eb;
        border-radius: 14px 14px 14px 2px; padding: 10px 14px;
        margin: 6px 0; max-width: 80%;
    }}
    .bubble-agent {{
        background: linear-gradient(120deg, {DARK2}, {MID});
        color: white; border-radius: 14px 14px 2px 14px;
        padding: 10px 14px; margin: 6px 0 6px auto; max-width: 80%;
    }}
    /* Kanban board (Bitrix-style) */
    .kanban-col-header {{
        border-radius: 10px 10px 0 0;
        padding: 10px 14px;
        font-weight: 700;
        color: white;
        font-size: 0.88rem;
        display: flex; justify-content: space-between; align-items: center;
    }}
    .kanban-col-body {{
        background: #f1f5f9;
        border-radius: 0 0 12px 12px;
        padding: 10px;
        min-height: 120px;
    }}
    .kanban-card {{
        background: white;
        border-radius: 12px;
        padding: 12px 14px;
        margin-bottom: 10px;
        box-shadow: 0 2px 8px rgba(11,47,28,0.08);
        border: 1px solid #e5e7eb;
        border-left: 4px solid {BRIGHT};
    }}
    .kanban-card-title {{
        font-weight: 700; color: {DARK}; font-size: 0.95rem; margin-bottom: 2px;
    }}
    .kanban-card-sub {{ color: #6b7280; font-size: 0.8rem; margin-bottom: 6px; }}
    .kanban-chip {{
        display: inline-block; background: #eff6ff; color: {DARK2};
        border-radius: 999px; padding: 2px 10px; font-size: 0.72rem; font-weight: 600;
        margin-right: 4px;
    }}
    .kanban-avatar {{
        width: 26px; height: 26px; border-radius: 50%;
        background: linear-gradient(135deg, {BRIGHT2}, {MID});
        color: white; font-size: 0.72rem; font-weight: 800;
        display: inline-flex; align-items: center; justify-content: center;
        margin-right: 6px; vertical-align: middle;
    }}
</style>
""", unsafe_allow_html=True)


# ============================================================
# INIT
# ============================================================

@st.cache_resource
def initialize():
    db.init_db()
    return True

initialize()


# ============================================================
# ADMIN LOGIN GATE
# ============================================================

def render_login():
    st.markdown(f"""
    <div style="max-width:420px;margin:60px auto 0 auto;text-align:center;">
        <div style="width:70px;height:70px;border-radius:18px;margin:0 auto 14px auto;
             background:linear-gradient(135deg,{BRIGHT2},{MID} 60%,{DARK});
             display:flex;align-items:center;justify-content:center;
             font-weight:800;font-size:32px;color:white;box-shadow:0 8px 20px rgba(11,47,28,0.3);">E</div>
        <h1 style="margin-bottom:2px;">Evolvia Africa</h1>
        <p style="color:#4b5563;margin-top:0;">AI Company Operating System — Admin Login</p>
    </div>
    """, unsafe_allow_html=True)

    _, mid, _ = st.columns([1, 1.1, 1])
    with mid:
        with st.form("login_form"):
            username = st.text_input("Username", value="admin")
            password = st.text_input("Password", type="password")
            submitted = st.form_submit_button("Sign In →", use_container_width=True)
            if submitted:
                if db.verify_admin(username, password):
                    st.session_state.authenticated = True
                    st.session_state.username = username
                    st.rerun()
                else:
                    st.error("Invalid username or password.")
        st.caption(f"Default login: **{db.DEFAULT_ADMIN_USERNAME}** / **{db.DEFAULT_ADMIN_PASSWORD}** "
                    "— change it under Settings after signing in.")


if "authenticated" not in st.session_state:
    st.session_state.authenticated = False

if not st.session_state.authenticated:
    render_login()
    st.stop()


def page_header(title: str, subtitle: str = ""):
    st.markdown(f"""
    <div class="evolvia-page-header">
        <h1>{title}</h1>
        <p>{subtitle}</p>
    </div>
    """, unsafe_allow_html=True)


# ============================================================
# SIDEBAR NAVIGATION
# ============================================================

with st.sidebar:
    st.markdown("""
    <div class="evolvia-brand">
        <div class="evolvia-logo-badge">E</div>
        <div class="evolvia-brand-text">
            <h2>Evolvia Africa</h2>
            <span>AI Company Operating System</span>
        </div>
    </div>
    """, unsafe_allow_html=True)
    st.markdown("---")

    page = st.radio(
        "Navigation",
        [
            "📊 Dashboard",
            "🗂️ Pipeline (Kanban)",
            "🔗 Connect WhatsApp",
            "💬 WhatsApp Inbox (Test)",
            "🏫 Schools",
            "📅 Bookings & Training",
            "👥 Trainers",
            "💰 Payments",
            "🧾 Trainer Payouts",
            "🤖 Agent Logs",
            "⚙️ Settings"
        ],
        label_visibility="collapsed"
    )

    st.markdown("---")
    wa_status = db.get_setting("wa_status", "disconnected")
    pill = ('<span class="status-pill status-connected">🔵 WhatsApp Linked</span>' if wa_status == "connected"
            else '<span class="status-pill status-disconnected">🔴 WhatsApp Not Linked</span>')
    st.markdown(pill, unsafe_allow_html=True)

    st.markdown(
        f'<div class="sidebar-admin-badge">👤 Signed in as <b>{st.session_state.get("username","admin")}</b></div>',
        unsafe_allow_html=True
    )
    if st.button("🚪 Log Out", use_container_width=True):
        st.session_state.authenticated = False
        st.rerun()

    st.markdown("---")
    st.caption("© 2026 Evolvia Africa")
    st.caption("Powered by AI Agents")


# ============================================================
# DASHBOARD
# ============================================================

if page == "📊 Dashboard":
    page_header("Evolvia Africa Dashboard", "Real-time overview of the AI-operated company")

    stats = db.get_dashboard_stats()

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Total Schools", stats["total_schools"])
    col2.metric("Active Schools", stats["active_schools"])
    col3.metric("Active Trainers", stats["active_trainers"])
    col4.metric("Total Revenue (KES)", f"{stats['total_revenue']:,}")

    col5, col6, col7 = st.columns(3)
    col5.metric("Pending Bookings", stats["pending_bookings"])
    col6.metric("Pending Payments", stats["pending_payments"])
    col7.metric("Pending Payouts", stats["pending_payouts"])

    st.markdown("---")

    # Quick actions + recent activity
    left, right = st.columns([1, 1])

    with left:
        st.subheader("Quick Actions")
        if st.button("🔄 Refresh Dashboard"):
            st.rerun()
        if st.button("📈 Generate Analyst Report"):
            report = data_analyst.generate_admin_report()
            st.success("Data Analyst Agent generated a new report.")
            st.json(report["stats"])

    with right:
        st.subheader("Recent Agent Activity")
        logs = db.get_recent_logs(10)
        if logs:
            for log in logs:
                st.markdown(
                    f"**{log['agent_name']}** • {log['action']}  \n"
                    f"<small>{log['details'] or ''} • {log['created_at'][:19]}</small>",
                    unsafe_allow_html=True
                )
                st.markdown("---")
        else:
            st.info("No agent activity yet.")


# ============================================================
# PIPELINE (KANBAN) — Bitrix-style board
# ============================================================

elif page == "🗂️ Pipeline (Kanban)":
    page_header("Sales & Onboarding Pipeline", "Every school's journey, stage by stage — moving a card triggers the right AI agent automatically.")

    STAGES = [
        {"key": "lead", "label": "🟡 New Lead", "color": "#d97706"},
        {"key": "demo_booked", "label": "🟣 Demo Booked", "color": "#7c3aed"},
        {"key": "training_done", "label": "🟠 Awaiting Payment", "color": "#ea580c"},
        {"key": "active", "label": "🔵 Active (Paying)", "color": "#1d4ed8"},
        {"key": "inactive", "label": "⚪ Inactive", "color": "#64748b"},
    ]

    schools = db.list_schools()
    by_stage = {s["key"]: [sc for sc in schools if sc["status"] == s["key"]] for s in STAGES}

    cols = st.columns(len(STAGES))

    def initials(name: str) -> str:
        parts = [p for p in name.split() if p]
        return "".join(p[0] for p in parts[:2]).upper() if parts else "?"

    for col, stage in zip(cols, STAGES):
        with col:
            st.markdown(
                f'<div class="kanban-col-header" style="background:{stage["color"]}">'
                f'<span>{stage["label"]}</span><span>{len(by_stage[stage["key"]])}</span></div>',
                unsafe_allow_html=True
            )
            st.markdown('<div class="kanban-col-body">', unsafe_allow_html=True)

            if not by_stage[stage["key"]]:
                st.caption("No schools here")

            for sc in by_stage[stage["key"]]:
                st.markdown(f"""
                <div class="kanban-card">
                    <div class="kanban-card-title"><span class="kanban-avatar">{initials(sc['name'])}</span>{sc['name']}</div>
                    <div class="kanban-card-sub">{sc['principal_name']} • {sc['phone']}</div>
                    <span class="kanban-chip">{sc['student_count']} students</span>
                    <span class="kanban-chip">KES {sc['monthly_fee']:,}/mo</span>
                </div>
                """, unsafe_allow_html=True)

                # --- Contextual automated action per stage ---
                if stage["key"] == "lead":
                    with st.popover("📅 Book Demo →", use_container_width=True):
                        d = st.date_input("Demo / Training date", min_value=datetime.now().date(), key=f"date_{sc['id']}")
                        if st.button("Confirm & Auto-Assign Trainer", key=f"book_{sc['id']}"):
                            whatsapp_agent.book_demo(sc["id"], str(d), sc.get("location"))
                            st.success("Booked — trainer auto-assigned.")
                            st.rerun()

                elif stage["key"] == "demo_booked":
                    with st.popover("✅ Complete Training →", use_container_width=True):
                        booking = db.get_latest_booking_for_school(sc["id"])
                        transport = st.checkbox("Include transport (KES 500)", value=True, key=f"tr_{sc['id']}")
                        rating = st.slider("Rating", 1, 5, 5, key=f"rt_{sc['id']}")
                        feedback = st.text_area("Feedback (optional)", key=f"fb_{sc['id']}")
                        if st.button("Mark Complete & Auto-Pay Trainer", key=f"cmp_{sc['id']}"):
                            if booking:
                                db.complete_training(booking["id"], feedback or None, rating)
                                trainer_manager.complete_training_and_pay(booking["id"], transport)
                                accountant.create_school_invoice(sc["id"], "First Term")
                                st.success("Training complete → trainer paid → invoice sent automatically.")
                                st.rerun()
                            else:
                                st.error("No booking found for this school.")

                elif stage["key"] == "training_done":
                    pending_inv = [p for p in db.list_payments() if p["school_id"] == sc["id"] and p["status"] == "pending"]
                    if pending_inv:
                        st.caption(f"⏳ Invoice #{pending_inv[0]['id']} pending — mark paid on the Payments page to auto-activate.")
                    else:
                        if st.button("🧾 Generate Invoice", key=f"inv_{sc['id']}", use_container_width=True):
                            accountant.create_school_invoice(sc["id"], "First Term")
                            st.rerun()

                elif stage["key"] == "active":
                    if st.button("⏸️ Mark Inactive", key=f"inact_{sc['id']}", use_container_width=True):
                        db.update_school_status(sc["id"], "inactive")
                        accountant.log("School marked inactive", sc["name"], sc["id"])
                        st.rerun()

                elif stage["key"] == "inactive":
                    if st.button("🔄 Reactivate", key=f"react_{sc['id']}", use_container_width=True):
                        db.update_school_status(sc["id"], "lead")
                        st.rerun()

            st.markdown('</div>', unsafe_allow_html=True)

    st.markdown("---")
    st.caption("🤖 **Fully automated stage transitions:** booking a demo auto-assigns a trainer • completing "
               "training auto-pays the trainer and auto-generates the invoice • marking an invoice paid "
               "auto-activates the school. No manual status juggling needed.")


# ============================================================
# CONNECT WHATSAPP (QR LINK)
# ============================================================

elif page == "🔗 Connect WhatsApp":
    page_header("Connect WhatsApp", "Link the number Evolvia's WhatsApp Agent replies from — scan once, like WhatsApp Web.")

    wa_status = db.get_setting("wa_status", "disconnected")
    linked_number = db.get_setting("wa_linked_number", "")

    left, right = st.columns([1, 1.2])

    with left:
        st.markdown('<div class="evolvia-card">', unsafe_allow_html=True)
        if wa_status == "connected":
            st.markdown('<span class="status-pill status-connected">🔵 Connected</span>', unsafe_allow_html=True)
            st.markdown(f"### 📱 {linked_number or 'Linked number'}")
            st.write("Incoming messages to this number are picked up automatically by the WhatsApp Agent, "
                     "and replies are sent back the same way.")
            if st.button("🔌 Unlink this number"):
                db.set_setting("wa_status", "disconnected")
                db.set_setting("wa_linked_number", "")
                whatsapp_agent.log("WhatsApp unlinked", linked_number or "")
                st.rerun()
        else:
            st.markdown('<span class="status-pill status-disconnected">🔴 Not Connected</span>', unsafe_allow_html=True)
            st.write("Scan the QR code on the right with the WhatsApp app on the number you want "
                     "Evolvia to reply from — the same way you'd link WhatsApp Web.")
            st.markdown("**On your phone:** WhatsApp → Settings → Linked Devices → Link a Device → scan.")

            number_input = st.text_input("Number this QR should link (for this demo)", placeholder="2547XXXXXXXX")
            if st.button("🔄 Generate New QR Code"):
                db.new_pairing_token()
                st.session_state["wa_pending_number"] = number_input
                st.rerun()

            st.text_input(
                "Simulate the scan (demo mode)",
                key="wa_scan_sim",
                placeholder="Type anything and click the button below to simulate a phone scanning this code"
            )
            if st.button("✅ Simulate: Phone Scanned QR", type="primary"):
                final_number = st.session_state.get("wa_pending_number") or number_input or "254700000000"
                db.set_setting("wa_status", "connected")
                db.set_setting("wa_linked_number", final_number)
                whatsapp_agent.log("WhatsApp linked", final_number)
                st.success(f"Linked! {final_number} is now connected.")
                st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)

    with right:
        st.markdown('<div class="evolvia-card" style="text-align:center;">', unsafe_allow_html=True)
        if wa_status == "connected":
            st.markdown(f"""
            <div style="padding:40px 0;">
                <div style="font-size:64px;">✅</div>
                <h3 style="margin-top:8px;">WhatsApp is linked</h3>
                <p style="color:#4b5563;">No QR code needed while connected.</p>
            </div>
            """, unsafe_allow_html=True)
        else:
            token = db.get_setting("wa_pairing_token") or db.new_pairing_token()
            qr_data_url = None
            try:
                import qrcode
                qr_img = qrcode.make(f"evolvia-link:{token}")
                buf = BytesIO()
                qr_img.save(buf, format="PNG")
                qr_data_url = "data:image/png;base64," + base64.b64encode(buf.getvalue()).decode()
            except ImportError:
                pass

            if qr_data_url:
                st.markdown(f'<img src="{qr_data_url}" width="240" style="border-radius:12px;border:8px solid white;box-shadow:0 4px 16px rgba(0,0,0,0.12);"/>', unsafe_allow_html=True)
            else:
                st.warning("Install `qrcode` (already in requirements.txt) to render the actual QR image. "
                           "Run `pip install -r requirements.txt` and restart the app.")
            st.caption("This code refreshes each time you click 'Generate New QR Code'.")
        st.markdown('</div>', unsafe_allow_html=True)

    st.markdown("---")
    st.markdown("""
    <div class="evolvia-card">
    <b>⚠️ Production note:</b> This QR flow is a demo of the pairing UX. For a real, reliable connection
    that WhatsApp won't ban, use the official <b>WhatsApp Business Cloud API</b> (Meta) or a provider like
    Twilio — plug your Phone Number ID + Access Token into <code>agents.py</code> and point Meta's webhook
    at your deployed app. Automating the personal WhatsApp Web session with a scraper/bot violates WhatsApp's
    Terms of Service and risks the number being permanently banned, so avoid that route for anything live.
    </div>
    """, unsafe_allow_html=True)


# ============================================================
# WHATSAPP SIMULATOR
# ============================================================

elif page == "💬 WhatsApp Inbox (Test)":
    page_header("WhatsApp Inbox (Test Chat)",
                "Simulate a Principal messaging Evolvia via WhatsApp so you can see exactly how the AI Agent replies.")

    st.markdown("""
    <div class="evolvia-card">
        <strong>How to use:</strong><br>
        1. Enter a phone number (e.g. 254712345678)<br>
        2. Type a message as the Principal<br>
        3. The WhatsApp Agent will reply automatically<br>
        4. For new schools, send: <code>School Name, Principal Name, Students, Location</code>
    </div>
    """, unsafe_allow_html=True)

    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []

    phone = st.text_input("Principal Phone Number", value="254700000001", key="wa_phone")

    # Display chat
    for entry in st.session_state.chat_history:
        if entry["role"] == "user":
            st.markdown(
                f'<div class="bubble-user"><b>👤 Principal ({entry["phone"]})</b><br>{entry["content"]}</div>',
                unsafe_allow_html=True
            )
        else:
            content = entry["content"].replace("\n", "<br>")
            st.markdown(
                f'<div class="bubble-agent"><b>🤖 Evolvia AI Agent</b><br>{content}</div>',
                unsafe_allow_html=True
            )

    with st.form("whatsapp_form", clear_on_submit=True):
        message = st.text_area("Message from Principal", height=100)
        submitted = st.form_submit_button("Send Message →")

        if submitted and message.strip():
            # Add user message
            st.session_state.chat_history.append({
                "role": "user",
                "phone": phone,
                "content": message
            })

            # Check if this looks like registration data
            parts = [p.strip() for p in message.split(",")]
            school = db.get_school_by_phone(phone)

            if not school and len(parts) >= 4:
                try:
                    name = parts[0]
                    principal = parts[1]
                    students = int(parts[2])
                    location = parts[3]
                    reply = whatsapp_agent.register_new_school(phone, name, principal, students, location)
                except Exception:
                    reply = whatsapp_agent.handle_incoming_message(phone, message)
            else:
                # Try to detect date for booking
                if school and any(char.isdigit() for char in message) and any(m in message.lower() for m in ["jan", "feb", "mar", "apr", "may", "jun", "jul", "aug", "sep", "oct", "nov", "dec", "2026", "2025"]):
                    reply = whatsapp_agent.book_demo(school["id"], message.strip(), school.get("location"))
                else:
                    reply = whatsapp_agent.handle_incoming_message(phone, message)

            st.session_state.chat_history.append({
                "role": "agent",
                "content": reply
            })
            st.rerun()


# ============================================================
# SCHOOLS
# ============================================================

elif page == "🏫 Schools":
    page_header("Schools & Principals", "Every school that has come through the WhatsApp Agent or been added manually.")

    tab1, tab2 = st.tabs(["All Schools", "Add New School"])

    with tab1:
        schools = db.list_schools()
        if schools:
            df = pd.DataFrame(schools)
            df = df[["id", "name", "principal_name", "phone", "student_count", "monthly_fee", "status", "location", "created_at"]]
            st.dataframe(df, use_container_width=True, hide_index=True)
        else:
            st.info("No schools registered yet. Use the WhatsApp Simulator or the form below.")

    with tab2:
        with st.form("add_school"):
            name = st.text_input("School Name")
            principal = st.text_input("Principal Full Name")
            phone = st.text_input("Phone (WhatsApp)", placeholder="2547XXXXXXXX")
            students = st.number_input("Number of Students", min_value=0, value=200)
            location = st.text_input("Location (County / Town)")
            submitted = st.form_submit_button("Register School")

            if submitted:
                if name and principal and phone:
                    fee = db.calculate_monthly_fee(students)
                    school_id = db.create_school(name, principal, phone, students, location)
                    whatsapp_agent.log("School registered via Admin", f"{name}", school_id)
                    st.success(f"✅ School registered! ID: {school_id} | Monthly Fee: KES {fee:,}")
                    st.rerun()
                else:
                    st.error("Please fill Name, Principal and Phone.")


# ============================================================
# BOOKINGS & TRAINING
# ============================================================

elif page == "📅 Bookings & Training":
    page_header("Bookings & Training Management", "Demo & training dates, auto-assigned trainers, and completions.")

    tab1, tab2, tab3 = st.tabs(["All Bookings", "Create Booking", "Complete Training"])

    with tab1:
        bookings = db.list_bookings()
        if bookings:
            df = pd.DataFrame(bookings)
            cols = ["id", "school_name", "principal_name", "demo_date", "training_date",
                    "trainer_name", "status", "location", "created_at"]
            available = [c for c in cols if c in df.columns]
            st.dataframe(df[available], use_container_width=True, hide_index=True)
        else:
            st.info("No bookings yet.")

    with tab2:
        schools = db.list_schools()
        if not schools:
            st.warning("Register at least one school first.")
        else:
            school_options = {f"{s['name']} ({s['principal_name']})": s["id"] for s in schools}
            with st.form("create_booking"):
                selected = st.selectbox("Select School", list(school_options.keys()))
                demo_date = st.date_input("Demo / Training Date", min_value=datetime.now().date())
                location = st.text_input("Training Location (optional)")
                submitted = st.form_submit_button("Create Booking & Auto-Assign Trainer")

                if submitted:
                    school_id = school_options[selected]
                    booking_id = db.create_booking(school_id, str(demo_date), str(demo_date), location)
                    db.update_school_status(school_id, "demo_booked")
                    result = trainer_manager.auto_assign_trainer(booking_id)
                    st.success(f"Booking #{booking_id} created.")
                    st.info(result)
                    st.rerun()

    with tab3:
        pending = db.list_bookings()
        active = [b for b in pending if b["status"] in ("training_scheduled", "demo_scheduled", "pending")]
        if not active:
            st.info("No active bookings to complete.")
        else:
            options = {f"#{b['id']} - {b.get('school_name', 'Unknown')} ({b['status']})": b["id"] for b in active}
            selected = st.selectbox("Select Booking to Complete", list(options.keys()))
            include_transport = st.checkbox("Include Transport Allowance (KES 500)", value=True)
            feedback = st.text_area("Principal Feedback (optional)")
            rating = st.slider("Rating", 1, 5, 5)

            if st.button("Mark Training Complete & Create Payout"):
                booking_id = options[selected]
                db.complete_training(booking_id, feedback, rating)
                result = trainer_manager.complete_training_and_pay(booking_id, include_transport)
                if result["success"]:
                    st.success(result["message"])
                    # Also create school invoice
                    booking = db.get_booking(booking_id)
                    inv = accountant.create_school_invoice(booking["school_id"], "First Term")
                    st.info(inv)
                else:
                    st.error(result["message"])
                st.rerun()


# ============================================================
# TRAINERS
# ============================================================

elif page == "👥 Trainers":
    page_header("Trainer Management", "Trainers are real people — the AI Trainer Manager Agent assigns and pays them.")

    tab1, tab2 = st.tabs(["Active Trainers", "Register New Trainer"])

    with tab1:
        trainers = db.list_trainers(active_only=False)
        if trainers:
            df = pd.DataFrame(trainers)
            st.dataframe(df[["id", "name", "phone", "location", "trainings_completed", "total_earnings", "active"]],
                         use_container_width=True, hide_index=True)
        else:
            st.info("No trainers registered. Add some below.")

    with tab2:
        with st.form("add_trainer"):
            name = st.text_input("Full Name")
            phone = st.text_input("Phone Number")
            email = st.text_input("Email (optional)")
            location = st.text_input("Base Location")
            submitted = st.form_submit_button("Register Trainer")

            if submitted and name and phone:
                msg = hr_agent.register_trainer(name, phone, email, location)
                st.success(msg)
                st.rerun()


# ============================================================
# PAYMENTS (School Fees)
# ============================================================

elif page == "💰 Payments":
    page_header("School Payments", "Invoices and fee collection, tiered by student count.")

    tab1, tab2 = st.tabs(["All Payments", "Create Invoice"])

    with tab1:
        payments = db.list_payments()
        if payments:
            df = pd.DataFrame(payments)
            st.dataframe(df[["id", "school_name", "principal_name", "amount", "period", "status", "created_at"]],
                         use_container_width=True, hide_index=True)

            st.subheader("Mark as Paid")
            pending = [p for p in payments if p["status"] == "pending"]
            if pending:
                opts = {f"#{p['id']} - {p['school_name']} - KES {p['amount']:,}": p["id"] for p in pending}
                sel = st.selectbox("Select Payment", list(opts.keys()))
                method = st.selectbox("Payment Method", ["M-Pesa", "Bank Transfer", "Cash", "Other"])
                ref = st.text_input("Transaction Reference")
                if st.button("Confirm Payment Received"):
                    db.mark_payment_paid(opts[sel], method, ref)
                    accountant.log("Payment received", f"Payment #{opts[sel]} via {method}", opts[sel])
                    st.success("Payment marked as paid.")
                    st.rerun()
        else:
            st.info("No payments yet.")

    with tab2:
        schools = db.list_schools()
        if schools:
            opts = {f"{s['name']} (KES {s['monthly_fee']:,}/mo)": s["id"] for s in schools}
            selected = st.selectbox("School", list(opts.keys()))
            period = st.text_input("Period", value="First Term")
            if st.button("Generate Invoice"):
                msg = accountant.create_school_invoice(opts[selected], period)
                st.success("Invoice created")
                st.info(msg)
                st.rerun()


# ============================================================
# TRAINER PAYOUTS
# ============================================================

elif page == "🧾 Trainer Payouts":
    page_header("Trainer Payouts", "Standard: KES 250 per school completed + KES 500 transport when they travel.")

    payouts = db.list_payouts()
    if payouts:
        df = pd.DataFrame(payouts)
        st.dataframe(df[["id", "trainer_name", "trainer_phone", "school_name", "base_pay", "transport", "total", "status", "created_at"]],
                     use_container_width=True, hide_index=True)

        pending = [p for p in payouts if p["status"] == "pending"]
        if pending:
            st.subheader("Approve & Pay")
            opts = {f"#{p['id']} - {p['trainer_name']} - KES {p['total']}": p["id"] for p in pending}
            sel = st.selectbox("Select Payout", list(opts.keys()))
            if st.button("Approve & Mark as Paid"):
                msg = accountant.approve_and_pay_trainer(opts[sel])
                # Update trainer earnings
                payout = next(p for p in pending if p["id"] == opts[sel])
                db.update_trainer_earnings(payout["trainer_id"], payout["total"])
                st.success(msg)
                st.rerun()
    else:
        st.info("No trainer payouts yet. Complete a training to generate one.")


# ============================================================
# AGENT LOGS
# ============================================================

elif page == "🤖 Agent Logs":
    page_header("AI Agent Activity Log", "Full transparency of every decision made by the agents.")

    logs = db.get_recent_logs(100)
    if logs:
        df = pd.DataFrame(logs)
        st.dataframe(df[["id", "agent_name", "action", "details", "created_at"]],
                     use_container_width=True, hide_index=True)
    else:
        st.info("No agent activity recorded yet.")


# ============================================================
# SETTINGS
# ============================================================

elif page == "⚙️ Settings":
    page_header("System Settings", "Pricing rules, WhatsApp integration, admin account and database.")

    st.subheader("Pricing Rules (Official)")
    st.markdown("""
    | Students       | Monthly Fee (KES) |
    |----------------|-------------------|
    | 0 – 300        | 2,500             |
    | 301 – 600      | 5,000             |
    | 601 – 1,000    | 7,500             |
    | 1,000+         | 10,000            |
    """)

    st.subheader("Trainer Pay Rules")
    st.markdown("""
    - Base pay per school completed: **KES 250**
    - Transport allowance (when they travel): **KES 500**
    """)

    st.subheader("WhatsApp Integration (Production)")
    st.info("""
    This simulator is ready for production WhatsApp Business API.
    
    Recommended path:
    1. Create a Meta Business account + WhatsApp Business App
    2. Get Permanent Access Token + Phone Number ID
    3. Use a library such as `whatsapp-business-api` or Twilio
    4. Point webhooks to your deployed backend
    5. Replace the simulator logic with real incoming webhook handling
    
    Do **not** use WhatsApp Web scraping / QR automation — it violates ToS and risks permanent ban.
    """)

    st.subheader("Admin Account")
    with st.form("change_password"):
        st.write(f"Signed in as **{st.session_state.get('username', 'admin')}**")
        new_pw = st.text_input("New Password", type="password")
        confirm_pw = st.text_input("Confirm New Password", type="password")
        if st.form_submit_button("Update Password"):
            if not new_pw or len(new_pw) < 6:
                st.error("Password must be at least 6 characters.")
            elif new_pw != confirm_pw:
                st.error("Passwords do not match.")
            else:
                db.change_admin_password(st.session_state.get("username", "admin"), new_pw)
                st.success("Password updated.")

    st.subheader("Database")
    st.code(f"Current DB: {db.DB_PATH}", language="text")
    if st.button("Re-initialize Database Tables"):
        db.init_db()
        st.success("Tables verified / created.")
