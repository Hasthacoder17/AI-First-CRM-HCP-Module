from langchain_core.tools import tool
from database import SessionLocal
import crud
import schemas
from datetime import datetime
from typing import Optional

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
        return f"Interaction logged successfully with ID {result.id}"
    except Exception as e:
        return f"Error logging interaction: {str(e)}"
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
            return f"Interaction {interaction_id} updated successfully"
        return f"Interaction {interaction_id} not found"
    except Exception as e:
        return f"Error updating interaction: {str(e)}"
    finally:
        db.close()


@tool
def search_hcp_history(hcp_id: int) -> str:
    """Search and retrieve past interactions for a specific HCP. Use this when the user asks about previous meetings or history with an HCP."""
    db = SessionLocal()
    try:
        interactions = crud.get_interactions_by_hcp(db, hcp_id, limit=50)
        if not interactions:
            return f"No interactions found for HCP {hcp_id}"
        history = f"Found {len(interactions)} interaction(s) for HCP {hcp_id}:\n"
        for idx, interaction in enumerate(interactions, 1):
            history += f"{idx}. ID: {interaction.id}, Date: {interaction.date_time}, Type: {interaction.interaction_type}, Sentiment: {interaction.hcp_sentiment}\n"
            if interaction.topics_discussed:
                history += f"   Topics: {interaction.topics_discussed}\n"
        return history
    except Exception as e:
        return f"Error searching HCP history: {str(e)}"
    finally:
        db.close()


@tool
def schedule_followup(interaction_id: int, follow_up_actions: list) -> str:
    """Schedule a follow-up action for an interaction. Use this when the user mentions follow-up tasks, next steps, or action items from a meeting."""
    db = SessionLocal()
    try:
        interaction = crud.get_interaction(db, interaction_id)
        if not interaction:
            return f"Interaction {interaction_id} not found"

        existing_actions = interaction.follow_up_actions or []
        updated_actions = existing_actions + follow_up_actions
        update_data = schemas.InteractionUpdate(follow_up_actions=updated_actions)
        result = crud.update_interaction(db, interaction_id, update_data)
        if result:
            return f"Follow-up actions added to interaction {interaction_id}: {follow_up_actions}"
        return f"Failed to update interaction {interaction_id}"
    except Exception as e:
        return f"Error scheduling follow-up: {str(e)}"
    finally:
        db.close()


@tool
def log_sample_distribution(interaction_id: int, material_name: str, quantity: int = 1, material_type: Optional[str] = None) -> str:
    """Log samples or materials distributed to an HCP during an interaction. Use this when the user mentions giving samples, materials, or promotional items to an HCP."""
    db = SessionLocal()
    try:
        interaction = crud.get_interaction(db, interaction_id)
        if not interaction:
            return f"Interaction {interaction_id} not found"

        material = models.MaterialShared(
            interaction_id=interaction_id,
            material_name=material_name,
            quantity=quantity,
            material_type=material_type
        )
        db.add(material)
        db.commit()
        return f"Sample '{material_name}' (qty: {quantity}) logged to interaction {interaction_id}"
    except Exception as e:
        return f"Error logging sample distribution: {str(e)}"
    finally:
        db.close()
