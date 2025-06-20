# 🧠 NikAssistant

**NikAssistant** is a smart, personalized productivity assistant built using Python and Streamlit. Designed to help users manage daily tasks, receive important email reminders, get notified across devices, and maintain calendar schedules effortlessly.

---

## 🚀 Features

- ✅ Personalized task manager with daily/weekly views
- 📩 Sends task reminders via email
- 📬 Fetches important email updates from your inbox
- 🔔 Notifies you on both mobile and desktop devices
- 📆 Schedules meetings and syncs with Google Calendar
- 🗣️ Voice input for tasks and reminders (optional)
- 🗒️ Quick notes and smart to-do dashboard

---

## 🛠️ Tech Stack

- **Frontend**: Streamlit
- **Backend**: Python, APScheduler
- **Email**: SMTP, Gmail API
- **Notifications**: Plyer, Firebase (optional)
- **Calendar**: Google Calendar API
- **Voice Input**: SpeechRecognition (optional)

---

## 📁 Project Structure

```
nikassistant/
├── .env                         # API keys (SMTP, Firebase, Google API)
├── README.md                    # Project documentation
├── requirements.txt             # Python dependencies
├── app.py                       # Main Streamlit app
├── config.py                    # Configurations and constants
├── data/                        # Stores tasks and notes (JSON/DB)
│   ├── tasks.json
│   ├── notes.json
├── backend/                     # Core backend functionality
│   ├── scheduler.py             # Background scheduler for reminders
│   ├── email_service.py         # Email sending and fetching
│   ├── notification_service.py  # Push/desktop notifications
│   ├── calendar_service.py      # Google Calendar integration
│   ├── speech_to_text.py        # Voice input module
├── ui/                          # Streamlit UI components
│   ├── dashboard.py
│   ├── task_panel.py
│   ├── calendar_view.py
│   ├── notes_panel.py
├── utils/                       # Helper modules
│   ├── helper.py
│   ├── email_parser.py
│   ├── notifier.py
└── static/                      # Styles and icons
    ├── styles.css
    └── icons/
```

---

## 🚀 Quick Start

### Option 1: Automated Setup (Recommended)
```bash
# Run the setup script
./setup.sh

# Start the application
./start.sh
```

### Option 2: Manual Setup
1. **Clone the repository**
```bash
git clone https://github.com/yourusername/nikassistant.git
cd nikassistant
```

2. **Create virtual environment**
```bash
python3 -m venv nikassistant_env
source nikassistant_env/bin/activate  # On Windows: nikassistant_env\Scripts\activate
```

3. **Install dependencies**
```bash
pip install -r requirements.txt
```

4. **Configure environment**
```bash
# Copy the example environment file
cp .env.example .env

# Edit .env with your credentials
nano .env  # or use your preferred editor
```

5. **Run the application**
```bash
streamlit run app.py
```

---

## ⚙️ Configuration

### Required Settings
Edit the `.env` file with your actual credentials:

```env
# Email Configuration (Required for email notifications)
EMAIL_USER=your_email@gmail.com
EMAIL_PASS=your_gmail_app_password

# Google Calendar API (Optional - for calendar integration)
GOOGLE_API_KEY=your_google_api_key
GOOGLE_CALENDAR_ID=primary

# Additional Settings
DEBUG=False
APP_PORT=8501
```

