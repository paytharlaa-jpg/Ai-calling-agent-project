import os
from dotenv import load_dotenv
from twilio.rest import Client

load_dotenv()

# The WebSocket URL we got from localtunnel
localtunnel_url = "wss://odd-houses-clean.loca.lt"

twiml_response = f"""
<Response>
    <Connect>
        <Stream url="{localtunnel_url}" />
    </Connect>
</Response>
"""

client = Client(os.getenv("TWILIO_ACCOUNT_SID"), os.getenv("TWILIO_AUTH_TOKEN"))

try:
    import urllib.parse
    twiml_encoded = urllib.parse.quote(twiml_response)
    echo_url = f"http://twimlets.com/echo?Twiml={twiml_encoded}"

    call = client.calls.create(
        to="+919959751331",
        from_="+17372508034",
        url=echo_url
    )
    print(f"Successfully triggered test call to +919959751331. Call SID: {call.sid}")
except Exception as e:
    print(f"Failed to trigger test call: {e}")
