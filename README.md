# AI-First CRM HCP Module – LogInteractionScreen

Enterprise-grade pharmaceutical CRM system for field representatives to log Healthcare Professional (HCP) interactions using a dual-input approach: structured forms and conversational AI.

## Tech Stack

- **Frontend**: React (Vite) + Redux Toolkit + Tailwind CSS + Google Inter Font
- **Backend**: Python + FastAPI + SQLAlchemy + PostgreSQL
- **AI**: LangGraph + Groq API (`gemma2-9b-it`)
- **State Management**: Redux (single source of truth)

## Features

- **Split-Screen UI**: Left pane for structured form input, right pane for AI conversational interface
- **Real-Time Sync**: AI chat updates the form via Redux in real-time
- **5 LangGraph Tools**:
  1. `log_interaction` - Log new HCP interactions
  2. `edit_interaction` - Update existing interactions
  3. `search_hcp_history` - Retrieve past interaction history
  4. `schedule_followup` - Create follow-up tasks
  5. `log_sample_distribution` - Track samples/materials distributed

## Prerequisites

- Python 3.8+
- Node.js 18+
- PostgreSQL database
- Groq API key

## Installation

### Backend Setup

```bash
cd backend
pip install -r requirements.txt
```

Create `.env` file:
```env
GROQ_API_KEY=your_groq_api_key_here
DATABASE_URL=postgresql://postgres:postgres@localhost:5432/crm_hcp
```

### Frontend Setup

```bash
cd frontend
npm install
```

## Running the Application

### Start Backend (Terminal 1)
```bash
cd backend
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```
Visit `http://localhost:8000/docs` for Swagger API documentation.

### Start Frontend (Terminal 2)
```bash
cd frontend
npm run dev
```
Visit `http://localhost:5173` for the application.

## Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `GROQ_API_KEY` | Groq API key for AI agent | Required |
| `DATABASE_URL` | PostgreSQL connection string | `postgresql://postgres:postgres@localhost:5432/crm_hcp` |

## API Endpoints

### HCP Endpoints
- `POST /api/hcps` - Create new HCP
- `GET /api/hcps` - List all HCPs

### Interaction Endpoints
- `POST /api/interactions` - Create new interaction (with attendees and materials)
- `GET /api/interactions` - List all interactions
- `PATCH /api/interactions/{id}` - Update existing interaction
- `GET /api/interactions/hcp/{id}` - Get HCP interaction history

### AI Endpoints
- `POST /api/ai/chat` - Send message to AI agent
- `GET /api/ai/tools` - List available AI tools

## Database Schema

### HCP Table
- id (PK), name, specialty, email, phone, address, created_at, updated_at

### Interaction Table
- id (PK), hcp_id (FK), date_time, interaction_type, topics_discussed, hcp_sentiment, follow_up_actions, created_at, updated_at

### Attendee Table
- id (PK), interaction_id (FK), name, role, created_at

### MaterialShared Table
- id (PK), interaction_id (FK), material_name, quantity, material_type, created_at

## Interaction Types & Sentiment

**Interaction Types**: `in_person`, `virtual`, `phone`

**Sentiment Values**: `positive`, `neutral`, `negative`

## Project Structure

```
AI-First CRM HCP Module – LogInteractionScreen/
├── backend/
│   ├── models.py           # SQLAlchemy ORM models
│   ├── schemas.py          # Pydantic validation schemas
│   ├── database.py         # DB connection + session management
│   ├── crud.py             # Database CRUD operations
│   ├── main.py             # FastAPI application + routes
│   ├── config.py           # Environment configuration
│   ├── langgraph_tools.py  # 5 LangChain tools
│   ├── langgraph_agent.py  # LangGraph ReAct agent
│   └── requirements.txt    # Python dependencies
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   │   ├── InteractionForm.jsx  # Left pane form
│   │   │   └── AIChat.jsx          # Right pane chat
│   │   ├── store/
│   │   │   ├── interactionSlice.js  # Redux slice
│   │   │   └── store.js            # Redux store
│   │   ├── App.jsx                 # Split-screen layout
│   │   ├── main.jsx                # Entry point
│   │   └── index.css               # Tailwind + Inter font
│   ├── index.html                   # Google Inter font link
│   └── vite.config.js              # Vite + Tailwind config
├── .gitignore
├── .env.example
└── README.md
```

## Usage Flow

1. **Form Input**: Field rep fills out structured form (left pane)
2. **AI Chat**: Describe interaction conversationally (right pane)
3. **AI Processing**: LangGraph agent extracts data using 5 tools
4. **Real-Time Update**: Redux updates form fields automatically
5. **Save**: Click "Save Interaction" to persist to PostgreSQL

## LangGraph Agent Tools

| Tool | Purpose | API Call |
|------|---------|----------|
| `log_interaction` | Create new interaction | `POST /api/interactions` |
| `edit_interaction` | Update interaction | `PATCH /api/interactions/{id}` |
| `search_hcp_history` | Get HCP history | `GET /api/interactions/hcp/{id}` |
| `schedule_followup` | Add follow-up actions | Updates `follow_up_actions` |
| `log_sample_distribution` | Track samples | Creates material record |

## License

MIT

## Author

Built with Claude Code - AI-First Enterprise CRM Solution
