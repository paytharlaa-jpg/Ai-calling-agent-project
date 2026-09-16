from fastapi import FastAPI, Depends, HTTPException, BackgroundTasks
from sqlalchemy.orm import Session
import models
import schemas
from database import engine, get_db

# Create tables
models.Base.metadata.create_all(bind=engine)

app = FastAPI(title="TryGaruda Voice AI Platform API")

# --- USER ENDPOINTS ---

@app.post("/users/", response_model=schemas.User)
def create_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    db_user = db.query(models.User).filter(models.User.email == user.email).first()
    if db_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    db_user = models.User(email=user.email, company_name=user.company_name)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

# --- AGENT ENDPOINTS ---

@app.post("/users/{user_id}/agents/", response_model=schemas.Agent)
def create_agent_for_user(
    user_id: int, agent: schemas.AgentCreate, db: Session = Depends(get_db)
):
    db_agent = models.Agent(**agent.model_dump(), owner_id=user_id)
    db.add(db_agent)
    db.commit()
    db.refresh(db_agent)
    return db_agent

@app.get("/agents/{agent_id}", response_model=schemas.Agent)
def get_agent(agent_id: int, db: Session = Depends(get_db)):
    agent = db.query(models.Agent).filter(models.Agent.id == agent_id).first()
    if agent is None:
        raise HTTPException(status_code=404, detail="Agent not found")
    return agent

# --- CALL ENDPOINTS ---

import redis
import json
import os

# Connect to Redis
redis_client = redis.Redis(
    host=os.getenv("REDIS_HOST", "localhost"),
    port=int(os.getenv("REDIS_PORT", 6379)),
    decode_responses=True
)

def trigger_outbound_call_worker(phone_number: str, agent_id: int):
    """
    Pushes an outbound call job to the Redis queue.
    The LiveKit workers listen to this queue and initiate the WebRTC pipeline.
    """
    job_payload = {
        "action": "outbound_call",
        "phone_number": phone_number,
        "agent_id": agent_id
    }
    
    # Push to the 'outbound_calls' queue
    redis_client.lpush("outbound_calls", json.dumps(job_payload))
    print(f"DEBUG: Queued call to {phone_number} for Agent ID {agent_id} in Redis.")

@app.post("/agents/{agent_id}/calls/outbound")
def make_outbound_call(
    agent_id: int, phone_number: str, background_tasks: BackgroundTasks, db: Session = Depends(get_db)
):
    # Verify agent exists
    agent = db.query(models.Agent).filter(models.Agent.id == agent_id).first()
    if not agent:
        raise HTTPException(status_code=404, detail="Agent not found")
    
    # Send the job to the background worker queue
    background_tasks.add_task(trigger_outbound_call_worker, phone_number, agent_id)
    
    return {"status": "queued", "phone_number": phone_number, "agent_id": agent_id}

# --- TWILIO & WEBHOOKS ENDPOINTS ---

from fastapi.responses import HTMLResponse
import httpx

@app.post("/twilio/twiml")
def twilio_twiml(agent_id: int):
    """
    Twilio hits this endpoint when the call is answered.
    We return TwiML instructing Twilio to open a WebSocket stream to the worker.
    """
    # In production, worker_url should point to the specific auto-scaled worker instance
    worker_url = os.getenv("WORKER_WEBSOCKET_URL", "wss://your-ngrok-url.ngrok-free.app")
    
    twiml_response = f"""
    <Response>
        <Connect>
            <Stream url="{worker_url}" />
        </Connect>
    </Response>
    """
    return HTMLResponse(content=twiml_response, media_type="application/xml")

from pydantic import BaseModel

class CallCompletion(BaseModel):
    call_id: str
    status: str
    transcript: list

@app.post("/internal/calls/{agent_id}/complete")
async def call_completed_webhook(agent_id: int, completion: CallCompletion, db: Session = Depends(get_db)):
    """
    The agent worker hits this endpoint when the call finishes.
    This API then looks up the customer's webhook_url and dispatches the data.
    """
    agent = db.query(models.Agent).filter(models.Agent.id == agent_id).first()
    if not agent:
        raise HTTPException(status_code=404, detail="Agent not found")
        
    if agent.webhook_url:
        payload = {
            "event": "call.completed",
            "agent_id": agent_id,
            "call_id": completion.call_id,
            "status": completion.status,
            "transcript": completion.transcript
        }
        
        # Dispatch to customer's server asynchronously
        try:
            async with httpx.AsyncClient() as client:
                await client.post(agent.webhook_url, json=payload, timeout=5.0)
            print(f"DEBUG: Dispatched webhook for call {completion.call_id} to {agent.webhook_url}")
        except Exception as e:
            print(f"ERROR: Failed to dispatch webhook: {e}")
            
    return {"status": "success"}
