from fastapi import FastAPI, Form, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from passlib.context import CryptContext
from jose import jwt, JWTError
from datetime import datetime, timedelta
from pathlib import Path
import subprocess
import uuid
import os

app = FastAPI()

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Authentication settings
SECRET_KEY = "your_secret_key"  # Replace with a secure key in production
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")

# Password hashing context
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# In-memory user database
users_db = {}

def get_password_hash(password):
    return pwd_context.hash(password)

def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def create_access_token(data: dict, expires_delta: timedelta = None):
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

def get_current_user(token: str = Depends(oauth2_scheme)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid authentication credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    user = users_db.get(email)
    if user is None:
        raise credentials_exception
    return user

# Signup endpoint
@app.post("/signup")
async def signup(email: str = Form(...), password: str = Form(...)):
    if email in users_db:
        raise HTTPException(status_code=400, detail="Email already registered")
    hashed_password = get_password_hash(password)
    users_db[email] = {
        "email": email,
        "hashed_password": hashed_password,
        "referrals": 0,
        "earnings": 0.0
    }
    return {"message": "Account created successfully"}

# Login endpoint
@app.post("/login")
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    user = users_db.get(form_data.username)
    if not user or not verify_password(form_data.password, user["hashed_password"]):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    access_token = create_access_token(data={"sub": user["email"]})
    return {"access_token": access_token, "token_type": "bearer"}

# User dashboard endpoint
@app.get("/dashboard")
async def dashboard(current_user: dict = Depends(get_current_user)):
    return {
        "email": current_user["email"],
        "referrals": current_user["referrals"],
        "earnings": current_user["earnings"]
    }

# Ensure downloads directory exists
BASE_DIR = Path(__file__).resolve().parent
DOWNLOAD_DIR = BASE_DIR / "downloads"
DOWNLOAD_DIR.mkdir(exist_ok=True)

FFMPEG_PATH = "ffmpeg"  # Ensure ffmpeg is installed and accessible

# Audio download endpoint
@app.post("/download")
async def download_audio(url: str = Form(...)):
    temp_id = str(uuid.uuid4())
    webm_path = DOWNLOAD_DIR / f"{temp_id}.webm"
    mp3_path = DOWNLOAD_DIR / f"{temp_id}.mp3"

    try:
        # Download audio using yt-dlp
        subprocess.run([
            "yt-dlp",
            "-f", "bestaudio",
            "-o", str(webm_path),
            url
        ], check=True)

        # Convert to mp3 using ffmpeg
        subprocess.run([
            FFMPEG_PATH,
            "-i", str(webm_path),
            "-vn",
            "-ab", "192k",
            "-ar", "44100",
            "-y",
            str(mp3_path)
        ], check=True)

        # Clean up webm file
        os.remove(webm_path)

        return FileResponse(mp3_path, media_type="audio/mpeg", filename=f"{temp_id}.mp3")

    except subprocess.CalledProcessError as e:
        return {"error": f"Download or conversion failed: {e}"}
    except Exception as e:
        return {"error": str(e)}