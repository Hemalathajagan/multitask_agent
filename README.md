# Multi-Agent Task Assistant

A multi-agent system using Python, AutoGen, and OpenAI API with three coordinated agents (Planner, Executor, Reviewer), a professional Streamlit UI, and full authentication.

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

## Features

- **Multi-Agent Workflow**: Three specialized agents work together
  - **Planner**: Analyzes objectives and creates detailed task plans
  - **Executor**: Executes each subtask with detailed outputs
  - **Reviewer**: Validates work and provides final approval

- **Authentication**: Secure user management with Argon2id password hashing and JWT tokens

- **Real-time Updates**: WebSocket support for live agent message streaming

- **Professional UI**: Clean Streamlit interface with dashboard and task history

## Setup

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Configure Environment

Edit the `.env` file with your settings:

```env
# Required: Your OpenAI API key
OPENAI_API_KEY=your-openai-api-key-here

# Change in production
SECRET_KEY=your-secret-key-change-in-production
```

### 3. Run the Backend

```bash
python -m uvicorn app.main:app --reload
```

The API will be available at `http://127.0.0.1:8000`

### 4. Run the Frontend

In a separate terminal:

```bash
streamlit run streamlit_app/app.py
```

The UI will be available at `http://localhost:8501`

## Usage

1. **Register**: Create a new account with email, username, and password
2. **Login**: Sign in with your credentials
3. **Create Task**: Enter your objective in the task input form
4. **Watch Agents**: See the Planner, Executor, and Reviewer collaborate
5. **View Results**: Check the plan, execution, and review results

## API Endpoints

### Authentication
- `POST /auth/register` - Register new user
- `POST /auth/login` - Login and get JWT token
- `POST /auth/logout` - Logout and clear session
- `GET /auth/me` - Get current user info

### Tasks
- `POST /tasks/` - Create new task
- `GET /tasks/` - List user's tasks
- `GET /tasks/{task_id}` - Get task details

### WebSocket
- `WS /ws/task/{task_id}` - Real-time task updates

## Project Structure

```
ai_agent/
├── app/
│   ├── main.py              # FastAPI entry point
│   ├── config.py            # Environment configuration
│   ├── agents/              # AutoGen agents
│   │   ├── planner.py
│   │   ├── executor.py
│   │   ├── reviewer.py
│   │   └── orchestrator.py
│   ├── api/                 # API endpoints
│   │   ├── auth.py
│   │   ├── tasks.py
│   │   └── websocket.py
│   ├── auth/                # Authentication
│   │   ├── security.py
│   │   └── dependencies.py
│   ├── db/                  # Database
│   │   ├── database.py
│   │   ├── models.py
│   │   └── crud.py
│   └── schemas/             # Pydantic models
├── streamlit_app/
│   ├── app.py               # Main Streamlit app
│   ├── pages/
│   ├── components/
│   └── utils/
├── .env
├── requirements.txt
└── README.md
```

## Technology Stack

- **Backend**: FastAPI, SQLAlchemy, SQLite
- **Agents**: AutoGen 0.4+, OpenAI GPT-4o-mini
- **Frontend**: Streamlit
- **Auth**: Argon2id, JWT
- **Real-time**: WebSockets
