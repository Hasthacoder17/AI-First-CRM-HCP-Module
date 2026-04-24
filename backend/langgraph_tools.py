from langchain_core.tools import tool
from database import SessionLocal
import crud
import schemas
from datetime import datetime
from typing import Optional
import json

@tool
def log_interaction(hcp_id: int, date_time: str, interaction_type: str, topics_discussed: Optional[str] = None,
                     hcp_sentiment: str = "neutral", follow_up_actions: Optional[list] = None,
                     attendees: Optional[list] = None, materials: Optional[list] = None) -> str:
    """Log a new interaction with an HCP. Use this when the user describes a meeting or interaction with a healthcare professional."""
    db = SessionLocal()
    try:
        interaction_data = schemas.InteractionCreate(
            hcp_id=hcp_id,
            date_time=datetime.fromisoformat(date_time.replace("Z", "+00:00")),
            interaction_type=interaction_type,
            topics_discussed=topics_discussed,
            hcp_sentiment=hcp_sentiment,
            follow_up_actions=follow_up_actions or [],
            attendees=[schemas.AttendeeCreate(**a) for a in (attendees or [])],
            materials=[schemas.MaterialSharedCreate(**m) for m in (materials or [])]
        )
        result = crud.create_interaction(db, interaction_data)
        # Return structured JSON for UI population
        return json.dumps({
            "action": "log_interaction",
            "status": "success",
            "interaction": {
                "id": result.id,
                "hcp_id": result.hcp_id,
                "date_time": result.date_time.isoformat() if result.date_time else None,
                "interaction_type": result.interaction_type,
                "topics_discussed": result.topics_discussed,
                "hcp_sentiment": result.hcp_sentiment,
                "follow_up_actions": result.follow_up_actions or [],
                "attendees": [{"name": a.name, "role": a.role} for a in result.attendees],
                "materials": [{"material_name": m.material_name, "quantity": m.quantity, "material_type": m.material_type} for m in result.materials]
            }
        })
    except Exception as e:
        return json.dumps({"action": "log_interaction", "status": "error", "message": str(e)})
    finally:
        db.close()


@tool
def edit_interaction(interaction_id: int, date_time: Optional[str] = None, interaction_type: Optional[str] = None,
                     topics_discussed: Optional[str] = None, hcp_sentiment: Optional[str] = None,
                     follow_up_actions: Optional[list] = None) -> str:
    """Edit an existing interaction by ID. Use this when the user wants to update or correct a previously logged interaction."""
    db = SessionLocal()
    try:
        update_data = {}
        if date_time:
            update_data["date_time"] = datetime.fromisoformat(date_time.replace("Z", "+00:00"))
        if interaction_type:
            update_data["interaction_type"] = interaction_type
        if topics_discussed is not None:
            update_data["topics_discussed"] = topics_discussed
        if hcp_sentiment:
            update_data["hcp_sentiment"] = hcp_sentiment
        if follow_up_actions is not None:
            update_data["follow_up_actions"] = follow_up_actions

        interaction_update = schemas.InteractionUpdate(**update_data)
        result = crud.update_interaction(db, interaction_id, interaction_update)
        if result:
            return json.dumps({
                "action": "edit_interaction",
                "status": "success",
                "interaction": {
                    "id": result.id,
                    "hcp_id": result.hcp_id,
                    "date_time": result.date_time.isoformat() if result.date_time else None,
                    "interaction_type": result.interaction_type,
                    "topics_discussed": result.topics_discussed,
                    "hcp_sentiment": result.hcp_sentiment,
                    "follow_up_actions": result.follow_up_actions or [],
                    "attendees": [{"name": a.name, "role": a.role} for a in result.attendees],
                    "materials": [{"material_name": m.material_name, "quantity": m.quantity, "material_type": m.material_type} for m in result.materials]
                }
            })
        return json.dumps({"action": "edit_interaction", "status": "error", "message": f"Interaction {interaction_id} not found"})
    except Exception as e:
        return json.dumps({"action": "edit_interaction", "status": "error", "message": str(e)})
    finally:
        db.close()


@tool
def search_hcp_history(hcp_id: int) -> str:
    """Search and retrieve past interactions for a specific HCP. Use this when the user asks about previous meetings or history with an HCP."""
    db = SessionLocal()
    try:
        interactions = crud.get_interactions_by_hcp(db, hcp_id, limit=50)
        return json.dumps({
            "action": "search_hcp_history",
            "status": "success",
            "hcp_id": hcp_id,
            "count": len(interactions),
            "interactions": [
                {
                    "id": i.id,
                    "date_time": i.date_time.isoformat() if i.date_time else None,
                    "interaction_type": i.interaction_type,
                    "topics_discussed": i.topics_discussed,
                    "hcp_sentiment": i.hcp_sentiment,
                    "follow_up_actions": i.follow_up_actions or []
                }
                for i in interactions
            ]
        })
    except Exception as e:
        return json.dumps({"action": "search_hcp_history", "status": "error", "message": str(e)})
    finally:
        db.close()


@tool
def schedule_followup(interaction_id: int, follow_up_actions: list) -> str:
    """Schedule a follow-up action for an interaction. Use this when the user mentions follow-up tasks, next steps, or action items from a meeting."""
    db = SessionLocal()
    try:
        interaction = crud.get_interaction(db, interaction_id)
        if not interaction:
            return json.dumps({"action": "schedule_followup", "status": "error", "message": f"Interaction {interaction_id} not found"})

        existing_actions = interaction.follow_up_actions or []
        updated_actions = existing_actions + follow_up_actions
        update_data = schemas.InteractionUpdate(follow_up_actions=updated_actions)
        result = crud.update_interaction(db, interaction_id, update_data)
        if result:
            return json.dumps({
                "action": "schedule_followup",
                "status": "success",
                "interaction_id": interaction_id,
                "follow_up_actions": updated_actions
            })
        return json.dumps({"action": "schedule_followup", "status": "error", "message": f"Failed to update interaction {interaction_id}"})
    except Exception as e:
        return json.dumps({"action": "schedule_followup", "status": "error", "message": str(e)})
    finally:
        db.close()


@tool
def log_sample_distribution(interaction_id: int, material_name: str, quantity: int = 1, material_type: Optional[str] = None) -> str:
    """Log samples or materials distributed to an HCP during an interaction. Use this when the user mentions giving samples, materials, or promotional items to an HCP."""
    db = SessionLocal()
    try:
        interaction = crud.get_interaction(db, interaction_id)
        if not interaction:
            return json.dumps({"action": "log_sample_distribution", "status": "error", "message": f"Interaction {interaction_id} not found"})

        material = models.MaterialShared(
            interaction_id=interaction_id,
            material_name=material_name,
            quantity=quantity,
            material_type=material_type
        )
        db.add(material)
        db.commit()
        return json.dumps({
            "action": "log_sample_distribution",
            "status": "success",
            "interaction_id": interaction_id,
            "material": {"material_name": material_name, "quantity": quantity, "material_type": material_type}
        })
    except Exception as e:
        return json.dumps({"action": "log_sample_distribution", "status": "error", "message": str(e)})
    finally:
        db.close()
