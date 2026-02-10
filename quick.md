# Quick Guide - Multi-Agent Task Assistant

## What is This?

An AI-powered task automation platform that uses **3 coordinated AI agents** to deliver higher-quality outputs for complex objectives — by adding structured planning, execution, and review stages.

### The 3 Agents

| Step | Agent | Role |
|------|-------|------|
| 1 | **Planner** | Breaks your goal into subtasks, sets priorities & dependencies |
| 2 | **Executor** | Works through each subtask systematically |
| 3 | **Reviewer** | Checks quality, finds gaps, approves or sends back for revision |

### Target Users

Knowledge workers, researchers, content creators, and analysts who want to automate multi-step projects.

---

## How is This Different from ChatGPT?

**This is NOT a ChatGPT replica.** ChatGPT is a general-purpose conversational AI. This project is a specialized task automation tool that does one thing differently:

**Take an objective → Plan it → Execute it → Review it → Deliver a validated output.**

| Aspect | ChatGPT | This Project |
|--------|---------|-------------|
| Architecture | One AI, single response | Three specialized AIs collaborating |
| Quality Control | No self-review | Reviewer agent validates before delivery |
| Workflow | One-shot generation | Structured Plan → Execute → Review pipeline |
| Iteration | You manually re-prompt | Automatic revision cycle |
| Persistence | Chat logs only | Database — re-run, continue, view history |
| Real-time | Not applicable | Watch agents work live via WebSockets |

### When This Project Wins

- Complex multi-step tasks (research plans, strategies, reports)
- Tasks needing quality assurance
- Repeatable workflows with stored history

### When ChatGPT Wins

- Simple questions and quick answers
- Casual conversation
- General-purpose tasks

### The Honest Take

This project uses the **same underlying model** (GPT-4o-mini). The raw intelligence is identical. The advantage comes purely from the **workflow** — multiple passes, specialized roles, and self-review.

> **Analogy:** ChatGPT = one person doing everything alone. This project = a team of 3 specialists (project manager, worker, quality reviewer) collaborating on your task.

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
4. Watch the 3 agents collaborate in real-time
5. View the structured plan, execution, and review results

---

## Tech Stack

| Layer | Technology |
|-------|-----------|
| Backend | FastAPI + SQLite + SQLAlchemy |
| Frontend | Streamlit |
| AI Agents | AutoGen 0.4+ + OpenAI GPT-4o-mini |
| Auth | JWT + Argon2id hashing |
| Real-time | WebSockets |
| Deployment | Render (backend) + Streamlit Cloud (frontend) |

---

## Live Demo

- **Frontend**: Deployed on Streamlit Cloud
- **Backend**: Deployed on Render (free tier — first request may take 30-60s to wake up)

---

**Made by [Hemalathajagan](https://github.com/Hemalathajagan)**
