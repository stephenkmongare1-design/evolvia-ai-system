# Evolvia Africa – AI Company Operating System

Production-ready multi-agent CRM and operations platform for **Evolvia Africa**.

## Features

- **Admin Login** – dashboard is protected; bcrypt-hashed password, changeable from Settings
- **Connect WhatsApp** – QR "link a device" page (WhatsApp Web–style pairing UX) showing live connection status
- **WhatsApp Agent** – Frontline AI that handles principal inquiries, registration, booking, payments & feedback
- **Trainer Manager Agent** – Automatically assigns real human trainers and calculates their pay. Trainer identity, phone number and exact location logistics are kept internal and are never sent to the principal.
- **Accountant Agent** – Generates invoices, tracks school payments, manages trainer payouts. Automatically fires the first-term invoice the moment a principal submits post-training feedback.
- **HR Agent** – Onboards trainers
- **Data Analyst Agent** – Produces admin reports and activity insights
- Full CRM for Schools, Bookings, Payments, Trainers & Payouts
- Modern green-themed UI matching the Evolvia logo (dark forest green → bright leaf green)
- SQLite database (easy to upgrade to PostgreSQL)
- Complete agent activity logging for transparency

## Default Admin Login

On first run, a default admin account is created automatically:

| Username | Password     |
|----------|--------------|
| `admin`  | `evolvia2026`|

**Change this immediately** after first login: sidebar → ⚙️ Settings → Admin Account.

You can also override the defaults before first run with environment variables:
```bash
export EVOLVIA_ADMIN_USER=youradmin
export EVOLVIA_ADMIN_PASSWORD=your-strong-password
```

## Official Pricing Rules

| Students     | Monthly Fee (KES) |
|--------------|-------------------|
| 0 – 300      | 2,500             |
| 301 – 600    | 5,000             |
| 601 – 1,000  | 7,500             |
| 1,000+       | 10,000            |

## Trainer Pay

- KES 250 per school completed
- KES 500 transport allowance (when they travel for training)

## Quick Start (Local)

```bash
# 1. Create virtual environment
python -m venv venv
source venv/bin/activate          # Windows: venv\Scripts\activate

# 2. Install dependencies
pip install -r requirements.txt

# 3. Run the application
streamlit run app.py
```

The app will open at `http://localhost:8501`. Log in with the default admin credentials above.

## Deploy for a Public Link

### Option A – Streamlit Community Cloud (Easiest)
1. Push this folder to a GitHub repository
2. Go to [share.streamlit.io](https://share.streamlit.io)
3. Deploy the repo → you get a public URL instantly
4. Streamlit Cloud auto-redeploys every time you push new commits to the connected repo

### Option B – Replit
1. Create a new Replit → Python
2. Upload the files
3. In Shell: `pip install -r requirements.txt`
4. Run `streamlit run app.py --server.port 3000`
5. Use the Replit webview / public URL

### Option C – Railway / Render / Fly.io
Any platform that supports Python + Streamlit works. Set the start command to:
```bash
streamlit run app.py --server.port $PORT --server.address 0.0.0.0
```

## Project Structure

```
evolvia_ai_system/
├── app.py              # Main Streamlit application (UI + routing + login)
├── agents.py           # All AI agents (WhatsApp, Trainer Manager, Accountant, HR, Analyst)
├── database.py         # SQLite models, pricing logic, auth, CRUD
├── requirements.txt
└── README.md
```

## The WhatsApp "Connect" Page

The sidebar's **🔗 Connect WhatsApp** page shows a QR code and a live linked/not-linked status,
demonstrating the pairing experience (similar to linking WhatsApp Web). This is a **UI demo of the
pairing flow**, not a live connection to WhatsApp's servers.

## Connecting Real WhatsApp Business API (Production)

For a real, reliable connection that won't get your number banned:

1. Create a Meta Developer account + WhatsApp Business App
2. Get a Phone Number ID + Permanent Token
3. Use the official Cloud API or a provider (Twilio, MessageBird, etc.)
4. Create a webhook endpoint that receives messages
5. Call `whatsapp_agent.handle_incoming_message(phone, text)` and send the returned reply back via the API
6. Update the **Connect WhatsApp** page's "linked" status to reflect your real webhook connection instead of the demo simulate-scan button

**Important**: Do not automate the personal WhatsApp Web session (scraping / bot-driven QR linking) to send real production traffic. It violates WhatsApp's Terms of Service and will get the number permanently banned. Use the official Business API instead.

## Security Notes

- Admin login is enabled by default; passwords are hashed with bcrypt, never stored in plain text
- Change the default admin password immediately after first deploy
- For multi-admin setups, use `database.create_admin_user()` to add more accounts
- Never commit real API keys – use environment variables

## Next Recommended Improvements

- Role-based accounts (Admin vs Viewer vs Accountant)
- Calendar view for trainings
- Location-based trainer matching
- Automatic M-Pesa STK Push / B2C integration
- Real WhatsApp Business Cloud API webhook (replacing the demo Connect page)
- Email / SMS notifications
- Upgrade SQLite → PostgreSQL for multi-user production (SQLite on Streamlit Cloud does not persist reliably across every rebuild)

---

**Evolvia Africa** – Built to be run by AI.
