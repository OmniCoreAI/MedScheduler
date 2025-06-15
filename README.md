# 🏥 MediBook - AI Medical Appointment Booking System

A professional AI-powered medical appointment booking system with session management, built with FastAPI, LangChain, OpenAI, and Streamlit. Features both a conversational API and a beautiful web interface.

## 🏗️ Project Structure

```
Booking/
├── src/                          # Source code
│   ├── __init__.py
│   ├── models/                   # Data models
│   │   ├── __init__.py
│   │   ├── base.py              # Base enums and types
│   │   ├── session.py           # Session-related models
│   │   ├── chat.py              # Chat-related models
│   │   └── appointment.py       # Appointment models
│   ├── services/                # Business logic
│   │   ├── __init__.py
│   │   ├── session_manager.py   # Session management
│   │   ├── chat_history.py      # Chat history service
│   │   ├── appointment.py       # Appointment service
│   │   └── ai_assistant.py      # AI assistant service
│   ├── api/                     # API endpoints
│   │   ├── __init__.py
│   │   └── routes.py            # All API routes
│   └── config/                  # Configuration
│       ├── __init__.py
│       └── settings.py          # Application settings
├── tests/                       # Test suite
│   ├── __init__.py
│   └── test_api.py             # API tests
├── static/                      # Static files
│   └── index.html              # Chat interface
├── data/                        # Data storage (auto-created)
│   ├── sessions/               # Session files
│   ├── chat_history/           # Chat history files
│   ├── appointments/           # Appointment files
│   └── available_slots.json    # Available time slots
├── main.py                     # FastAPI application entry point
├── streamlit_app.py            # Streamlit web interface
├── run_app.py                  # Script to run both servers
├── start.sh                    # Shell script for easy startup
├── requirements.txt            # Python dependencies
├── env.example                 # Environment variables example
└── README.md                   # This file
```

## 🚀 Features

### Core Features
- **Beautiful Web Interface**: Modern Streamlit frontend with real-time chat
- **Professional Session Management**: UUID-based sessions with 24-hour expiration
- **AI-Powered Conversations**: OpenAI GPT-4o-mini integration with LangChain
- **Step-by-Step Booking**: Guided appointment booking workflow
- **Persistent Storage**: File-based storage for sessions, chat history, and appointments
- **Real-time Chat**: WebSocket support for live conversations
- **REST API**: Complete HTTP API for all operations
- **Dual Interface**: Both web UI and API access

### Booking Workflow
1. **Greeting**: Welcome and introduction
2. **Name Collection**: Patient name gathering
3. **Phone Collection**: Contact information
4. **Symptoms Collection**: Medical symptoms/reason for visit
5. **Doctor Preference**: Doctor selection based on specialty
6. **Slot Selection**: Available time slot selection
7. **Confirmation**: Appointment confirmation
8. **Completion**: Final appointment details

### Available Doctors
- **Dr. Smith**: General Medicine
- **Dr. Johnson**: Cardiology  
- **Dr. Brown**: Dermatology

## 🛠️ Installation & Setup

### Prerequisites
- Python 3.8+
- OpenAI API key

### Installation Steps

1. **Clone and navigate to the project**:
   ```bash
   cd Booking
   ```

2. **Create virtual environment**:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment variables**:
   ```bash
   cp env.example .env
   # Edit .env and add your OpenAI API key
   ```

5. **Run the application**:

   **Option 1: Easy startup (Recommended)**
   ```bash
   ./start.sh
   ```

   **Option 2: Advanced server management**
   ```bash
   # Start both servers
   ./run_servers.sh start
   
   # Check server status
   ./run_servers.sh status
   
   # View logs
   ./run_servers.sh logs
   
   # Stop servers
   ./run_servers.sh stop
   
   # Restart servers
   ./run_servers.sh restart
   ```

   **Option 3: Python script (legacy)**
   ```bash
   python run_app.py
   ```

   **Option 4: Run servers separately**
   ```bash
   # Terminal 1 - FastAPI Backend
   python main.py
   
   # Terminal 2 - Streamlit Frontend
   streamlit run streamlit_app.py
   ```

