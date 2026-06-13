import os

from elevenlabs import VoiceSettings
from elevenlabs.client import ElevenLabs

from config import ELEVENLABS_API_KEY

client = ElevenLabs(api_key=ELEVENLABS_API_KEY)


def text_to_speech_file(text: str, folder: str) -> str:
    """
    Convert `text` to speech and save it as audio.mp3 inside
    user_uploads/<folder>/audio.mp3.

    Returns the path to the saved file.
    """
    response = client.text_to_speech.convert(
        voice_id="pNInz6obpgDQGcFmaJgB",   # Adam — pre-made voice
        output_format="mp3_22050_32",
        text=text,
        model_id="eleven_turbo_v2_5",       # low-latency turbo model
        voice_settings=VoiceSettings(
            stability=0.0,
            similarity_boost=1.0,
            style=0.0,
            use_speaker_boost=True,
            speed=1.0,
        ),
    )

    save_file_path = os.path.join("user_uploads", folder, "audio.mp3")

    with open(save_file_path, "wb") as f:
        for chunk in response:
            if chunk:
                f.write(chunk)

    print(f"[TTS] Saved: {save_file_path}")
    return save_file_path
