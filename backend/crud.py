from sqlalchemy.orm import Session, joinedload
from typing import List, Optional

import models
import schemas


def create_hcp(db: Session, hcp: schemas.HCPCreate) -> models.HCP:
    db_hcp = models.HCP(**hcp.dict())
    db.add(db_hcp)
    db.commit()
    db.refresh(db_hcp)
    return db_hcp


def get_hcps(db: Session, skip: int = 0, limit: int = 100) -> List[models.HCP]:
    return db.query(models.HCP).offset(skip).limit(limit).all()


def get_hcp(db: Session, hcp_id: int) -> Optional[models.HCP]:
    return db.query(models.HCP).filter(models.HCP.id == hcp_id).first()


def create_interaction(db: Session, interaction: schemas.InteractionCreate) -> models.Interaction:
    interaction_data = interaction.dict(exclude={"attendees", "materials"})
    db_interaction = models.Interaction(**interaction_data)
    db.add(db_interaction)
    db.commit()
    db.refresh(db_interaction)

    for attendee in interaction.attendees:
        db_attendee = models.Attendee(**attendee.dict(), interaction_id=db_interaction.id)
        db.add(db_attendee)

    for material in interaction.materials:
        db_material = models.MaterialShared(**material.dict(), interaction_id=db_interaction.id)
        db.add(db_material)

    db.commit()
    db.refresh(db_interaction)
    return db_interaction


def get_interactions(db: Session, skip: int = 0, limit: int = 100) -> List[models.Interaction]:
    return (
        db.query(models.Interaction)
        .options(joinedload(models.Interaction.attendees), joinedload(models.Interaction.materials))
        .offset(skip)
        .limit(limit)
        .all()
    )


def get_interaction(db: Session, interaction_id: int) -> Optional[models.Interaction]:
    return (
        db.query(models.Interaction)
        .options(joinedload(models.Interaction.attendees), joinedload(models.Interaction.materials))
        .filter(models.Interaction.id == interaction_id)
        .first()
    )


def update_interaction(
    db: Session, interaction_id: int, interaction: schemas.InteractionUpdate
) -> Optional[models.Interaction]:
    db_interaction = get_interaction(db, interaction_id)
    if not db_interaction:
        return None

    update_data = interaction.dict(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_interaction, key, value)

    db.commit()
    db.refresh(db_interaction)
    return db_interaction


def get_interactions_by_hcp(
    db: Session, hcp_id: int, skip: int = 0, limit: int = 100
) -> List[models.Interaction]:
    return (
        db.query(models.Interaction)
        .options(joinedload(models.Interaction.attendees), joinedload(models.Interaction.materials))
        .filter(models.Interaction.hcp_id == hcp_id)
        .offset(skip)
        .limit(limit)
        .all()
    )
