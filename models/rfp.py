from pydantic import BaseModel, Field, EmailStr
from typing import Optional, List, Dict
from datetime import datetime
from enum import Enum

class RFPStatus(str, Enum):
    DRAFT = "draft"
    PENDING_APPROVAL = "pending_approval"
    APPROVED = "approved"
    REJECTED = "rejected"
    SENT = "sent"
    CANCELLED = "cancelled"

class Supplier(BaseModel):
    """Model for a supplier."""
    name: str
    email: EmailStr
    phone: Optional[str] = None
    contact_person: Optional[str] = None

class RFP(BaseModel):
    """Model for a Request for Proposal."""
    id: Optional[str] = None
    request_id: str
    title: str
    category: str
    content: str
    status: RFPStatus = RFPStatus.DRAFT
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)
    suppliers: List[Supplier] = []
    approval_feedback: Optional[str] = None
    approval_date: Optional[datetime] = None
    sent_date: Optional[datetime] = None
    
    class Config:
        use_enum_values = True

class ApprovalResult(BaseModel):
    """Model for the result of RFP approval."""
    rfp_id: str
    approved: bool
    feedback: str
    issues: List[str] = []