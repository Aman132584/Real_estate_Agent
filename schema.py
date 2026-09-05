from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field


class Lead(BaseModel):
    id: Optional[int] = Field(default=None, description="Database id, empty for a new lead")
    name: Optional[str] = Field(default=None, description="Lead's name, may be unknown at first")
    phone_number: str = Field(..., description="Lead's WhatsApp number, used to match conversations")
    source: str = Field(default="whatsapp_organic", description="Where this lead came from, e.g. meta_ad")
    budget_min: Optional[int] = Field(default=None, description="Lowest budget mentioned so far")
    budget_max: Optional[int] = Field(default=None, description="Highest budget mentioned so far")
    timeline: Optional[str] = Field(default=None, description="When the lead wants to move, e.g. '2 months'")
    tier: Optional[str] = Field(default=None, description="hot, warm, or cold")
    status: str = Field(default="new", description="new, contacted, qualified, viewing_booked, closed")


class IncomingMessage(BaseModel):
    phone_number: str = Field(..., description="Which lead this message is from")
    content: str = Field(..., description="The actual text the lead sent")
    message_id: Optional[str] = Field(default=None, description="WhatsApp's unique message ID, used to prevent duplicate processing")
    received_at: datetime = Field(default_factory=datetime.utcnow, description="When we got this message")


class AgentReply(BaseModel):
    phone_number: str = Field(..., description="Which lead this reply is going to")
    content: str = Field(..., description="The reply text the agent generated")


class Listing(BaseModel):
    id: Optional[int] = Field(default=None, description="Database id, empty for a new listing")
    title: str = Field(..., description="Short listing title, e.g. '3-bed in DHA Phase 6'")
    location: str = Field(..., description="Area or address of the property")
    price: int = Field(..., description="Listing price")
    bedrooms: int = Field(..., description="Number of bedrooms")
    description: str = Field(..., description="Full listing details for the agent to reference")
    status: str = Field(default="available", description="available, sold, or rented")