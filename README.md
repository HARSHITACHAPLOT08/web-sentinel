# 🌐 Website Monitoring & OSINT Alert System

A full-stack, modular Python system for tracking website uptime, response times, and content changes (OSINT). Designed as a production-level SaaS MVP.

## 🚀 Key Features
- **Multi-Site Management**: Monitor multiple URLs with custom intervals.
- **Uptime Monitoring**: Real-time HTTP health checks.
- **OSINT Content Tracking**: Detects website changes using SHA256 hashing (cleans dynamic scripts to reduce noise).
- **Intelligent Alerting**: Real-time Telegram notifications for downtime, recovery, content changes, and high latency.
- **Interactive Dashboard**: Streamlit-powered UI with latency graphs and uptime statistics.
- **Modular Architecture**: Clean separation between monitoring engine, database layer, and dashboard.

## 📂 Project Structure
```
websitemonitor/
├── monitors/       # Core checking & hashing logic
├── alerts/         # Telegram integration
├── database/       # SQLAlchemy models & session management
├── dashboard/      # Streamlit web interface
├── main.py         # Background scheduler (APScheduler)
├── config.py       # Centralized configuration
└── requirements.txt
```

## 🛠️ Setup Guide

### 1. Prerequisites
- Python 3.9+
- A Telegram Bot Token (from [@BotFather](https://t.me/BotFather))
- Your Telegram Chat ID (from [@userinfobot](https://t.me/userinfobot))

### 2. Installation
```powershell
# Clone or move to the project directory
cd websitemonitor

# Install dependencies
pip install -r requirements.txt
```

### 3. Configuration
1. Copy `.env.example` to `.env`:
   ```powershell
   copy .env.example .env
   ```
2. Edit `.env` and add your `TELEGRAM_BOT_TOKEN` and `TELEGRAM_CHAT_ID`.

### 4. Running the System
You need to run **two** separate processes:

**Terminal 1: Background Monitor**
```powershell
python main.py
```

**Terminal 2: Dashboard UI**
```powershell
streamlit run dashboard/app.py
```

## 🔐 Security Best Practices
- **Environment Variables**: Never commit your `.env` file. It's listed in `.gitignore` by default.
- **User Agent**: The monitor identifies as `WebsiteMonitor/1.0`. You can change this in `config.py`.
- **Concurrency**: SQLite is used with a connection pool that supports multi-threading safely.

## 🚢 Deployment
This system is ready for deployment on:
- **VPS (Ubuntu/Debian)**: Use `systemd` to manage `main.py` and `app.py`.
- **Railway/Render**: 
  - Add a "Worker" service for `python main.py`.
  - Add a "Web" service for `streamlit run dashboard/app.py`.
