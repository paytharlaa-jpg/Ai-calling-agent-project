# TryGaruda Core Agent Worker

This is the core low-latency real-time voice pipeline for TryGaruda. It uses the `pipecat-ai` framework to stream audio via WebSockets.

## Setup

1. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Set your API keys as environment variables:
```bash
export OPENAI_API_KEY="your-key"
export DEEPGRAM_API_KEY="your-key"
export CARTESIA_API_KEY="your-key"
```

4. Run the worker:
```bash
python agent.py
```
The worker will start listening on `ws://0.0.0.0:8765`.

## Connecting to Telephony (SIP Bridging)

To connect this worker to real phone calls, you need a SIP trunk provider (like Twilio, Telnyx, or Plivo).

### Using Twilio Media Streams (Example)

When a call comes into your Twilio phone number, Twilio executes a TwiML Bin (or hits your API) to tell it what to do. You instruct Twilio to open a `<Stream>` to your WebSocket.

1. **Expose your local server:** Use `ngrok` or similar to expose port 8765.
   ```bash
   ngrok http 8765
   ```
2. **Configure Twilio TwiML:** Return this XML when a call comes in:
   ```xml
   <Response>
       <Connect>
           <Stream url="wss://YOUR-NGROK-URL.ngrok-free.app" />
       </Connect>
   </Response>
   ```

Twilio will bridge the raw audio stream to your worker, which handles the STT -> LLM -> TTS loop.
