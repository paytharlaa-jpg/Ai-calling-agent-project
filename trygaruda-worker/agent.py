import asyncio
import os
import sys

from pipecat.pipeline.pipeline import Pipeline
from pipecat.pipeline.runner import PipelineRunner
from pipecat.pipeline.task import PipelineParams, PipelineTask
from pipecat.processors.aggregators.llm_response import LLMFullResponseAggregator
from pipecat.services.cartesia import CartesiaTTSService
from pipecat.services.deepgram import DeepgramSTTService
from pipecat.services.openai import OpenAILLMService
from pipecat.transports.network.websocket_server import (
    WebsocketServerParams,
    WebsocketServerTransport,
)
from pipecat.vad.silero import SileroVADAnalyzer

import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("trygaruda-worker")


async def main():
    """
    TryGaruda Core Agent Worker
    This script runs the low-latency real-time pipeline (STT -> LLM -> TTS).
    It uses a WebSocket transport, which is how SIP telephony providers (like Twilio/Plivo)
    will connect media to your agent.
    """
    
    # Check for required API keys (in production, these come from your TryGaruda API based on the tenant)
    required_env_vars = ["OPENAI_API_KEY", "DEEPGRAM_API_KEY", "CARTESIA_API_KEY"]
    missing = [var for var in required_env_vars if not os.getenv(var)]
    if missing:
        logger.error(f"Missing required environment variables: {', '.join(missing)}")
        logger.error("Please set them before running the worker.")
        sys.exit(1)

    # 1. Transport (WebSocket for Twilio/Plivo Media Streams)
    # This listens for incoming audio streams from a phone call.
    transport = WebsocketServerTransport(
        params=WebsocketServerParams(
            audio_out_enabled=True,
            add_wav_header=False, # Raw PCM audio typically used by SIP providers
            vad_enabled=True,
            vad_analyzer=SileroVADAnalyzer(), # Used for barge-in detection
            vad_audio_passthrough=True,
            host="0.0.0.0",
            port=8765
        )
    )

    # 2. STT (Speech-to-Text) - Deepgram Nova-3 is currently the latency leader
    stt = DeepgramSTTService(
        model="nova-3",
        language="en",
        interim_results=True # Critical for low latency (speculative execution)
    )

    # 3. LLM (Dialog Manager) - GPT-4o-mini (fast and supports tool calling)
    llm = OpenAILLMService(
        model="gpt-4o-mini",
        api_key=os.getenv("OPENAI_API_KEY")
    )

    # 4. TTS (Text-to-Speech) - Cartesia Sonic for sub-100ms TTFA
    tts = CartesiaTTSService(
        model="sonic-english",
        voice_id="a0e99841-438c-4a64-b679-ae501e7d6091", # Example expressive voice
        api_key=os.getenv("CARTESIA_API_KEY")
    )

    messages = [
        {
            "role": "system",
            "content": (
                "You are an AI assistant representing TryGaruda. "
                "Keep your responses concise, warm, and conversational. "
                "Do not use markdown or lists, as your text will be spoken out loud. "
                "If asked, you are an AI assistant."
            )
        }
    ]

    tma_out = LLMFullResponseAggregator()

    pipeline = Pipeline(
        [
            transport.input(),   # Audio frames from caller
            stt,                 # Converts audio to text
            llm,                 # Generates reply text
            tts,                 # Converts reply text to audio
            transport.output(),  # Audio frames back to caller
            tma_out,             # Aggregates assistant reply into history
        ]
    )

    # Wrap the pipeline in a task to handle graceful start/stop
    task = PipelineTask(
        pipeline,
        PipelineParams(
            allow_interruptions=True, # BARGE-IN: Stops TTS if caller speaks
            enable_metrics=True,      # Important for the dashboard
            enable_usage_metrics=True,
        ),
    )

    @transport.event_handler("on_client_connected")
    async def on_client_connected(transport, client):
        logger.info(f"Caller connected! Starting conversation...")
        # Optional: Kick off the conversation with a greeting
        messages.append({"role": "system", "content": "The user has connected. Please say a brief greeting."})
        await task.queue_frames([llm.process_messages()])

    @transport.event_handler("on_client_disconnected")
    async def on_client_disconnected(transport, client):
        logger.info(f"Caller disconnected.")
        # Trigger the post-call summary and webhook dispatch
        agent_id = os.getenv("AGENT_ID", "1") # Default to 1 if not passed
        api_url = f"{os.getenv('TRYGARUDA_API_URL', 'http://localhost:8000')}/internal/calls/{agent_id}/complete"
        
        try:
            import httpx
            async with httpx.AsyncClient() as http_client:
                await http_client.post(
                    api_url, 
                    json={
                        "call_id": "call_" + str(hash(client)), # Placeholder for real call ID
                        "status": "completed",
                        "transcript": messages # Send the full conversation history
                    }
                )
            logger.info("Successfully dispatched call completion to TryGaruda API.")
        except Exception as e:
            logger.error(f"Failed to dispatch call completion: {e}")
    runner = PipelineRunner()

    logger.info("TryGaruda Agent Worker starting. Listening on ws://0.0.0.0:8765")
    # This runs the websocket server and blocks
    await runner.run(task)


if __name__ == "__main__":
    asyncio.run(main())
