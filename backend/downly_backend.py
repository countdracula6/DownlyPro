print("🔥 BACKEND FILE LOADED 🔥")

from fastapi import FastAPI, Form
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import os
import uuid
import subprocess

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)

# 💡 Mount static files at /static to avoid conflict
app.mount("/static", StaticFiles(directory="C:/Users/pc/Desktop/DownlyPRO/frontend"), name="static")

# ✨ Serve index.html manually
@app.get("/")
def root():
    return FileResponse("C:/Users/pc/Desktop/DownlyPRO/frontend/index.html", media_type="text/html")

# 🔧 Configuration
DOWNLOAD_DIR = "downloads"
FFMPEG_PATH = "C:/ffmpeg-7.1.1-essentials_build/bin/ffmpeg.exe"

os.makedirs(DOWNLOAD_DIR, exist_ok=True)

# 🎧 Audio download endpoint
@app.post("/download")
async def download_audio(url: str = Form(...)):
    temp_id = str(uuid.uuid4())
    webm_path = os.path.join(DOWNLOAD_DIR, f"{temp_id}.webm")
    mp3_path = os.path.join(DOWNLOAD_DIR, f"{temp_id}.mp3")

    try:
        print("📥 yt-dlp starting for:", url)
        subprocess.run(["yt-dlp", "-f", "251", "-o", webm_path, url], check=True)

        print("🎧 ffmpeg converting...")
        subprocess.run([FFMPEG_PATH, "-i", webm_path, "-vn", "-ab", "192k", "-ar", "44100", "-y", mp3_path], check=True)

        os.remove(webm_path)
        print("✅ MP3 ready")
        return FileResponse(mp3_path, media_type="audio/mpeg", filename="downlypro_audio.mp3")
    except Exception as e:
        print("❌ Error:", e)
        return {"error": str(e)}

# 🎥 Video download endpoint
@app.post("/download-video")
async def download_video(url: str = Form(...)):
    temp_id = str(uuid.uuid4())
    mp4_path = os.path.join(DOWNLOAD_DIR, f"{temp_id}.mp4")

    try:
        print("📥 yt-dlp starting for:", url)
        subprocess.run(["yt-dlp", "-f", "best", "-o", mp4_path, url], check=True)

        print("✅ MP4 ready")
        return FileResponse(mp4_path, media_type="video/mp4", filename="downlypro_video.mp4")
    except Exception as e:
        print("❌ Error:", e)
        return {"error": str(e)}
