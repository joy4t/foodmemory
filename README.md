# FoodMemory 🍕🧠

An AI-powered food ordering copilot that remembers what you loved (and what you didn't).

Built on [Swiggy's MCP Food Server](https://mcp.swiggy.com/builders/) with an intelligence layer that captures your ratings, tracks reorder patterns, and gives you contextual recommendations when you browse menus.

## What It Does

- **Search restaurants & menus** through a conversational agent
- **Order food** via Swiggy's MCP APIs
- **Rate dishes** after each order (1-5 stars + notes)
- **Get smart recommendations** based on your history ("You rated this 4/5 last time, said it was too spicy")
- **Track implicit signals** like reorder frequency and skipped items

## Tech Stack

- **Backend:** Python 3.11 + FastAPI
- **LLM:** Groq API (Llama 3.3 70B)
- **Database:** SQLite
- **Frontend:** Vanilla HTML/JS/CSS
- **MCP Integration:** Swiggy Food Server (mocked for demo)

## Quick Start

```bash
# Clone
git clone https://github.com/joy4t/foodmemory.git
cd foodmemory

# Create virtual environment
python -m venv venv
source venv/bin/activate        # Linux/Mac
venv\Scripts\activate           # Windows

# Install dependencies
pip install -r requirements.txt

# Set up environment
cp .env.example .env
# Edit .env with your GROQ_API_KEY

# Run
uvicorn backend.main:app --reload
```

## Project Structure

```
foodmemory/
├── backend/
│   ├── main.py              # FastAPI entry point
│   ├── config.py            # Settings & env vars
│   ├── database.py          # SQLite schema & connection
│   ├── agent/               # AI orchestrator + memory
│   ├── mcp/                 # Swiggy MCP client + mocks
│   ├── routes/              # API endpoints
│   └── models/              # Pydantic schemas
├── frontend/                # Chat UI
└── data/                    # SQLite database
```

## Status

🔨 **Phase 1-2:** Scaffold + database — *in progress*

---

Built by [@joy4t](https://github.com/joy4t) | Sokka Project
