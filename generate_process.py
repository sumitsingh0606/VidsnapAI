"""
Background worker — run this as a separate process (Railway worker dyno).
It polls user_uploads/ every 4 seconds and converts any new submission
into a reel using ffmpeg.
"""

import os
import subprocess
import time

from text_to_audio import text_to_speech_file

DONE_FILE = "done.txt"
UPLOADS_DIR = "user_uploads"
REELS_DIR = os.path.join("static", "reels")


# ── Helpers ────────────────────────────────────────────────────────────────────
def load_done() -> set:
    if not os.path.exists(DONE_FILE):
        return set()
    with open(DONE_FILE, "r") as f:
        return {line.strip() for line in f if line.strip()}


def mark_done(folder: str):
    with open(DONE_FILE, "a") as f:
        f.write(folder + "\n")


def text_to_audio(folder: str):
    desc_path = os.path.join(UPLOADS_DIR, folder, "desc.txt")
    with open(desc_path) as f:
        text = f.read().strip()
    print(f"[TTA] Generating audio for: {folder}")
    text_to_speech_file(text, folder)


def create_reel(folder: str):
    input_txt = os.path.join(UPLOADS_DIR, folder, "input.txt")
    audio_mp3 = os.path.join(UPLOADS_DIR, folder, "audio.mp3")
    output_mp4 = os.path.join(REELS_DIR, f"{folder}.mp4")

    command = [
        "ffmpeg",
        "-f", "concat",
        "-safe", "0",
        "-i", input_txt,
        "-i", audio_mp3,
        "-vf", "scale=1080:1920:force_original_aspect_ratio=decrease,"
               "pad=1080:1920:(ow-iw)/2:(oh-ih)/2:black",
        "-c:v", "libx264",
        "-c:a", "aac",
        "-shortest",
        "-r", "30",
        "-pix_fmt", "yuv420p",
        output_mp4,
    ]

    print(f"[CR] Creating reel for: {folder}")
    subprocess.run(command, check=True)
    print(f"[CR] Done: {output_mp4}")


# ── Main loop ──────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    os.makedirs(UPLOADS_DIR, exist_ok=True)
    os.makedirs(REELS_DIR, exist_ok=True)

    print("Worker started — polling for new submissions...")

    while True:
        try:
            done = load_done()
            folders = set(os.listdir(UPLOADS_DIR))

            for folder in folders - done:
                folder_path = os.path.join(UPLOADS_DIR, folder)

                # Only process complete submissions (must have input.txt + desc.txt)
                has_input = os.path.exists(os.path.join(folder_path, "input.txt"))
                has_desc = os.path.exists(os.path.join(folder_path, "desc.txt"))

                if not (has_input and has_desc):
                    continue

                try:
                    text_to_audio(folder)
                    create_reel(folder)
                    mark_done(folder)
                except Exception as e:
                    print(f"[ERROR] Failed to process {folder}: {e}")

        except Exception as e:
            print(f"[LOOP ERROR] {e}")

        time.sleep(4)
