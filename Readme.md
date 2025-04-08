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

## ⚙️ Setup Instructions

1. **Clone the repo**
```bash
git clone https://github.com/yourusername/nikassistant.git
cd nikassistant
```

2. **Install dependencies**
```bash
pip install -r requirements.txt
```

3. **Add your credentials in `.env`**
```
EMAIL_USER=youremail@gmail.com
EMAIL_PASS=your_app_password
GOOGLE_API_KEY=your_google_api_key
FIREBASE_KEY=your_firebase_key
```

4. **Run the app**
```bash
streamlit run app.py
```

---

## 🧪 Modules Breakdown

- **`scheduler.py`** – Runs background jobs for reminders
- **`email_service.py`** – Sends task reminders and fetches inbox summaries
- **`calendar_service.py`** – Manages Google Calendar integration
- **`notification_service.py`** – Sends desktop and mobile notifications
- **`speech_to_text.py`** – Optional voice assistant input

---

## 📌 Future Improvements

- Add multi-user login with authentication
- Integrate ChatGPT for smart suggestions
- Cross-platform mobile app using Flutter or React Native

---

## 📃 License

This project is licensed under the MIT License.

---

## 👨‍💻 Developed by Nikhil Soni

Connect with me on [LinkedIn](https://www.linkedin.com/in/nikhil-soni-14b56b241/) | Portfolio: [nikhilij.github.io/nikhil-soni-portfolio](https://nikhilij.github.io/nikhil-soni-portfolio)

