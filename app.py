"""
Evolvia Africa - AI-Powered Company Operating System
Production-ready Streamlit application
"""

import streamlit as st
import pandas as pd
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
    page_icon="🟢",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS - Evolvia Green Theme (matching logo)
st.markdown("""
<style>
    /* Main background */
    .stApp {
        background: linear-gradient(180deg, #f0fdf4 0%, #ffffff 100%);
    }

    /* Sidebar */
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #064e3b 0%, #065f46 100%);
    }
    [data-testid="stSidebar"] * {
        color: #ecfdf5 !important;
    }
    [data-testid="stSidebar"] .stSelectbox label, 
    [data-testid="stSidebar"] .stRadio label {
        color: #ecfdf5 !important;
    }

    /* Headers */
    h1, h2, h3 {
        color: #064e3b !important;
    }

    /* Metric cards */
    [data-testid="stMetric"] {
        background: white;
        padding: 16px 20px;
        border-radius: 12px;
        border-left: 5px solid #10b981;
        box-shadow: 0 2px 8px rgba(6, 78, 59, 0.08);
    }

    /* Buttons */
    .stButton > button {
        background: linear-gradient(90deg, #059669, #10b981);
        color: white;
        border: none;
        border-radius: 8px;
        font-weight: 600;
        padding: 0.5rem 1.2rem;
        transition: all 0.2s;
    }
    .stButton > button:hover {
        background: linear-gradient(90deg, #047857, #059669);
        box-shadow: 0 4px 12px rgba(16, 185, 129, 0.3);
    }

    /* Success / Info boxes */
    .stSuccess, .stInfo {
        border-radius: 10px;
    }

    /* Dataframes */
    .stDataFrame {
        border-radius: 10px;
        overflow: hidden;
    }

    /* Tabs */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
    }
    .stTabs [data-baseweb="tab"] {
        border-radius: 8px 8px 0 0;
        background: #ecfdf5;
        color: #064e3b;
    }
    .stTabs [aria-selected="true"] {
        background: #064e3b !important;
        color: white !important;
    }

    /* Custom card */
    .evolvia-card {
        background: white;
        padding: 1.5rem;
        border-radius: 12px;
        border: 1px solid #d1fae5;
        box-shadow: 0 2px 10px rgba(6, 78, 59, 0.06);
        margin-bottom: 1rem;
    }
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
# SIDEBAR NAVIGATION
# ============================================================

with st.sidebar:
    st.markdown("## 🟢 Evolvia Africa")
    st.caption("AI Company Operating System")
    st.markdown("---")

    page = st.radio(
        "Navigation",
        [
            "📊 Dashboard",
            "💬 WhatsApp Simulator",
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
    st.caption("© 2026 Evolvia Africa")
    st.caption("Powered by AI Agents")


# ============================================================
# DASHBOARD
# ============================================================

if page == "📊 Dashboard":
    st.title("Evolvia Africa Dashboard")
    st.caption("Real-time overview of the AI-operated company")

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
# WHATSAPP SIMULATOR
# ============================================================

elif page == "💬 WhatsApp Simulator":
    st.title("WhatsApp Agent Simulator")
    st.caption("Simulate a Principal messaging Evolvia via WhatsApp. In production this connects to WhatsApp Business API.")

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
            st.markdown(f"**👤 Principal ({entry['phone']})**  \n{entry['content']}")
        else:
            st.markdown(f"**🤖 Evolvia WhatsApp Agent**  \n{entry['content']}")
        st.markdown("---")

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
    st.title("Schools & Principals")

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
    st.title("Bookings & Training Management")

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
    st.title("Trainer Management")
    st.caption("Trainers are real people managed by the AI Trainer Manager Agent")

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
    st.title("School Payments")

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
    st.title("Trainer Payouts")
    st.caption("Standard: KES 250 per school + KES 500 transport")

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
    st.title("AI Agent Activity Log")
    st.caption("Full transparency of every decision made by the agents")

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
    st.title("System Settings")

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

    st.subheader("Database")
    st.code(f"Current DB: {db.DB_PATH}", language="text")
    if st.button("Re-initialize Database Tables"):
        db.init_db()
        st.success("Tables verified / created.")
