import os

# Load from environment variable (set this in Railway dashboard)
# Never hardcode API keys — use environment variables
ELEVENLABS_API_KEY = os.environ.get("ELEVENLABS_API_KEY", "")

if not ELEVENLABS_API_KEY:
    raise RuntimeError("ELEVENLABS_API_KEY environment variable is not set.")
