# Multi-Agent Task Assistant

A powerful AI-powered task management system that uses three coordinated agents (Planner, Executor, Reviewer) to break down, execute, and validate your tasks automatically.

![Python](https://img.shields.io/badge/Python-3.11+-blue.svg)
![FastAPI](https://img.shields.io/badge/FastAPI-0.109+-green.svg)
![Streamlit](https://img.shields.io/badge/Streamlit-1.31+-red.svg)
![License](https://img.shields.io/badge/License-MIT-yellow.svg)

## Features

- **Multi-Agent AI Workflow**
  - **Planner Agent**: Analyzes your objective and creates detailed task plans
  - **Executor Agent**: Executes each subtask with comprehensive outputs
  - **Reviewer Agent**: Validates work quality and provides approval

- **User Authentication**
  - Secure registration and login
  - JWT token-based sessions
  - Argon2id password hashing (industry standard)

- **Professional UI**
  - Clean, modern Streamlit interface
  - Real-time agent conversation display
  - Task dashboard and history
  - User profile with photo upload

- **RESTful API**
  - FastAPI backend with async support
  - WebSocket for real-time updates
  - SQLite database (easily upgradable to PostgreSQL)

## Architecture

```
┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│   Streamlit UI  │◄───►│   FastAPI API   │◄───►│  AutoGen Agents │
│   (Frontend)    │     │   (Backend)     │     │  (Multi-Agent)  │
└─────────────────┘     └─────────────────┘     └─────────────────┘
                              │
                              ▼
                    ┌─────────────────┐
                    │   SQLite DB     │
                    └─────────────────┘
```

## Quick Start (Local Development)

### 1. Clone the Repository

```bash
git clone https://github.com/Hemalathajagan/multitask_agent.git
cd multitask_agent
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Configure Environment

Create a `.env` file from the example:

```bash
cp .env.example .env
```

Edit `.env` with your settings:

```env
OPENAI_API_KEY=your-openai-api-key-here
SECRET_KEY=your-secret-key-here
```

> Generate a secret key: `python -c "import secrets; print(secrets.token_hex(32))"`

### 4. Run the Application

**Terminal 1 - Backend:**
```bash
python -m uvicorn app.main:app --reload
```

**Terminal 2 - Frontend:**
```bash
streamlit run streamlit_app/app.py
```

### 5. Access the App

- **Frontend**: http://localhost:8501
- **Backend API**: http://127.0.0.1:8000
- **API Docs**: http://127.0.0.1:8000/docs

## Usage

1. **Register** - Create an account with email and password
2. **Login** - Sign in to your account
3. **Create Task** - Enter your objective (e.g., "Create a marketing plan for a mobile app")
4. **Watch Agents** - See Planner → Executor → Reviewer collaborate
5. **View Results** - Check the detailed plan, execution, and review

## Project Structure

```
multitask_agent/
├── app/                        # FastAPI Backend
│   ├── main.py                 # App entry point
│   ├── config.py               # Configuration
│   ├── agents/                 # AutoGen Agents
│   │   ├── planner.py          # Planning agent
│   │   ├── executor.py         # Execution agent
│   │   ├── reviewer.py         # Review agent
│   │   └── orchestrator.py     # Agent coordination
│   ├── api/                    # API Routes
│   │   ├── auth.py             # Authentication
│   │   ├── tasks.py            # Task management
│   │   └── websocket.py        # Real-time updates
│   ├── auth/                   # Auth utilities
│   ├── db/                     # Database
│   └── schemas/                # Pydantic models
├── streamlit_app/              # Streamlit Frontend
│   ├── app.py                  # Main app
│   ├── pages/                  # App pages
│   │   ├── 1_dashboard.py      # Task dashboard
│   │   ├── 2_history.py        # Task history
│   │   └── 3_profile.py        # User profile
│   ├── components/             # UI components
│   └── utils/                  # Utilities
├── requirements.txt
├── .env.example
└── README.md
```

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/auth/register` | Register new user |
| POST | `/auth/login` | Login user |
| POST | `/auth/logout` | Logout user |
| GET | `/auth/me` | Get current user |
| PUT | `/auth/profile` | Update profile |
| PUT | `/auth/password` | Change password |
| PUT | `/auth/photo` | Update profile photo |
| POST | `/tasks/` | Create new task |
| GET | `/tasks/` | List all tasks |
| GET | `/tasks/{id}` | Get task details |

## Technology Stack

| Component | Technology |
|-----------|------------|
| Backend | FastAPI, Python 3.11+ |
| Frontend | Streamlit |
| AI Agents | AutoGen 0.4+, OpenAI GPT-4o-mini |
| Database | SQLite (async SQLAlchemy) |
| Authentication | JWT, Argon2id |
| Real-time | WebSockets |

---

## Deployment Guide

### Best Free Option: Render (Backend) + Streamlit Cloud (Frontend)

This combination gives you **completely free** hosting with generous limits.

---

### Step 1: Deploy Backend on Render (Free)

1. **Go to [render.com](https://render.com)** and sign up (free)

2. **Click "New +" → "Web Service"**

3. **Connect your GitHub repo**: `Hemalathajagan/multitask_agent`

4. **Configure the service**:
   - **Name**: `multitask-agent-api`
   - **Region**: Choose nearest to you
   - **Branch**: `main`
   - **Runtime**: `Python 3`
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`

5. **Add Environment Variables** (click "Advanced"):
   | Key | Value |
   |-----|-------|
   | `OPENAI_API_KEY` | Your OpenAI API key |
   | `SECRET_KEY` | A random secure string |
   | `API_HOST` | `0.0.0.0` |

6. **Click "Create Web Service"**

7. **Wait for deployment** - You'll get a URL like: `https://multitask-agent-api.onrender.com`

> **Note**: Free tier sleeps after 15 min of inactivity. First request may take 30-60 seconds to wake up.

---

### Step 2: Update Frontend API URL

Before deploying frontend, update the API URL:

**Edit `streamlit_app/utils/api_client.py`:**

```python
# Change this line:
API_BASE_URL = "http://127.0.0.1:8000"

# To your Render URL:
API_BASE_URL = "https://multitask-agent-api.onrender.com"
```

**Commit and push**:
```bash
git add .
git commit -m "Update API URL for deployment"
git push
```

---

### Step 3: Deploy Frontend on Streamlit Cloud (Free)

1. **Go to [share.streamlit.io](https://share.streamlit.io)** and sign in with GitHub

2. **Click "New app"**

3. **Configure**:
   - **Repository**: `Hemalathajagan/multitask_agent`
   - **Branch**: `main`
   - **Main file path**: `streamlit_app/app.py`

4. **Click "Deploy!"**

5. **Your app will be live** at: `https://your-app-name.streamlit.app`

---

### Alternative Free Options

| Platform | Free Tier | Best For |
|----------|-----------|----------|
| **Render** | 750 hours/month | Backend API |
| **Streamlit Cloud** | Unlimited for public repos | Frontend |
| **Railway** | $5 credit/month | Full stack |
| **Hugging Face Spaces** | Unlimited | AI/ML apps |
| **Fly.io** | 3 shared VMs | Containers |

---

### Production Deployment Tips

1. **Use PostgreSQL** instead of SQLite:
   ```python
   DATABASE_URL = "postgresql+asyncpg://user:pass@host/db"
   ```

2. **Update CORS** in `app/main.py`:
   ```python
   allow_origins=["https://your-frontend.streamlit.app"]
   ```

3. **Use environment variables** - Never commit `.env` files

4. **Enable HTTPS** - All platforms above provide free SSL

---

## Environment Variables

| Variable | Description | Required |
|----------|-------------|----------|
| `OPENAI_API_KEY` | Your OpenAI API key | Yes |
| `SECRET_KEY` | JWT signing key | Yes |
| `API_HOST` | API host (default: 127.0.0.1) | No |
| `API_PORT` | API port (default: 8000) | No |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | Token expiry (default: 60) | No |

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- [AutoGen](https://github.com/microsoft/autogen) - Multi-agent framework
- [FastAPI](https://fastapi.tiangolo.com/) - Modern Python web framework
- [Streamlit](https://streamlit.io/) - App framework for ML/AI

---

**Made with by [Hemalathajagan](https://github.com/Hemalathajagan)**
