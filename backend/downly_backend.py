print("🔥 BACKEND FILE LOADED 🔥")

from fastapi import FastAPI, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from pathlib import Path
import subprocess
import uuid
import os

from database import create_db_and_tables
from auth.routes import router as auth_router


# 🚀 Initialize FastAPI
app = FastAPI()

# 🔓 CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 📂 Download configuration
BASE_DIR = Path(__file__).resolve().parent
DOWNLOAD_DIR = BASE_DIR / "downloads"
FFMPEG_PATH = "ffmpeg"  # Ensure ffmpeg is available in PATH

DOWNLOAD_DIR.mkdir(exist_ok=True)

# 📡 Startup event
@app.on_event("startup")
def on_startup():
    create_db_and_tables()
    print("✅ Database & Tables ready")

# 🔗 Register authentication routes
app.include_router(auth_router)

# 🎧 Download audio endpoint
@app.post("/download")
async def download_audio(url: str = Form(...)):
    temp_id = str(uuid.uuid4())
    webm_path = DOWNLOAD_DIR / f"{temp_id}.webm"
    mp3_path = DOWNLOAD_DIR / f"{temp_id}.mp3"

    try:
        subprocess.run(["yt-dlp", "-f", "bestaudio", "-o", str(webm_path), url], check=True)
        subprocess.run([FFMPEG_PATH, "-i", str(webm_path), "-vn", "-ab", "192k", "-ar", "44100", "-y", str(mp3_path)], check=True)
        os.remove(webm_path)
        return FileResponse(mp3_path, media_type="audio/mpeg", filename=f"{temp_id}.mp3")
    except subprocess.CalledProcessError as e:
        return {"error": f"Download failed: {e}"}
    except Exception as e:
        return {"error": str(e)}

# 🎥 Download video endpoint
@app.post("/download-video")
async def download_video(url: str = Form(...)):
    temp_id = str(uuid.uuid4())
    mp4_path = DOWNLOAD_DIR / f"{temp_id}.mp4"

    try:
        subprocess.run(["yt-dlp", "-f", "best", "-o", str(mp4_path), url], check=True)
        return FileResponse(mp4_path, media_type="video/mp4", filename=f"{temp_id}.mp4")
    except subprocess.CalledProcessError as e:
        return {"error": f"Video download failed: {e}"}
    except Exception as e:
        return {"error": str(e)}
