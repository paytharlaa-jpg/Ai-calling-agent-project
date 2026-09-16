from pydantic import BaseModel
from typing import List, Optional, Any

# Agent Schemas
class AgentBase(BaseModel):
    name: str
    system_prompt: str
    voice_id: str
    tools: Optional[List[Any]] = []
    webhook_url: Optional[str] = None

class AgentCreate(AgentBase):
    pass

class Agent(AgentBase):
    id: int
    owner_id: int

    class Config:
        from_attributes = True

# User Schemas
class UserBase(BaseModel):
    email: str
    company_name: str

class UserCreate(UserBase):
    pass

class User(UserBase):
    id: int
    agents: List[Agent] = []

    class Config:
        from_attributes = True
