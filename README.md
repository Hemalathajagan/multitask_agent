# Multi-Agent Task Assistant

A powerful AI-powered task automation system that uses three coordinated agents (Planner, Executor, Reviewer) to break down, execute, and validate your tasks automatically — with real-world tool execution, desktop automation, scheduling, and user confirmation at every step.

![Python](https://img.shields.io/badge/Python-3.11+-blue.svg)
![FastAPI](https://img.shields.io/badge/FastAPI-0.109+-green.svg)
![Streamlit](https://img.shields.io/badge/Streamlit-1.31+-red.svg)
![License](https://img.shields.io/badge/License-MIT-yellow.svg)

## What is This?

This is a **specialized AI-powered task automation tool** that uses **3 coordinated AI agents** to automatically plan, execute, and review any task you give it.

You provide a high-level objective (e.g., *"Research the latest AI trends and create a report"*), and three agents take over:

1. **Planner Agent** — Breaks the objective into subtasks with priorities and dependencies
2. **Executor Agent** — Executes each subtask using real-world tools (web search, file editing, email, browser/desktop automation, social media posting)
3. **Reviewer Agent** — Validates the work, checks quality, and approves or requests revisions

### Key Capabilities

- **Web Search & News** — Searches the internet in real-time using DuckDuckGo for current information
- **Desktop Automation** — Controls any desktop app (WhatsApp, Excel, browsers) via screen interaction
- **Browser Automation** — Fills forms, clicks buttons, takes screenshots in headless browsers
- **File Operations** — Creates, reads, and edits Excel/CSV files on your local machine
- **Email Sending** — Sends emails via SMTP with user-provided details
- **Social Media Posting** — Posts to Instagram, Twitter/X, LinkedIn, Facebook via official APIs
- **Task Scheduling** — Schedule tasks to run at a future time (persistent across restarts)
- **File Upload** — Upload files from your desktop to attach to tasks
- **User Confirmation** — Every tool action requires your approval before executing
- **Smart Stuck Detection** — Agent pauses and asks for your help when it gets confused or fails

### Target Users

Knowledge workers, researchers, content creators, and analysts who want to automate multi-step projects — instead of doing planning, execution, and review manually, the AI agents handle the entire workflow.

## How is This Different from ChatGPT?

| Aspect | ChatGPT (Single Agent) | This Project (Multi-Agent) |
|--------|----------------------|---------------------------|
| **Architecture** | One AI handles everything in a single response | Three specialized AIs collaborate on each task |
| **Quality Control** | No self-review — you catch mistakes | Reviewer agent checks quality before you see the output |
| **Workflow** | One-shot text generation | Structured Plan → Execute → Review pipeline |
| **Iteration** | You manually ask "try again" | Reviewer automatically sends work back for revision |
| **Real-World Actions** | Text only — cannot search, send emails, edit files | 27+ tools — web search, email, file editing, desktop/browser automation, social media |
| **Scheduling** | Not possible | Schedule tasks for future execution with persistent scheduling |
| **User Control** | No tool confirmation | Every action requires your approval before executing |
| **Safety** | N/A | Agent stops and asks for help when stuck instead of guessing |
| **Persistence** | Chat logs only | Tasks saved in database — re-run, continue, review history |
| **Real-time Tracking** | Not applicable | Watch each agent work live via WebSockets |

### When This Project is Better Than ChatGPT

- **Tasks requiring real-world actions** — web searches, sending emails, editing files, posting to social media
- **Complex multi-step tasks** (research plans, strategies, reports) — structured planning + self-review catches gaps
- **Tasks needing quality assurance** — the Reviewer agent forces quality improvement automatically
- **Scheduled/automated workflows** — run tasks at a specific future time
- **Desktop automation** — control apps like WhatsApp, Excel, browsers

### When ChatGPT is Better

- Simple questions and quick answers
- Casual conversation
- General-purpose tasks that don't need structured workflows

### The Honest Take

This project calls the **same underlying model** (GPT-4o-mini). The raw intelligence is identical. The advantage comes from the **workflow** — multiple passes, specialized roles, self-review, and most importantly, **real tool execution** instead of just generating text.

> **Think of it this way:** ChatGPT = one person answering questions. This project = a team of 3 specialists with access to your computer, the internet, and your apps — working on your task with your approval at every step.

## Features

- **Multi-Agent AI Workflow**
  - **Planner Agent**: Analyzes your objective and creates detailed task plans
  - **Executor Agent**: Executes each subtask using 27+ real-world tools
  - **Reviewer Agent**: Validates work quality and provides approval

- **27+ Real-World Tools**
  - **Research**: Web search, news search, webpage reader, API calls
  - **Files**: Create files, edit Excel (.xlsx), edit CSV, file upload/download
  - **Communication**: Send emails via SMTP
  - **Browser Automation**: Navigate, fill forms, click, screenshot, extract text
  - **Desktop Automation**: Find windows, click, type (unicode/emoji), hotkeys, screenshots
  - **Social Media**: Post to Instagram, Twitter/X, LinkedIn, Facebook
  - **Code Execution**: Run Python code in sandboxed environment

- **Task Scheduling**
  - Schedule tasks for future execution with date/time picker
  - Persistent scheduling survives server restarts (APScheduler + SQLAlchemy)
  - Cancel scheduled tasks before they run
  - Countdown timer shows time until execution

- **User Confirmation Flow**
  - Every tool action pauses and asks for your approval
  - Input forms for tools that need user details (email, social media content)
  - Approve or deny each action individually

- **Smart Stuck Detection**
  - Agent stops when it can't proceed and asks for your guidance
  - Detects: repeated tool denials, consecutive errors, revision loops, empty responses
  - You can provide instructions, change approach, or cancel the task

- **Privacy & Safety**
  - Desktop screenshots auto-delete after 5 minutes
  - Region screenshots available (captures only the target app area)
  - Temp screenshots excluded from database records
  - Agent instructed to never screenshot sensitive content

- **User Authentication**
  - Secure registration and login
  - JWT token-based sessions
  - Argon2id password hashing (industry standard)

- **Professional UI**
  - Clean, modern Streamlit interface with warm orange theme
  - Real-time agent conversation display
  - Task dashboard with scheduling, file upload, status badges
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
                              │                        │
                              ▼                        ▼
                    ┌─────────────────┐     ┌─────────────────┐
                    │   SQLite DB     │     │  27+ Tools      │
                    │   + Scheduler   │     │  (Web, Desktop, │
                    └─────────────────┘     │   Files, APIs)  │
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

**Optional configurations in `.env`:**
- SMTP settings for email tool
- Social media API credentials (Instagram, Twitter, LinkedIn, Facebook)
- See `.env.example` for all options

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
3. **Create Task** - Enter your objective (e.g., "Research latest AI trends and create a report")
4. **Schedule (Optional)** - Check "Schedule for later" and pick a date/time
5. **Upload Files (Optional)** - Attach files for the task to work with
6. **Watch Agents** - See Planner → Executor → Reviewer collaborate in real-time
7. **Approve Actions** - Each tool action asks for your confirmation before executing
8. **Provide Guidance** - If the agent gets stuck, it asks you what to do
9. **View Results** - Check the detailed plan, execution, and review

## Example Tasks

| Task | Tools Used |
|------|-----------|
| "Research the latest news about Tesla and create a summary" | web_search_news, read_webpage, create_file |
| "Send an email to john@example.com about the meeting" | send_email (asks for details via UI) |
| "Update cell A1 in C:/Users/me/report.xlsx to 'Q4 Revenue'" | edit_excel_file |
| "Message John on WhatsApp saying 'Meeting at 3pm'" | desktop_find_window, desktop_click, desktop_type_text |
| "Post 'Hello World' to Twitter" | post_to_twitter (asks for content review) |
| "Search for Python tutorials and save the best 5 links" | web_search, read_webpage, create_file |

## Project Structure

```
multitask_agent/
├── app/                        # FastAPI Backend
│   ├── main.py                 # App entry point + scheduler lifecycle
│   ├── config.py               # Configuration (API keys, SMTP, social media)
│   ├── scheduler.py            # APScheduler for task scheduling
│   ├── agents/                 # AutoGen Agents
│   │   ├── planner.py          # Planning agent
│   │   ├── executor.py         # Execution agent
│   │   ├── reviewer.py         # Review agent
│   │   ├── orchestrator.py     # Agent coordination + stuck detection
│   │   ├── interaction_manager.py  # Pause/resume for user confirmation
│   │   └── tools/              # 27+ real-world tools
│   │       ├── web_search.py       # DuckDuckGo search + news
│   │       ├── web_reader.py       # Webpage content extraction
│   │       ├── email_sender.py     # SMTP email
│   │       ├── file_manager.py     # File creation
│   │       ├── code_executor.py    # Sandboxed Python execution
│   │       ├── http_client.py      # REST API calls
│   │       ├── csv_handler.py      # CSV read/analyze/edit
│   │       ├── excel_handler.py    # Excel file editing (openpyxl)
│   │       ├── browser_automation.py  # Playwright browser control
│   │       ├── desktop_automation.py  # PyAutoGUI desktop control
│   │       ├── social_media.py     # Instagram/Twitter/LinkedIn/Facebook
│   │       ├── confirmed_tool.py   # User confirmation wrapper
│   │       └── _context.py         # Task ID context variable
│   ├── api/                    # API Routes
│   │   ├── auth.py             # Authentication
│   │   ├── tasks.py            # Task management + scheduling
│   │   ├── files.py            # File upload/download
│   │   ├── interactions.py     # User confirmation endpoints
│   │   └── websocket.py        # Real-time updates
│   ├── auth/                   # Auth utilities
│   ├── db/                     # Database models, CRUD, migrations
│   └── schemas/                # Pydantic models
├── streamlit_app/              # Streamlit Frontend
│   ├── app.py                  # Main app
│   ├── pages/                  # App pages
│   │   ├── 1_dashboard.py      # Task dashboard (scheduling, upload, confirmation UI)
│   │   ├── 2_history.py        # Task history
│   │   └── 3_profile.py        # User profile
│   ├── components/             # UI components
│   └── utils/                  # API client + utilities
├── requirements.txt
├── .env.example
├── quick.md
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
| POST | `/tasks/` | Create new task (with optional scheduling) |
| GET | `/tasks/` | List all tasks |
| GET | `/tasks/{id}` | Get task details |
| PUT | `/tasks/{id}` | Rename task |
| POST | `/tasks/{id}/rerun` | Re-run a task |
| POST | `/tasks/{id}/continue` | Create follow-up task |
| GET | `/tasks/scheduled/list` | List scheduled tasks |
| POST | `/tasks/{id}/cancel-schedule` | Cancel a scheduled task |
| POST | `/files/upload/{task_id}` | Upload file to task |
| GET | `/files/download/{task_id}/{filename}` | Download task file |
| GET | `/interactions/task/{task_id}/pending` | Get pending user interaction |
| POST | `/interactions/{id}/respond` | Respond to interaction |

## Technology Stack

| Component | Technology |
|-----------|------------|
| Backend | FastAPI, Python 3.11+ |
| Frontend | Streamlit |
| AI Agents | AutoGen 0.4+, OpenAI GPT-4o-mini |
| Database | SQLite (async SQLAlchemy) |
| Scheduling | APScheduler with SQLAlchemy job store |
| Authentication | JWT, Argon2id |
| Real-time | WebSockets |
| Web Search | DuckDuckGo (no API key needed) |
| Browser Automation | Playwright |
| Desktop Automation | PyAutoGUI |
| Excel Editing | openpyxl |
| Email | aiosmtplib |

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
> **Note**: Desktop automation tools only work when running locally (not on cloud deployment).

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
| `SMTP_HOST` | SMTP server for email tool | No |
| `SMTP_PORT` | SMTP port (default: 587) | No |
| `SMTP_USERNAME` | SMTP username | No |
| `SMTP_PASSWORD` | SMTP password | No |
| `INSTAGRAM_ACCESS_TOKEN` | Instagram Graph API token | No |
| `INSTAGRAM_BUSINESS_ACCOUNT_ID` | Instagram business account ID | No |
| `TWITTER_API_KEY` | Twitter API key | No |
| `TWITTER_API_SECRET` | Twitter API secret | No |
| `TWITTER_ACCESS_TOKEN` | Twitter access token | No |
| `TWITTER_ACCESS_TOKEN_SECRET` | Twitter access token secret | No |
| `LINKEDIN_ACCESS_TOKEN` | LinkedIn access token | No |
| `LINKEDIN_PERSON_ID` | LinkedIn person ID | No |
| `FACEBOOK_ACCESS_TOKEN` | Facebook page access token | No |
| `FACEBOOK_PAGE_ID` | Facebook page ID | No |

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
- [DuckDuckGo](https://duckduckgo.com/) - Privacy-first search engine
- [Playwright](https://playwright.dev/) - Browser automation
- [PyAutoGUI](https://pyautogui.readthedocs.io/) - Desktop automation

---

**Made with by [Hemalathajagan](https://github.com/Hemalathajagan)**
