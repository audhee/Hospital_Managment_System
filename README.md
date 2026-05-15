# Hospital Management System (HMS)

A modern, event-driven Hospital Management System featuring real-time dashboards, an advanced AI voice assistant, and a highly flexible appointment booking engine. Built with Django and Django Channels to handle asynchronous tasks and real-time WebSocket communications.

## 🚀 Key Features

### 1. Real-Time Operations
- **Doctor Dashboards:** Real-time, refresh-free dashboard updates powered by Django Channels and WebSockets.
- **Event-Driven Architecture:** Utilizes Django signals to decouple core business logic from notification events, ensuring a scalable and maintainable codebase.

### 2. Arohan AI Voice Assistant
- **Ultra-Low Latency Pipeline:** A real-time audio streaming pipeline achieving sub-second conversational responsiveness over WebSockets.
- **Advanced Stack:** Uses `faster-whisper` for high-speed speech-to-text, the `phi3` LLM for intelligent query resolution, and `edge-tts` for natural, word-by-word streaming voice synthesis.
- **RAG Integration:** Augmented context retrieval to assist patients efficiently.

### 3. Smart Appointment Booking
- **Flexible Scheduling:** Moves beyond fixed-slot booking to allow arbitrary booking times.
- **Conflict Management:** Implements smart overlap detection and automated scheduling suggestions for next-available times.
- **Secure Verification:** End-to-end verification code generation and validation for securing appointments.

### 4. Patient & Doctor Portals
- **Automated PDF Reports:** Users can instantly download detailed appointment summaries in PDF format.
- **Comprehensive Dashboards:** Dedicated views for patients to track appointments and for doctors to manage schedules and view patient statuses.

## 🛠️ Technology Stack

- **Backend Framework:** Django, Django REST Framework
- **Asynchronous Protocol:** ASGI (Daphne)
- **Real-Time Communication:** Django Channels (WebSockets)
- **Database:** SQLite (Configured as default)
- **AI / Voice Components:** faster-whisper, edge-tts, phi3
- **Frontend:** HTML5, CSS3, JavaScript (Vanilla JS with WebSocket API for streaming audio/events)

## 📁 Project Structure

```
HMS/
├── HMS/                  # Core Django project settings and ASGI/WSGI configs
│   ├── asgi.py           # ASGI configuration for WebSockets/Channels
│   ├── settings.py       # Main settings file
│   ├── urls.py           # Root URL routing
│   └── wsgi.py
├── clinic/               # Main application app containing the business logic
│   ├── api_views.py      # REST APIs for booking and voice agent integration
│   ├── consumers.py      # WebSocket consumers for real-time dashboards & audio streaming
│   ├── routing.py        # WebSocket routing
│   ├── signals.py        # Event triggers and decouple logic
│   ├── views.py          # Standard Django views and PDF generation logic
│   └── models.py         # Database schema (Users, Appointments, etc.)
└── manage.py             # Django execution script
```

## ⚙️ Installation & Setup

1. **Clone the repository:**
   ```bash
   git clone <repository-url>
   cd HMS/HMS
   ```

2. **Set up a virtual environment:**
   ```bash
   python -m venv venv
   # Windows
   venv\Scripts\activate
   # Linux/macOS
   source venv/bin/activate
   ```

3. **Install dependencies:**
   *(Ensure you have your environment dependencies installed. If `requirements.txt` is provided:)*
   ```bash
   pip install -r requirements.txt
   ```
   *Core dependencies typically include: `django`, `channels`, `daphne`, `djangorestframework`, `faster-whisper`, `edge-tts`.*

4. **Apply database migrations:**
   ```bash
   python manage.py migrate
   ```

5. **Run the development server (ASGI):**
   ```bash
   python manage.py runserver
   ```
   *Note: Because this project uses WebSockets via Django Channels, Daphne will automatically be used to serve the application on port 8000.*

6. **Access the application:**
   Open a web browser and navigate to `http://127.0.0.1:8000/`.

## 🤝 Contributing

When contributing to this repository, please ensure that all real-time functionalities (like dashboard updates and AI voice responses) are rigorously tested over WebSocket connections to avoid pipeline latency or disconnection errors.
