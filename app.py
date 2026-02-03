import streamlit as st
import plotly.express as px
from database.db_manager import DBManager
from database.models import CheckLog, AlertLog
import time
from datetime import datetime, timedelta
from apscheduler.schedulers.background import BackgroundScheduler
from monitors.checker import SiteChecker
import os

st.set_page_config(
    page_title="SiteMonitor OSINT Pro",
    layout="wide",
    page_icon="🛡️",
    initial_sidebar_state="expanded"
)

# --- Enhanced UI Styling (Vibrant & Modern) ---
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700&display=swap');
    
    html, body, [class*="css"] {
        font-family: 'Inter', sans-serif;
    }
    
    /* Main Background */
    .stApp {
        background: linear-gradient(135deg, #0f172a 0%, #1e293b 100%);
        color: #f8fafc;
    }
    
    /* Custom Card Style */
    .metric-card {
        background: rgba(30, 41, 59, 0.7);
        backdrop-filter: blur(10px);
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 16px;
        padding: 24px;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06);
        transition: transform 0.2s ease;
    }
    .metric-card:hover {
        transform: translateY(-2px);
        border-color: rgba(59, 130, 246, 0.5);
    }
    
    /* Vibrant Status Indicators */
    .status-badge {
        padding: 4px 12px;
        border-radius: 9999px;
        font-weight: 600;
        font-size: 0.875rem;
    }
    .status-up { background-color: rgba(34, 197, 94, 0.2); color: #4ade80; border: 1px solid #22c55e; }
    .status-down { background-color: rgba(239, 68, 68, 0.2); color: #f87171; border: 1px solid #ef4444; }
    
    /* Metric Labels */
    .metric-value {
        font-size: 2.25rem;
        font-weight: 700;
        background: linear-gradient(to right, #60a5fa, #a855f7);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }
    
    /* Table Styling */
    div[data-testid="stMarkdownContainer"] table {
        width: 100%;
        border-collapse: separate;
        border-spacing: 0 8px;
    }
    div[data-testid="stMarkdownContainer"] tr {
        background: rgba(30, 41, 59, 0.4);
        border-radius: 8px;
    }
    div[data-testid="stMarkdownContainer"] th {
        color: #94a3b8;
        font-weight: 600;
        text-transform: uppercase;
        font-size: 0.75rem;
        letter-spacing: 0.05em;
        border: none;
        padding: 12px;
    }
    div[data-testid="stMarkdownContainer"] td {
        padding: 16px 12px;
        border: none;
    }
</style>
""", unsafe_allow_html=True)

db = DBManager()

# --- Background Monitor Initialization (Singleton) ---
@st.cache_resource
def start_monitor():
    scheduler = BackgroundScheduler()
    checker = SiteChecker(db)
    
    # --- Auto-Seeding for Cloud (If DB is empty) ---
    websites = db.get_active_websites()
    if not websites:
        from reset_and_seed import reset_and_seed
        # We don't want to wipe the DB if it's just a restart, 
        # but reset_and_seed does. For cloud safety, we just add missing ones.
        sites = [
            ("GKToday - SSC/UPSC", "https://www.gktoday.in/"),
            ("Drishti IAS - News Analysis", "https://www.drishtiias.com/current-affairs-news-analysis-editorials"),
            ("AffairsCloud - Quizzes/PDFs", "https://affairscloud.com/"),
            ("Adda247 - SSC/Banking", "https://currentaffairs.adda247.com/"),
            ("PW Live - SSC/Railway", "https://www.pw.live/ssc/exams/daily-current-affairs-today"),
            ("Python.org Blogs", "https://www.python.org/blogs"),
            ("Python Weekly", "https://www.pythonweekly.com/"),
            ("Real Python News", "https://realpython.com/tutorials/news"),
            ("The Hacker News", "https://thehackernews.com/"),
            ("Dark Reading", "https://www.darkreading.com/"),
            ("Security Week", "https://www.securityweek.com/"),
            ("Automate the Boring Stuff", "https://automatetheboringstuff.com/"),
            ("Real Python - Automation", "https://realpython.com/"),
            ("SSC Official Site", "https://ssc.gov.in/"),
            ("Testbook - SSC CGL", "https://testbook.com/ssc-cgl-exam"),
            ("Oliveboard - SSC CGL", "https://www.oliveboard.in/ssc-cgl"),
            ("Google", "https://www.google.com/"),
            ("YouTube", "https://www.youtube.com/"),
            ("MyGov India", "https://www.mygov.in/"),
            ("Microsoft IT", "https://www.microsoft.com/"),
            ("TechCrunch", "https://techcrunch.com/"),
            ("Wired", "https://www.wired.com/"),
            ("The Verge", "https://www.theverge.com/"),
            ("MIT Technology Review", "https://www.technologyreview.com/"),
            ("Engadget", "https://www.engadget.com/"),
            ("Ars Technica", "https://arstechnica.com/"),
            ("VentureBeat", "https://venturebeat.com/"),
            ("Digital Trends", "https://www.digitaltrends.com/"),
            ("Reuters Technology", "https://www.reuters.com/technology"),
            ("WEBaniX Solutions", "https://webanixsolutions.com/"),
            ("PHP Poets Solutions", "https://phppoets.com/"),
            ("Zenver Technologies", "https://www.zenver.in/"),
            ("WhatsApp", "https://www.whatsapp.com/"),
        ]
        for name, url in sites:
            try:
                db.add_website(name, url, 300)
            except: pass
        websites = db.get_active_websites()

    for site in websites:
        scheduler.add_job(
            checker.check_site, 
            'interval', 
            seconds=site.check_interval, 
            args=[site.id],
            id=f"site_{site.id}",
            replace_existing=True
        )
    scheduler.start()
    return scheduler

# Start the engine
if "monitor_started" not in st.session_state:
    start_monitor()
    st.session_state.monitor_started = True

# --- Helper Functions ---
def get_uptime_percentage(website_id, days=7):
    with db.get_session() as session:
        since = datetime.utcnow() - timedelta(days=days)
        total = session.query(CheckLog).filter(CheckLog.website_id == website_id, CheckLog.timestamp >= since).count()
        if total == 0: return 100.0
        up_count = session.query(CheckLog).filter(CheckLog.website_id == website_id, CheckLog.timestamp >= since, CheckLog.is_up == True).count()
        return (up_count / total) * 100

# --- Sidebar Management ---
with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/2622/2622244.png", width=80)
    st.title("SiteMonitor Pro")
    st.markdown("---")
    
    with st.expander("➕ Add New Target", expanded=False):
        new_name = st.text_input("Name", placeholder="My Website")
        new_url = st.text_input("URL", placeholder="https://example.com")
        new_interval = st.select_slider("Check Interval", options=[60, 300, 600, 1800, 3600], value=300, format_func=lambda x: f"{x//60}m")
        if st.button("Start Tracking", use_container_width=True):
            if new_name and new_url:
                result = db.add_website(new_name, new_url, new_interval)
                if result:
                    st.success(f"Added {new_name}!")
                    st.rerun()
                else:
                    st.error(f"Error: A target with URL '{new_url}' is already being monitored.")
            else:
                st.error("Please fill all fields.")
    
    st.markdown("---")
    st.caption("Background service handles OSINT & Alerts.")
    if st.button("🔄 Refresh Data", use_container_width=True):
        st.rerun()

# --- Main Dashboard Logic ---
tab_overview, tab_details, tab_help = st.tabs(["📊 Overview", "📈 Site Details", "📩 Setup Guide"])

websites = db.get_all_websites()

if not websites:
    with tab_overview:
        st.info("No targets found. Use the sidebar to add your first website!")
else:
    # --- OVERVIEW TAB ---
    with tab_overview:
        total_sites = len(websites)
        up_sites = sum(1 for w in websites if w.is_up)
        down_sites = total_sites - up_sites
        
        c1, c2, c3 = st.columns(3)
        with c1:
            st.markdown(f'<div class="metric-card"><div style="color: #94a3b8; font-size: 0.875rem;">Total Targets</div><div class="metric-value">{total_sites}</div></div>', unsafe_allow_html=True)
        with c2:
            st.markdown(f'<div class="metric-card"><div style="color: #4ade80; font-size: 0.875rem;">Online</div><div class="metric-value" style="background: linear-gradient(to right, #4ade80, #2dd4bf); -webkit-background-clip: text;">{up_sites}</div></div>', unsafe_allow_html=True)
        with c3:
            color = "#f87171" if down_sites > 0 else "#94a3b8"
            st.markdown(f'<div class="metric-card"><div style="color: {color}; font-size: 0.875rem;">Offline</div><div class="metric-value" style="background: linear-gradient(to right, #f87171, #fb923c); -webkit-background-clip: text;">{down_sites}</div></div>', unsafe_allow_html=True)

        st.markdown("### 📋 Live Monitor Status")
        
        table_header = "| Name | Status | Latency | Uptime (7d) | Last Check |"
        table_sep = "| :--- | :--- | :--- | :--- | :--- |"
        table_rows = []
        
        for site in websites:
            uptime = get_uptime_percentage(site.id)
            status_style = "status-up" if site.is_up else "status-down"
            status_text = "ONLINE" if site.is_up else "OFFLINE"
            latency = f"{site.last_response_time:.2f}s" if site.last_response_time else "--"
            last_check = site.last_check_at.strftime("%H:%M:%S") if site.last_check_at else "Never"
            
            table_rows.append(f"| **{site.name}** | <span class='status-badge {status_style}'>{status_text}</span> | `{latency}` | `{uptime:.1f}%` | {last_check} |")
        
        st.markdown("\n".join([table_header, table_sep] + table_rows), unsafe_allow_html=True)

    # --- DETAILS TAB ---
    with tab_details:
        site_select = st.selectbox("🎯 Target Analysis", options=[w.name for w in websites], index=0)
        selected_site = next(w for w in websites if w.name == site_select)
        
        with db.get_session() as session:
            logs = session.query(CheckLog).filter(CheckLog.website_id == selected_site.id).order_by(CheckLog.timestamp.desc()).limit(50).all()
            
            if logs:
                times = [l.timestamp for l in logs]
                latencies = [l.response_time for l in logs]
                
                # Plotly Chart with custom theme
                fig = px.area(x=times, y=latencies, title=f"Latency History: {selected_site.name}",
                              labels={'x': 'Time', 'y': 'Response Time (s)'},
                              template="plotly_dark")
                fig.update_traces(line_color='#60a5fa', fillcolor='rgba(96, 165, 250, 0.1)')
                fig.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
                                  font_color="#94a3b8", margin=dict(l=0, r=0, t=40, b=0))
                st.plotly_chart(fig, use_container_width=True)
                
                # Alerts Expander
                alerts = session.query(AlertLog).filter(AlertLog.website_id == selected_site.id).order_by(AlertLog.timestamp.desc()).limit(10).all()
                if alerts:
                    st.markdown("#### 🔔 Recent Security & Health Alerts")
                    for a in alerts:
                        icon = "🚨" if "DOWN" in a.alert_type else "✅" if "UP" in a.alert_type else "🔍"
                        st.markdown(f"""
                        <div style="background: rgba(30,41,59,0.5); padding: 12px; border-left: 4px solid #3b82f6; border-radius: 4px; margin-bottom: 8px;">
                            <span style="color: #64748b; font-size: 0.8rem;">{a.timestamp.strftime('%Y-%m-%d %H:%M:%S')}</span><br/>
                            {icon} <strong>{a.alert_type}</strong>: {a.message}
                        </div>
                        """, unsafe_allow_html=True)
                else:
                    st.success("No critical alerts recorded for this target.")
            else:
                st.info("Awaiting first check data...")

# --- HELP TAB (Telegram Setup) ---
with tab_help:
    st.markdown("## 📩 Telegram Notification Setup")
    st.markdown("""
    Follow these steps to receive real-time alerts on your phone whenever a site goes down or content changes.
    
    ### 1️⃣ Create Your Bot
    1. Open Telegram and search for [**@BotFather**](https://t.me/BotFather).
    2. Click 'Start' and send `/newbot`.
    3. Choose a name (e.g., `MyMonitorBot`).
    4. Copy the **API Token** provided (looks like `12345678:ABC-DEF1234...`).
    
    ### 2️⃣ Get Your Chat ID
    1. Search for [**@userinfobot**](https://t.me/userinfobot) on Telegram.
    2. Click 'Start'.
    3. It will reply with your **Id** (a series of numbers).
    
    ### 3️⃣ Update Configuration
    1. Open the `.env` file in the project directory.
    2. Fill in your details:
       ```bash
       TELEGRAM_BOT_TOKEN=your_copied_token
       TELEGRAM_CHAT_ID=your_id_number
       ```
    3. Restart calculations or background service.
    
    ### 🔔 What Alerts will I get?
    - **Website DOWN**: Sent after 3 consecutive failures.
    - **Website RECOVERED**: Sent as soon as it's back up.
    - **Content Change**: Sent when OSINT hashing detects code/text modification.
    - **High Latency**: Sent if response time exceeds 5 seconds.
    """)
    if st.button("Test Telegram Connection", use_container_width=True):
        st.info("Sending test message... check your .env configuration if it doesn't arrive.")
        from alerts.telegram_bot import TelegramBot
        bot = TelegramBot()
        if bot.send_message("🛡️ *SiteMonitor Test*: Connection successful!"):
            st.success("Test message sent!")
        else:
            st.error("Failed to send. Double check your Token and Chat ID in `.env`")

# Auto-refresh logic (only if enabled)
if st.sidebar.checkbox("Real-time Mode (10s Auto-refresh)", value=False):
    time.sleep(10)
    st.rerun()
