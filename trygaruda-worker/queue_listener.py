import os
import json
import redis
import time
import subprocess
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("trygaruda-queue-listener")

# Connect to Redis
redis_client = redis.Redis(
    host=os.getenv("REDIS_HOST", "localhost"),
    port=int(os.getenv("REDIS_PORT", 6379)),
    decode_responses=True
)

QUEUE_NAME = "outbound_calls"

def process_outbound_call(job):
    """
    This function processes the job payload from Redis.
    In a production system, it would:
    1. Fetch the Agent configuration from the TryGaruda API.
    2. Use the Twilio/Telnyx REST API to initiate a call to `phone_number`.
    3. Pass the Webhook URL of this worker so Twilio bridges the audio.
    4. Spin up the Pipecat agent loop for this specific call.
    """
    phone_number = job.get("phone_number")
    agent_id = job.get("agent_id")
    
    logger.info(f"Processing outbound call for Agent {agent_id} to {phone_number}")
    
    # Start the agent worker in the background (or in a new thread)
    # Using Popen to run the agent asynchronously for this specific call
    env = os.environ.copy()
    env["AGENT_ID"] = str(agent_id)
    worker_process = subprocess.Popen(["python", "agent.py"], env=env)
    
    # Trigger Twilio to dial the number
    # The URL points to the TryGaruda API which will return the TwiML XML
    try:
        from twilio.rest import Client
        twilio_client = Client(os.getenv("TWILIO_ACCOUNT_SID"), os.getenv("TWILIO_AUTH_TOKEN"))
        
        # We pass the agent_id to the Twilio webhook URL so the API knows which agent is handling the call
        api_twiml_url = f"{os.getenv('TRYGARUDA_API_URL', 'https://api.trygaruda.com')}/twilio/twiml?agent_id={agent_id}"
        
        call = twilio_client.calls.create(
            to=phone_number,
            from_=os.getenv("TWILIO_PHONE_NUMBER"),
            url=api_twiml_url
        )
        logger.info(f"Successfully triggered Twilio call {call.sid} for {phone_number}")
    except Exception as e:
        logger.error(f"Failed to trigger Twilio call: {e}")
        worker_process.terminate()

def listen_to_queue():
    logger.info(f"Listening for jobs on Redis queue: '{QUEUE_NAME}'...")
    while True:
        try:
            # BRPOP blocks until an item is available in the queue
            result = redis_client.brpop(QUEUE_NAME, timeout=0)
            if result:
                queue, payload_str = result
                job = json.loads(payload_str)
                process_outbound_call(job)
        except Exception as e:
            logger.error(f"Error processing queue: {e}")
            time.sleep(5) # Backoff on error

if __name__ == "__main__":
    listen_to_queue()
