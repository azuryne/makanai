# MakanAI 🍽️

> AI-powered mindful eating journal and nutrition chatbot built with FastAPI, Ollama, and React.

MakanAI helps you track your meals using natural language, get real nutritional data,
and receive personalized weekly insights — all powered by a local AI model running on your machine.

---

## Features

- 📝 **Natural language meal logging** — just type "nasi lemak and teh tarik for lunch"
- 🔍 **Real nutrition data** — fetched from USDA FoodData and Open Food Facts
- 📊 **Weekly insights** — AI-generated summary of your eating patterns
- 💬 **Nutrition chatbot** — ask questions about your meals and eating habits
- 🔒 **JWT authentication** — secure register and login system
- 🤖 **Fully local AI** — runs on Ollama, no OpenAI API key needed

---

## Tech Stack

### Backend
| Tool | Purpose |
|---|---|
| FastAPI | REST API framework |
| SQLAlchemy v2 | Async ORM |
| PostgreSQL | Database |
| Alembic | Database migrations |
| Ollama (phi3) | Local AI model |
| USDA FoodData API | Primary nutrition data |
| Open Food Facts API | Fallback nutrition data |
| python-jose | JWT token handling |
| passlib + bcrypt | Password hashing |

### Frontend
| Tool | Purpose |
|---|---|
| React | UI framework |
| Vite | Build tool |
| Axios | HTTP client |

---

## Project Structure
makanai/
├── backend/
│   ├── app/
│   │   ├── main.py                  # FastAPI entry point
│   │   ├── config.py                # environment settings
│   │   ├── api/
│   │   │   ├── deps.py              # JWT auth dependency
│   │   │   └── routes/
│   │   │       ├── auth.py          # register, login, /me
│   │   │       ├── meals.py         # meal logging + history
│   │   │       ├── insights.py      # weekly insights
│   │   │       ├── chat.py          # chatbot
│   │   │       └── health.py        # health check
│   │   ├── agents/
│   │   │   ├── orchestrator.py      # coordinates all agents
│   │   │   ├── parser_agent.py      # extracts food from text
│   │   │   ├── lookup_agent.py      # fetches nutrition data
│   │   │   ├── insight_agent.py     # weekly pattern summary
│   │   │   └── chat_agent.py        # chatbot logic
│   │   ├── services/
│   │   │   ├── ollama.py            # Ollama API wrapper
│   │   │   ├── usda.py              # USDA API wrapper
│   │   │   ├── openfoodfacts.py     # Open Food Facts wrapper
│   │   │   └── context_builder.py  # builds chat prompt context
│   │   ├── models/
│   │   │   ├── user.py              # users table
│   │   │   └── meal.py              # meals + chat_messages tables
│   │   ├── schemas/
│   │   │   ├── auth.py              # auth request/response schemas
│   │   │   ├── meal.py              # meal request/response schemas
│   │   │   ├── insight.py           # insight response schema
│   │   │   └── chat.py              # chat request/response schemas
│   │   ├── constants/
│   │   │   └── prompts.py           # all AI prompt templates
│   │   └── db/
│   │       └── session.py           # async DB session + Base
│   ├── alembic/                     # database migrations
│   ├── .env.example                 # environment variables template
│   ├── requirements.txt
│   └── alembic.ini
│
└── frontend/
├── src/
│   ├── api/
│   │   └── client.js            # axios base config
│   ├── pages/
│   │   ├── Login.jsx
│   │   ├── Register.jsx
│   │   ├── Log.jsx              # meal logging page
│   │   ├── Insights.jsx         # weekly insights page
│   │   └── Chat.jsx             # chatbot page
│   ├── components/
│   │   ├── Navbar.jsx
│   │   ├── MealForm.jsx
│   │   ├── NutritionCard.jsx
│   │   ├── InsightChart.jsx
│   │   └── ChatWindow.jsx
│   └── hooks/
│       ├── useAuth.js
│       ├── useMeals.js
│       └── useChat.js
├── package.json
└── vite.config.js

---

## Getting Started

### Prerequisites

- Python 3.11+
- Node.js 18+
- PostgreSQL 15+
- [Ollama](https://ollama.com) installed locally

---

### 1. Clone the repository

```bash
git clone https://github.com/yourusername/makanai.git
cd makanai
```

---

### 2. Setup Ollama

```bash
# Install Ollama from https://ollama.com
# Then pull the phi3 model
ollama pull phi3

# Start Ollama
ollama serve
```

---

### 3. Setup the database

```bash
# Create PostgreSQL database
psql -U postgres
CREATE DATABASE makanai;
\q
```

---

### 4. Setup the backend

```bash
cd backend

# Create virtual environment
python -m venv venv

# Activate virtual environment
# Windows:
venv\Scripts\activate
# Mac/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Setup environment variables
cp .env.example .env
# Edit .env with your values

# Run database migrations
alembic upgrade head

# Start the backend server
uvicorn app.main:app --reload
```

Backend runs at `http://localhost:8000`
API docs available at `http://localhost:8000/docs`

---

### 5. Setup the frontend

```bash
cd frontend

# Install dependencies
npm install

# Start the frontend dev server
npm run dev
```

Frontend runs at `http://localhost:5173`

---