### Setting up Gmail App Password
1. Go to [Google Account Settings](https://myaccount.google.com/)
2. Enable 2-Factor Authentication
3. Generate an App Password for "Mail"
4. Use this app password in the `.env` file

### Setting up Google Calendar API
1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select existing
3. Enable Google Calendar API
4. Create credentials (API key)
5. Add the API key to `.env` file

---

## 📱 Features Overview

### 📊 Dashboard
- Task completion statistics
- Upcoming deadlines
- Calendar overview
- Performance metrics

### 📝 Task Management
- Create, edit, and delete tasks
- Set priorities and due dates
- Category organization
- Status tracking
- Bulk operations

### 📄 Notes Management
- Rich text notes
- Categorization and tagging
- Search functionality
- Private/public notes

### 📅 Calendar Integration
- Google Calendar sync
- Event creation from tasks
- Monthly/weekly views
- Reminder scheduling

### 🔔 Smart Notifications
- Desktop notifications
- Email reminders
- Overdue task alerts
- Daily summaries

### 🎤 Voice Input (Optional)
- Voice-to-task conversion
- Voice notes
- Hands-free operation

---

## 🛠️ Development

### Project Structure
```
nikassistant/
├── app.py                      # Main Streamlit application
├── config.py                   # Configuration settings
├── requirements.txt            # Python dependencies
├── setup.sh                    # Automated setup script
├── start.sh                    # Application launcher
├── .env.example               # Environment template
├── README.md                  # This file
├── data/                      # Data storage
│   ├── tasks.json            # Tasks database
│   ├── notes.json            # Notes database
│   └── calendar.json         # Calendar cache
├── backend/                   # Core services
│   ├── scheduler.py          # Background task scheduler
│   ├── email_service.py      # Email functionality
│   ├── notification_service.py # Notification system
│   ├── calendar_service.py   # Google Calendar integration
│   └── speech_to_text.py     # Voice recognition
├── ui/                       # User interface components
│   ├── dashboard.py          # Main dashboard
│   ├── task_panel.py         # Task management UI
│   ├── notes_panel.py        # Notes management UI
│   └── calendar_view.py      # Calendar interface
├── utils/                    # Utility functions
│   └── helper.py            # Common helper functions
└── logs/                    # Application logs
```

### Adding New Features
1. Create new modules in appropriate directories
2. Update `config.py` for new settings
3. Add UI components in the `ui/` directory
4. Update the main `app.py` navigation

---

## 🔧 Troubleshooting

### Common Issues

**Import Errors:**
```bash
# Install missing packages
pip install -r requirements.txt

# Or install specific packages
pip install streamlit apscheduler plyer
```

**Permission Errors (Linux/Mac):**
```bash
# Make scripts executable
chmod +x setup.sh start.sh
```

**Microphone Issues:**
```bash
# Install audio dependencies
sudo apt-get install portaudio19-dev python3-pyaudio  # Ubuntu/Debian
brew install portaudio  # macOS
```

**Google Calendar API Issues:**
- Ensure API is enabled in Google Cloud Console
- Check API key permissions
- Verify calendar ID is correct

### Performance Tips
- Close unused browser tabs
- Limit concurrent background tasks
- Regular cleanup of old tasks/notes
- Use filters for large datasets

---

## 📋 Usage Guide

### Creating Your First Task
1. Navigate to "📝 Tasks" page
2. Click "➕ Add New Task"
3. Fill in task details
4. Set due date and priority
5. Click "Create Task"

### Setting Up Notifications
1. Go to "🔔 Notifications" page
2. Configure notification preferences
3. Test notifications
4. Set up email/calendar integration

### Voice Input Setup
1. Ensure microphone permissions
2. Go to Settings → Voice Input
3. Test microphone
4. Use "🎤 Voice Input" feature

---

## 🧪 Testing

### Quick System Test
```bash
# Test notification system
python -c "from backend.notification_service import NotificationService; ns = NotificationService(); ns.test_notification()"

# Test email service
python -c "from backend.email_service import EmailService; es = EmailService(); print('Email service loaded')"
```

---

## 📌 Roadmap

### Version 2.0 (Planned)
- [ ] Multi-user support
- [ ] Mobile app (React Native)
- [ ] AI-powered task suggestions
- [ ] Team collaboration features
- [ ] Advanced analytics dashboard

### Version 1.5 (Next)
- [ ] Theme customization
- [ ] Export/import functionality
- [ ] Advanced search filters
- [ ] Recurring tasks
- [ ] Integration with more services

---

## 🤝 Contributing

We welcome contributions! Please see our contributing guidelines:

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

### Development Setup
```bash
# Clone your fork
git clone https://github.com/YOUR-USERNAME/nikassistant.git

# Create development branch
git checkout -b feature/your-feature-name

# Install development dependencies
pip install -r requirements.txt

# Make your changes and test
streamlit run app.py
```

---

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## 👨‍💻 About the Developer

**Nikhil Soni** - Full Stack Developer & AI Enthusiast

- 🌐 Portfolio: [nikhilij.github.io/nikhil-soni-portfolio](https://nikhilij.github.io/nikhil-soni-portfolio)
- 💼 LinkedIn: [linkedin.com/in/nikhil-soni-14b56b241](https://www.linkedin.com/in/nikhil-soni-14b56b241/)
- 📧 Email: contact@nikhilsoni.dev

---

## 🙏 Acknowledgments

- Streamlit team for the amazing framework
- Google for Calendar and Speech APIs
- Open source community for various libraries
- Beta testers and contributors

---

<div align="center">
  <p><strong>🧠 NikAssistant - Your Personal Productivity Companion</strong></p>
  <p>Made with ❤️ and ☕</p>
</div>