The application will be available at:
- **Streamlit Web Interface**: `http://localhost:8501` (or custom `STREAMLIT_PORT`)
- **FastAPI Backend**: `http://localhost:8000` (or custom `PORT`)
- **API Documentation**: `http://localhost:8000/docs`

## 📚 API Documentation

### Session Management

#### Create Session
```http
POST /sessions
Content-Type: application/json

{
  "patient_email": "patient@example.com",
  "metadata": {}
}
```

#### Get Session Info
```http
GET /sessions/{session_id}
```

#### List All Sessions
```http
GET /sessions?status=active
```

### Chat Operations

#### Send Message
```http
POST /chat
Content-Type: application/json

{
  "session_id": "uuid-here",
  "message": "Hello, I'd like to book an appointment"
}
```

#### Get Chat History
```http
GET /chat-history/{session_id}
```

### WebSocket Chat
```javascript
const ws = new WebSocket('ws://localhost:8000/ws/{session_id}');
ws.send(JSON.stringify({message: "Hello"}));
```

### Utility Endpoints

#### Health Check
```http
GET /health
```

#### Cleanup Expired Sessions
```http
POST /cleanup
```

## 🧪 Testing

### Run Automated Tests
```bash
cd tests
python test_api.py
```

### Interactive Testing
```bash
python test_api.py interactive
```

### Test Coverage
- Complete booking flow simulation
- Session management operations
- Error handling scenarios
- Interactive chat testing

## 🔧 Configuration

### Environment Variables
See `env.example` for all available configuration options:

- `OPENAI_API_KEY`: Your OpenAI API key (required)
- `HOST`: Server host (default: 0.0.0.0)
- `PORT`: FastAPI backend port (default: 8000)
- `STREAMLIT_PORT`: Streamlit frontend port (default: 8501)
- `SESSION_TIMEOUT_HOURS`: Session expiration time (default: 24)
- `LOG_LEVEL`: Logging level (default: INFO)

### Port Configuration
You can customize the ports by setting environment variables:

```bash
# Set custom ports
export PORT=9000
export STREAMLIT_PORT=9001

# Or add to .env file
echo "PORT=9000" >> .env
echo "STREAMLIT_PORT=9001" >> .env

# Then start the application
./run_servers.sh start
```

### Settings Management
Configuration is managed through `src/config/settings.py` using Pydantic BaseSettings for type safety and validation.

## 🏥 Usage Examples

### Complete Booking Flow
```python
from tests.test_api import MedicalBookingAPIClient

client = MedicalBookingAPIClient()

# Create session
session = client.create_session("patient@example.com")

# Book appointment through conversation
messages = [
    "Hello, I'd like to book an appointment",
    "John Doe",
    "555-123-4567",
    "I have been having headaches",
    "I'd prefer Dr. Smith",
    "I'll take the 9:00 AM slot",
    "Yes, please confirm"
]

for message in messages:
    response = client.send_message(message)
    print(f"Assistant: {response['assistant_response']}")
```

### WebSocket Integration
```html
<script>
const ws = new WebSocket('ws://localhost:8000/ws/your-session-id');

ws.onmessage = function(event) {
    const data = JSON.parse(event.data);
    console.log('Assistant:', data.message);
};

function sendMessage(message) {
    ws.send(JSON.stringify({message: message}));
}
</script>
```

## 🔒 Security Features

- Session-based authentication
- Input validation with Pydantic models
- CORS configuration
- Error handling and logging
- Session expiration management

## 🚀 Deployment

### Production Setup
1. Set `DEBUG=false` in environment
2. Configure proper CORS origins
3. Use production WSGI server (e.g., Gunicorn)
4. Set up proper logging
5. Configure SSL/TLS

### Docker Deployment
```dockerfile
FROM python:3.9-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
CMD ["python", "main.py"]
```

## 🤝 Contributing

1. Follow the established project structure
2. Add tests for new features
3. Update documentation
4. Follow Python PEP 8 style guidelines
5. Use type hints throughout

## 📄 License

This project is licensed under the MIT License.

## 🆘 Support

For support and questions:
1. Check the API documentation at `/docs`
2. Run the test suite to verify functionality
3. Review the logs for debugging information
4. Use the interactive test mode for manual testing

---

**Built with ❤️ using FastAPI, LangChain, and OpenAI** 