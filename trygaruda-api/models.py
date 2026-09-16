from sqlalchemy import Column, Integer, String, Text, ForeignKey, JSON
from sqlalchemy.orm import relationship
from database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True)
    company_name = Column(String)
    
    agents = relationship("Agent", back_populates="owner")

class Agent(Base):
    __tablename__ = "agents"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    owner_id = Column(Integer, ForeignKey("users.id"))
    
    # AI Configuration
    system_prompt = Column(Text)
    voice_id = Column(String) # E.g., a Cartesia or ElevenLabs Voice ID
    tools = Column(JSON) # JSON array of tool definitions
    webhook_url = Column(String, nullable=True) # Where to send call transcripts
    
    owner = relationship("User", back_populates="agents")
    calls = relationship("CallLog", back_populates="agent")

class CallLog(Base):
    __tablename__ = "call_logs"

    id = Column(String, primary_key=True, index=True) # UUID for the call
    agent_id = Column(Integer, ForeignKey("agents.id"))
    direction = Column(String) # "inbound" or "outbound"
    status = Column(String) # "completed", "failed", "in_progress"
    transcript = Column(JSON)
    recording_url = Column(String, nullable=True)
    
    agent = relationship("Agent", back_populates="calls")
