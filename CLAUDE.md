# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

AI-First CRM HCP Module – LogInteractionScreen

A pharmaceutical CRM system for field reps to log Healthcare Professional (HCP) interactions. Features a dual-input pattern: structured forms and conversational AI both feed into a single Redux store, keeping the split-screen UI (form left, AI chat right) in real-time sync.

### High-Level Architecture

**Two-tier application** with a FastAPI backend and React/Vite frontend:

- **Backend** (`backend/`): FastAPI REST API + LangGraph AI agent. PostgreSQL/SQLAlchemy ORM. Exposes both traditional CRUD endpoints and an AI chat endpoint that delegates to a ReAct agent.
- **Frontend** (`frontend/`): React 19 + Vite + Tailwind CSS 4 + Redux Toolkit. Split-screen layout — `InteractionForm` (left) and `AIChat` (right) share a single Redux store (`interactionSlice`).

**Key Integration Point**: The LangGraph agent in the backend calls the same CRUD functions that the REST API uses. The AI chat endpoint (`/api/ai/chat`) returns structured JSON tool responses that the frontend parses to update Redux state, keeping the form in sync.

## Commands

### Backend Development

```bash
cd backend

# Install dependencies
pip install -r requirements.txt

# Run dev server (requires .env with GROQ_API_KEY and DATABASE_URL)
uvicorn main:app --reload --host 0.0.0.0 --port 8000

# Swagger docs
# http://localhost:8000/docs
```

**Environment variables** (`.env` in backend/):
- `GROQ_API_KEY` — Required for LangGraph agent (Groq API)
- `DATABASE_URL` — PostgreSQL connection string (e.g., `postgresql://postgres:postgres@localhost:5432/crm_hcp`)

### Frontend Development

```bash
cd frontend

# Install dependencies
npm install

# Dev server (http://localhost:5173)
# The Vite dev server proxies /api/* requests to the backend at localhost:8000
npm run dev

# Production build
npm run build

# Lint check
npm run lint
```

**Note**: No test framework is configured. API requests from the frontend to `/api/*` are proxied through the Vite dev server to `localhost:8000` during development (see `vite.config.js`). This avoids CORS issues and eliminates the need to configure backend CORS for dev origins.

### Running Both Simultaneously

```bash
# Terminal 1: Backend
cd backend && uvicorn main:app --reload --host 0.0.0.0 --port 8000

# Terminal 2: Frontend
cd frontend && npm run dev
```

## Data Model (Big Picture)

### Core Entities

- **HCP** (`hcps` table) — Healthcare Professional. Basic contact info.
- **Interaction** (`interactions` table) — A meeting/communication with an HCP. Has type (in_person/virtual/phone), sentiment, topics, timestamps.
- **Attendee** (`attendees` table) — People who attended an interaction (1-to-many from Interaction).
- **MaterialShared** (`materials_shared` table) — Samples/promotional items given during an interaction (1-to-many from Interaction).

### Relationships

```
HCP (1) ←→ (many) Interaction (1) ←→ (many) Attendee
                              (1) ←→ (many) MaterialShared
```

### Schema ↔ Model Sync

- `models.py` — SQLAlchemy ORM models (database layer)
- `schemas.py` — Pydantic models (request/response validation)
- They mirror each other closely. The `InteractionCreate` schema includes nested `attendees` and `materials` arrays which are flattened when persisting via `crud.py`.

## Backend Deep Dive

### Layered Architecture

```
main.py                    — FastAPI app, routes, CORS
  ↓
schemas.py                 — Pydantic request/response models
  ↓
crud.py                    — Database operations (SQLAlchemy ORM)
  ↓
models.py                  — SQLAlchemy declarative models
  ↓
database.py                — Engine, SessionLocal, Base
```

### API Endpoints

- `POST /api/hcps` — Create HCP
- `GET /api/hcps` — List HCPs (paginated)
- `POST /api/interactions` — Create interaction (with nested attendees/materials)
- `GET /api/interactions` — List interactions (paginated, joined)
- `PATCH /api/interactions/{id}` — Update interaction
- `GET /api/interactions/hcp/{hcp_id}` — Get interactions for specific HCP

### AI Agent Layer

```
langgraph_agent.py         — ReAct agent setup (Groq LLM + tools)
  ↓
langgraph_tools.py         — 5 tools: log_interaction, edit_interaction,
                            search_hcp_history, schedule_followup,
                            log_sample_distribution
```

**Important**: Each tool in `langgraph_tools.py` creates its own `SessionLocal()` database session independently. They **do not** use the FastAPI dependency injection (`get_db`). They return JSON strings that the agent includes in its response.

**Tool → CRUD mapping**:
- `log_interaction` → `crud.create_interaction`
- `edit_interaction` → `crud.update_interaction`
- `search_hcp_history` → `crud.get_interactions_by_hcp`
- `schedule_followup` → `crud.get_interaction` + `crud.update_interaction`
- `log_sample_distribution` → Creates `MaterialShared` directly

## Frontend Deep Dive

### Component Tree

```
App.jsx
├── InteractionForm (left pane)  — Read-only form, displays interaction state
└── AIChat (right pane)          — Chat interface, sends to /api/ai/chat
```

