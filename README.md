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

## Deployment Guide

### Option 1: Deploy on Railway (Recommended - Easy)

Railway supports both FastAPI and Streamlit with automatic deployments.

1. **Create Railway Account**: Go to [railway.app](https://railway.app) and sign up

2. **Create New Project**: Click "New Project" → "Deploy from GitHub repo"

3. **Connect Repository**: Select `Hemalathajagan/multitask_agent`

4. **Add Environment Variables** in Railway dashboard:
   ```
   OPENAI_API_KEY=your-openai-api-key
   SECRET_KEY=your-secret-key-here
   API_HOST=0.0.0.0
   API_PORT=8000
   ```

5. **Configure Services**: You'll need two services:
   - **Backend Service**:
     - Start command: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
   - **Frontend Service**:
     - Start command: `streamlit run streamlit_app/app.py --server.port $PORT --server.address 0.0.0.0`

6. **Update Frontend API URL**: In `streamlit_app/utils/api_client.py`, change:
   ```python
   API_BASE_URL = "https://your-backend-service.railway.app"
   ```

### Option 2: Deploy on Render

1. **Create Render Account**: Go to [render.com](https://render.com)

2. **Create Web Service for Backend**:
   - Connect GitHub repo
   - Build Command: `pip install -r requirements.txt`
   - Start Command: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
   - Add environment variables (OPENAI_API_KEY, SECRET_KEY)

3. **Create Web Service for Frontend**:
   - Start Command: `streamlit run streamlit_app/app.py --server.port $PORT --server.address 0.0.0.0`
   - Update API_BASE_URL to point to backend URL

### Option 3: Deploy on Heroku

1. **Create Procfile** in project root:
   ```
   web: uvicorn app.main:app --host 0.0.0.0 --port $PORT
   ```

2. **Deploy**:
   ```bash
   heroku create your-app-name
   heroku config:set OPENAI_API_KEY=your-key SECRET_KEY=your-secret
   git push heroku main
   ```

3. **For Streamlit**: Deploy separately or use Streamlit Cloud

### Option 3: Deploy on Streamlit Cloud (Frontend Only)

Best for the Streamlit frontend when backend is hosted elsewhere.

1. Go to [share.streamlit.io](https://share.streamlit.io)
2. Connect your GitHub repository
3. Set main file path: `streamlit_app/app.py`
4. Add secrets in Streamlit Cloud dashboard

### Option 4: Deploy with Docker

1. **Create Dockerfile**:
   ```dockerfile
   FROM python:3.11-slim
   WORKDIR /app
   COPY requirements.txt .
   RUN pip install -r requirements.txt
   COPY . .
   EXPOSE 8000 8501
   CMD ["sh", "-c", "uvicorn app.main:app --host 0.0.0.0 --port 8000 & streamlit run streamlit_app/app.py --server.port 8501 --server.address 0.0.0.0"]
   ```

2. **Build and Run**:
   ```bash
   docker build -t multitask-agent .
   docker run -p 8000:8000 -p 8501:8501 -e OPENAI_API_KEY=your-key -e SECRET_KEY=your-secret multitask-agent
   ```

### Option 5: Deploy on AWS/GCP/Azure

For production deployments, consider:
- **AWS**: ECS/Fargate with Application Load Balancer
- **GCP**: Cloud Run (serverless containers)
- **Azure**: Container Apps

### Important Notes for Deployment

1. **Database**: For production, replace SQLite with PostgreSQL:
   ```python
   # In app/db/database.py
   DATABASE_URL = "postgresql+asyncpg://user:pass@host/db"
   ```

2. **CORS**: Update allowed origins in `app/main.py`:
   ```python
   allow_origins=["https://your-frontend-domain.com"]
   ```

3. **Environment Variables**: Never commit `.env` - always set via platform dashboard

4. **API URL**: Update `API_BASE_URL` in `streamlit_app/utils/api_client.py` to match your deployed backend URL

## License

MIT License
