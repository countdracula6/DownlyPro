from fastapi import FastAPI, Form
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
import os
import uuid
import subprocess
from pathlib import Path

app = FastAPI()

# ✅ CORS for frontend to call backend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)

# ✅ Auto-create downloads folder
BASE_DIR = Path(__file__).resolve().parent
DOWNLOAD_DIR = BASE_DIR / "downloads"
DOWNLOAD_DIR.mkdir(exist_ok=True)

# ✅ ffmpeg setup (Render uses preinstalled ffmpeg)
FFMPEG_PATH = "ffmpeg"

# 🎧 AUDIO DOWNLOAD ENDPOINT
@app.post("/download")
async def download_audio(url: str = Form(...)):
    temp_id = str(uuid.uuid4())
    webm_path = DOWNLOAD_DIR / f"{temp_id}.webm"
    mp3_path = DOWNLOAD_DIR / f"{temp_id}.mp3"

    try:
        print(f"📥 Downloading audio: {url}")
        subprocess.run(["yt-dlp", "-f", "251", "-o", str(webm_path), url], check=True)

        print("🎧 Converting to MP3...")
        subprocess.run([
            FFMPEG_PATH, "-i", str(webm_path), "-vn", "-ab", "192k", "-ar", "44100", "-y", str(mp3_path)
        ], check=True)

        os.remove(webm_path)
        print("✅ MP3 ready:", mp3_path.name)
        return FileResponse(mp3_path, media_type="audio/mpeg", filename="downlypro_audio.mp3")

    except Exception as e:
        print("❌ Error:", e)
        return {"error": str(e)}

# 🎥 VIDEO DOWNLOAD ENDPOINT
@app.post("/download-video")
async def download_video(url: str = Form(...)):
    temp_id = str(uuid.uuid4())
    mp4_path = DOWNLOAD_DIR / f"{temp_id}.mp4"

    try:
        print(f"📥 Downloading video: {url}")
        subprocess.run(["yt-dlp", "-f", "best", "-o", str(mp4_path), url], check=True)

        print("✅ MP4 ready:", mp4_path.name)
        return FileResponse(mp4_path, media_type="video/mp4", filename="downlypro_video.mp4")

    except Exception as e:
        print("❌ Error:", e)
        return {"error": str(e)}

# ✅ Health Check Endpoint
@app.get("/ping")
def ping():
    return {"message": "pong"}
