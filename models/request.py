from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime

class ProcurementRequest(BaseModel):
    """Model for a procurement request submitted by a user."""
    id: Optional[str] = None
    title: str
    description: str
    estimated_budget: Optional[float] = None
    timeline: Optional[str] = None
    department: Optional[str] = None
    requester: Optional[str] = None
    required_by_date: Optional[datetime] = None
    additional_notes: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.now)
    
class ClassificationResult(BaseModel):
    """Model for the result of classification."""
    request_id: str
    category: str
    confidence: float
    reasoning: str