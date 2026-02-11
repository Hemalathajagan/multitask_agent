# Quick Guide - Multi-Agent Task Assistant

## What is This?

An AI-powered task automation platform that uses **3 coordinated AI agents** + **27+ real-world tools** to plan, execute, and review any task you give it — with your approval at every step.

### The 3 Agents

| Step | Agent | Role |
|------|-------|------|
| 1 | **Planner** | Breaks your goal into subtasks, sets priorities & dependencies |
| 2 | **Executor** | Works through each subtask using real tools (search, email, desktop, files, social media) |
| 3 | **Reviewer** | Checks quality, finds gaps, approves or sends back for revision |

### What It Can Actually Do

| Capability | How |
|-----------|-----|
| Search the internet for current info | DuckDuckGo search + news (no API key needed) |
| Read any webpage | Fetches and extracts article content |
| Send emails | SMTP with user-provided details |
| Edit Excel files on your PC | openpyxl — opens, edits cells, saves, closes |
| Edit CSV files on your PC | Direct file editing, no DB records |
| Control desktop apps (WhatsApp, etc.) | PyAutoGUI — finds windows, clicks, types, screenshots |
| Automate browsers | Playwright — navigate, fill forms, click buttons |
| Post to social media | Instagram, Twitter/X, LinkedIn, Facebook APIs |
| Run Python code | Sandboxed execution with output capture |
| Schedule tasks for later | APScheduler — persistent, survives restarts |
| Upload files | Attach files from your desktop to tasks |

### Safety Features

- Every tool action requires your **approval before executing**
- Agent **stops and asks for help** when stuck (instead of guessing)
- Desktop screenshots **auto-delete after 5 minutes**
- Region screenshots capture **only the target app** (not full desktop)
- You can **cancel any task** at any time

---

## How is This Different from ChatGPT?

**This is NOT a ChatGPT replica.** ChatGPT generates text. This project **actually does things** — searches the web, sends emails, edits your files, controls your desktop apps.

| Aspect | ChatGPT | This Project |
|--------|---------|-------------|
| Architecture | One AI, single response | Three specialized AIs collaborating |
| Can search the web | No (without plugins) | Yes — DuckDuckGo search + news |
| Can send emails | No | Yes — SMTP |
| Can edit your files | No | Yes — Excel, CSV on your local machine |
| Can control your desktop | No | Yes — WhatsApp, browsers, any app |
| Can post to social media | No | Yes — Instagram, Twitter, LinkedIn, Facebook |
| Can schedule future tasks | No | Yes — persistent scheduling |
| Quality control | No self-review | Reviewer agent validates before delivery |
| User confirmation | N/A | Approve/deny every action |
| When stuck | Keeps generating | Stops and asks you for help |

### The Honest Take

This project uses the **same underlying model** (GPT-4o-mini). The raw intelligence is identical. The advantage comes from the **workflow** + **real tool execution**.

> **Analogy:** ChatGPT = one person answering questions at a desk. This project = a team of 3 specialists with access to your computer, email, browser, and apps — working on your task with your permission at every step.

---

## Quick Start

### 1. Clone & Install

```bash
git clone https://github.com/Hemalathajagan/multitask_agent.git
cd multitask_agent
pip install -r requirements.txt
```

### 2. Configure

```bash
cp .env.example .env
```

Edit `.env`:
```env
OPENAI_API_KEY=your-openai-api-key
SECRET_KEY=your-secret-key
```

Optional: Add SMTP, social media credentials (see `.env.example`).

### 3. Run

**Backend:**
```bash
python -m uvicorn app.main:app --reload
```

**Frontend (separate terminal):**
```bash
streamlit run streamlit_app/app.py
```

### 4. Use It

1. Open http://localhost:8501
2. Register an account
3. Create a task with any objective
4. Optionally schedule it for later or attach a file
5. Watch the 3 agents collaborate in real-time
6. Approve each tool action when prompted
7. If the agent gets stuck, provide guidance
8. View the structured plan, execution, and review results

---

## Example Tasks

| What You Say | What Happens |
|-------------|-------------|
| "Research latest news about AI" | Searches DuckDuckGo news, reads top articles, creates summary |
| "Send email to boss about the meeting" | Asks you for email details, shows preview, sends after approval |
| "Update cell B3 in C:/report.xlsx to 500" | Opens Excel file, updates cell, saves, closes |
| "Message John on WhatsApp: Meeting at 3pm" | Finds WhatsApp window, navigates to contact, types and sends |
| "Post 'Hello World' to Twitter in 2 hours" | Schedules task, runs at specified time, asks for tweet review |

---

## Tech Stack

| Layer | Technology |
|-------|-----------|
| Backend | FastAPI + SQLite + SQLAlchemy |
| Frontend | Streamlit |
| AI Agents | AutoGen 0.4+ + OpenAI GPT-4o-mini |
| Scheduling | APScheduler (persistent) |
| Auth | JWT + Argon2id hashing |
| Real-time | WebSockets |
| Web Search | DuckDuckGo (no API key) |
| Desktop | PyAutoGUI |
| Browser | Playwright |
| Excel | openpyxl |
| Email | aiosmtplib |
| Social Media | Instagram/Twitter/LinkedIn/Facebook APIs |

---

## Live Demo

- **Frontend**: Deployed on Streamlit Cloud
- **Backend**: Deployed on Render (free tier — first request may take 30-60s to wake up)
- **Note**: Desktop automation only works when running locally

---

**Made by [Hemalathajagan](https://github.com/Hemalathajagan)**
