from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from typing import List
from pydantic import BaseModel

import crud
import schemas
import models
from database import SessionLocal, engine, Base, get_db
import langgraph_agent

# Create database tables
Base.metadata.create_all(bind=engine)

app = FastAPI(title="AI-First CRM HCP Module API")

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.post("/api/hcps", response_model=schemas.HCPResponse)
def create_hcp(hcp: schemas.HCPCreate, db: Session = Depends(get_db)):
    return crud.create_hcp(db, hcp)


@app.get("/api/hcps", response_model=List[schemas.HCPResponse])
def read_hcps(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return crud.get_hcps(db, skip, limit)


@app.post("/api/interactions", response_model=schemas.InteractionResponse)
def create_interaction(interaction: schemas.InteractionCreate, db: Session = Depends(get_db)):
    return crud.create_interaction(db, interaction)


@app.get("/api/interactions", response_model=List[schemas.InteractionResponse])
def read_interactions(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return crud.get_interactions(db, skip, limit)


@app.patch("/api/interactions/{interaction_id}", response_model=schemas.InteractionResponse)
def update_interaction(
    interaction_id: int, interaction: schemas.InteractionUpdate, db: Session = Depends(get_db)
):
    db_interaction = crud.update_interaction(db, interaction_id, interaction)
    if not db_interaction:
        raise HTTPException(status_code=404, detail="Interaction not found")
    return db_interaction


@app.get("/api/interactions/hcp/{hcp_id}", response_model=List[schemas.InteractionResponse])
def read_hcp_interactions(
    hcp_id: int, skip: int = 0, limit: int = 100, db: Session = Depends(get_db)
):
    return crud.get_interactions_by_hcp(db, hcp_id, skip, limit)


# AI Chat request model
class ChatMessage(BaseModel):
    message: str
    interaction_id: int = None


@app.post("/api/ai/chat")
def ai_chat(chat: ChatMessage):
    response = langgraph_agent.invoke_agent(chat.message)
    return {"response": response}


@app.get("/api/ai/tools")
def list_tools():
    tool_names = [
        "log_interaction",
        "edit_interaction",
        "search_hcp_history",
        "schedule_followup",
        "log_sample_distribution",
    ]
    return {"tools": tool_names}