### State Management

**Single Redux store** (`store/store.js`) with one slice:

- `interactionSlice` (`store/interactionSlice.js`) — Holds the current interaction being built:
  - `hcpId`, `hcpName`, `dateTime`, `interactionType`, `topicsDiscussed`, `sentiment`
  - Arrays: `attendees`, `materials`, `followUpActions`

**Data Flow**:

1. User types message in AIChat
2. POST `/api/ai/chat` → LangGraph agent runs
3. Agent uses tools → Tool returns JSON `{action, status, interaction: {...}}`
4. Frontend `parseToolResponse()` extracts `interaction` object
5. `dispatch(setInteractionData(...))` updates Redux
6. InteractionForm re-renders with new values (all inputs are `readOnly`/`disabled`)

### Key Implementation Details

- **No local form state** — Everything comes from Redux (`useSelector(state => state.interaction)`)
- **Form is read-only** — All fields are `readOnly` or `disabled`. The "Reset Form" button dispatches `resetForm()` which restores `initialState`
- **AI controls form** — The only way to populate the form is via the AI agent's tool responses
- **API calls via Vite proxy** — The frontend uses relative `/api/*` URLs proxied by Vite dev server to the backend at `localhost:8000`, avoiding CORS issues in development.

## Critical Patterns & Notes

### Dual-Input Sync Pattern

Both UI panes conceptually modify the same data:
- **Left** (form): *Displays* the current interaction state (read-only)
- **Right** (chat): *Updates* the state via AI tool responses

The Redux store is the single source of truth.

### LangGraph Tool Response Format

All tools return a JSON string (not a dict) with this structure:
```json
{
  "action": "log_interaction|edit_interaction|...",
  "status": "success|error",
  "interaction": { ... }  // or other relevant data
}
```

When the string is valid JSON and has `action` + `interaction`, the frontend extracts `interaction` and dispatches it to Redux.

### Database Sessions

- **REST API routes** use `get_db()` dependency (yields session, auto-closes)
- **LangGraph tools** create `SessionLocal()` manually and `db.close()` in `finally` block
- **Both** use the same `engine` from `database.py`

### CORS Configuration

Currently configured for development: allows `http://localhost:5173` and `http://127.0.0.1:5173` as origins with credentials enabled. **Must be locked down before production** (see `main.py` lines 18-24).

During development, the Vite dev server proxies `/api/*` requests to the backend, avoiding CORS entirely for the frontend-Backend communication.

### No Auth Layer

All endpoints are unauthenticated and open. This is fine for local dev but needs middleware (API keys/JWT/auth) before any production deployment.

## Development Workflow Tips

### Adding a New Field to Interaction

1. Add column to `models.Interaction` (SQLAlchemy)
2. Add field to `schemas.InteractionBase` / `InteractionCreate` / `InteractionResponse`
3. Update `crud.create_interaction` / `update_interaction` to handle the field
4. Add field to frontend `interactionSlice.js` `initialState`
5. Add field mapping in `setInteractionData` reducer
6. Add display component in `InteractionForm.jsx`
7. Tool responses from `langgraph_tools.py` should include the new field if relevant

### Modifying the AI Agent

- Change model: Edit `config.py` (`GROQ_MODEL`)
- Add tool: Create function in `langgraph_tools.py` with `@tool` decorator, add to `tools` list in `langgraph_agent.py`
- Tool functions should return JSON strings for frontend parsing

### Testing the API Directly

```bash
# Create HCP
curl -X POST http://localhost:8000/api/hcps \
  -H "Content-Type: application/json" \
  -d '{"name": "Dr. Smith", "specialty": "Cardiology"}'

# Create interaction
curl -X POST http://localhost:8000/api/interactions \
  -H "Content-Type: application/json" \
  -d '{"hcp_id": 1, "date_time": "2026-04-25T10:00:00", "interaction_type": "in_person", "hcp_sentiment": "positive", "topics_discussed": "New drug launch"}'
```

## Troubleshooting

**Frontend can't reach backend ("Failed to fetch")**:
- Verify backend is running: `curl http://localhost:8000/docs`
- During dev, frontend uses Vite proxy — ensure both dev servers are running
- If calling backend directly (not via proxy), CORS must allow the frontend origin (see `main.py`)

**Database connection errors**: Ensure PostgreSQL is running and `DATABASE_URL` in `.env` is correct. Tables are auto-created on first run via `Base.metadata.create_all`.

**LangGraph tool errors**: Check Groq API key is set in `.env`. Each tool uses its own DB session — ensure PostgreSQL allows multiple concurrent connections.

**Redux state not updating**: Open browser dev tools → Redux devtools to inspect `interaction` slice state changes.

## Production Considerations (Not Yet Implemented)

- [ ] Authentication/Authorization middleware
- [ ] Lock down CORS origins
- [ ] Use connection pooling for database
- [ ] Add comprehensive error handling and logging
- [ ] Input validation beyond Pydantic schemas
- [ ] Test suite (frontend + backend)
- [ ] CI/CD pipeline
- [ ] Docker containerization
- [ ] Rate limiting on API endpoints
- [ ] Secure session/database credential management