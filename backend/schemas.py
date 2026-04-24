from pydantic import BaseModel
from datetime import datetime
from typing import Optional, List
from enum import Enum as EnumType

class InteractionType(str, EnumType):
    in_person = "in_person"
    virtual = "virtual"
    phone = "phone"

class SentimentType(str, EnumType):
    positive = "positive"
    neutral = "neutral"
    negative = "negative"

# HCP Schemas
class HCPBase(BaseModel):
    name: str
    specialty: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    address: Optional[str] = None

class HCPCreate(HCPBase):
    pass

class HCPResponse(HCPBase):
    id: int
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True

# Attendee Schemas
class AttendeeBase(BaseModel):
    name: str
    role: Optional[str] = None

class AttendeeCreate(AttendeeBase):
    pass

class AttendeeResponse(AttendeeBase):
    id: int
    interaction_id: int
    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True

# Material Shared Schemas
class MaterialSharedBase(BaseModel):
    material_name: str
    quantity: int = 1
    material_type: Optional[str] = None

class MaterialSharedCreate(MaterialSharedBase):
    pass

class MaterialSharedResponse(MaterialSharedBase):
    id: int
    interaction_id: int
    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True

# Interaction Schemas
class InteractionBase(BaseModel):
    hcp_id: int
    date_time: datetime
    interaction_type: InteractionType
    topics_discussed: Optional[str] = None
    hcp_sentiment: SentimentType
    follow_up_actions: Optional[list] = None

class InteractionCreate(InteractionBase):
    attendees: Optional[List[AttendeeCreate]] = []
    materials: Optional[List[MaterialSharedCreate]] = []

class InteractionUpdate(BaseModel):
    date_time: Optional[datetime] = None
    interaction_type: Optional[InteractionType] = None
    topics_discussed: Optional[str] = None
    hcp_sentiment: Optional[SentimentType] = None
    follow_up_actions: Optional[list] = None

class InteractionResponse(InteractionBase):
    id: int
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    attendees: List[AttendeeResponse] = []
    materials: List[MaterialSharedResponse] = []

    class Config:
        from_attributes = True
