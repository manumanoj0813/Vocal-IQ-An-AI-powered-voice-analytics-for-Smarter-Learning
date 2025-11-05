from fastapi import FastAPI, UploadFile, File, HTTPException, Depends, status, Request, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from fastapi.responses import StreamingResponse, FileResponse
from datetime import datetime, timedelta
from typing import List, Optional, Dict
import json
import os
import tempfile
from pathlib import Path
from jose import JWTError, jwt
from passlib.context import CryptContext
from bson import ObjectId
from pydantic import BaseModel, Field
import logging
import io
import random
import smtplib
from email.mime.text import MIMEText

from voice_analyzer import VoiceAnalyzer
from enhanced_analyzer import EnhancedAnalyzer
from export_utils import DataExporter, ChartGenerator
from pdf_generator import VoiceAnalysisPDFGenerator
from database import (
    init_db,
    create_user,
    get_user_by_username,
    get_user_by_email,
    get_user_by_username_or_email,
    create_recording,
    get_user_recordings,
    create_practice_session,
    get_user_practice_sessions,
    update_progress_metrics,
    get_user_progress,
    list_users,
    list_recent_recordings,
    get_usage_metrics,
    set_user_otp,
    clear_user_otp,
    set_password_reset_token,
    reset_password_with_token
)
from models import (
    UserDB, RecordingDB, PracticeSessionDB, ProgressMetricsDB,
    LanguageDetectionResult, VoiceCloningDetectionResult, ExportRequest
)

# Logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# FastAPI App
app = FastAPI()

# CORS Configuration
# Allow configurable frontend origins; defaults to '*'
allowed_origins_env = os.getenv("ALLOWED_ORIGINS")
if allowed_origins_env:
    origins = [o.strip() for o in allowed_origins_env.split(",") if o.strip()]
else:
    origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["Content-Disposition", "Authorization"],
)

# Add OPTIONS handler for CORS preflight
@app.options("/{full_path:path}")
async def options_handler(full_path: str):
    return {"message": "CORS preflight"}

# JWT Setup
SECRET_KEY = os.getenv("SECRET_KEY", "your-super-secret-key")
logger.info(f"Using SECRET_KEY: {SECRET_KEY}")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# Auth
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

# Request Models
class UserCreate(BaseModel):
    username: str
    email: str
    password: str
    is_admin: Optional[bool] = False
    otp: Optional[str] = None

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    username: Optional[str] = None

class LoginRequest(BaseModel):
    username: str
    password: str

class OTPRequest(BaseModel):
    identifier: str  # username or email

class ForgotPasswordRequest(BaseModel):
    email: str

class ResetPasswordRequest(BaseModel):
    token: str
    new_password: str

# Auth Helpers
def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password):
    return pwd_context.hash(password)

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=15))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

def send_email(to_email: str, subject: str, body: str):
    smtp_host = os.getenv("SMTP_HOST")
    smtp_port = int(os.getenv("SMTP_PORT", "587"))
    smtp_user = os.getenv("SMTP_USER")
    smtp_pass = os.getenv("SMTP_PASS")
    from_email = os.getenv("FROM_EMAIL", smtp_user or "no-reply@vocal-iq.local")

    if not smtp_host or not smtp_user or not smtp_pass:
        logger.warning(f"SMTP not configured. Would send to {to_email}: {subject} - {body}")
        return

    msg = MIMEText(body)
    msg["Subject"] = subject
    msg["From"] = from_email
    msg["To"] = to_email

    try:
        if smtp_port == 465:
            with smtplib.SMTP_SSL(smtp_host, smtp_port) as server:
                server.login(smtp_user, smtp_pass)
                server.send_message(msg)
        else:
            with smtplib.SMTP(smtp_host, smtp_port) as server:
                server.ehlo()
                server.starttls()
                server.ehlo()
                server.login(smtp_user, smtp_pass)
                server.send_message(msg)
        logger.info(f"Email sent to {to_email} via {smtp_host}:{smtp_port}")
    except Exception as e:
        logger.error(f"SMTP send failed to {to_email}: {e}")

async def get_current_user(token: str = Depends(oauth2_scheme)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
        token_data = TokenData(username=username)
    except JWTError:
        raise credentials_exception
    user = await get_user_by_username(token_data.username)
    if user is None:
        raise credentials_exception
    return user

# Startup: init DB
@app.on_event("startup")
async def startup_event():
    logger.info("Initializing database...")
    await init_db()

# Routes
@app.post("/register", response_model=Token)
async def register_user_endpoint(user: UserCreate):
    if await get_user_by_username(user.username):
        raise HTTPException(status_code=400, detail="Username already registered")
    # Email can be reused across accounts; only username must be unique
    # OTP is no longer required for registration

    hashed_password = get_password_hash(user.password)
    user_db = UserDB(username=user.username, email=user.email, hashed_password=hashed_password, is_admin=bool(user.is_admin))
    await create_user(user_db)

    access_token = create_access_token(data={"sub": user.username}, expires_delta=timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    return {"access_token": access_token, "token_type": "bearer"}

# Compatibility routes for frontend expectations
@app.post("/auth/register", response_model=Token)
async def auth_register(user: UserCreate):
    return await register_user_endpoint(user)

@app.get("/auth/me", response_model=UserDB)
async def auth_me(current_user: dict = Depends(get_current_user)):
    return current_user

@app.post("/token/refresh")
async def token_refresh(current_user: dict = Depends(get_current_user)):
    # If the provided token is valid, issue a fresh token
    access_token = create_access_token(data={"sub": current_user["username"]}, expires_delta=timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    return {"access_token": access_token, "token_type": "bearer"}

@app.post("/auth/request-otp")
async def request_otp(payload: OTPRequest):
    user = await get_user_by_username_or_email(payload.identifier)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    code = f"{random.randint(100000, 999999)}"
    expires_at = datetime.utcnow() + timedelta(minutes=10)
    await set_user_otp(payload.identifier, code, expires_at)
    try:
        to_email = user.get("email")
        logger.info(f"Issuing OTP for {user.get('username')} to {to_email}: {code}")
        send_email(to_email, "Your Vocal IQ OTP", f"Your OTP is {code}. It expires in 10 minutes.")
    except Exception as e:
        logger.warning(f"Failed to send OTP email: {e}")
    return {"message": "OTP sent if user exists"}

@app.post("/auth/request-register-otp")
async def request_register_otp(req: ForgotPasswordRequest):
    # Allow sending registration OTP even if email already exists
    code = f"{random.randint(100000, 999999)}"
    expires_at = datetime.utcnow() + timedelta(minutes=10)
    from database import set_registration_otp
    await set_registration_otp(req.email, code, expires_at)
    try:
        send_email(req.email, "Your Vocal IQ Registration OTP", f"Your OTP is {code}. It expires in 10 minutes.")
        logger.info(f"Registration OTP for {req.email}: {code}")
    except Exception as e:
        logger.warning(f"Failed to send registration OTP: {e}")
    return {"message": "Registration OTP sent if email is valid"}

@app.post("/login", response_model=Token)
async def login_with_otp(payload: LoginRequest):
    user = await get_user_by_username(payload.username)
    if not user or not verify_password(payload.password, user["hashed_password"]):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Incorrect username or password")

    # OTP validation removed; proceed with username/password only
    access_token = create_access_token(data={"sub": payload.username}, expires_delta=timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    return {"access_token": access_token, "token_type": "bearer"}

@app.post("/auth/forgot-password")
async def forgot_password(req: ForgotPasswordRequest):
    user = await get_user_by_email(req.email)
    if not user:
        return {"message": "If the email exists, a reset link has been sent"}
    token = jwt.encode({"sub": user["username"], "purpose": "reset", "exp": datetime.utcnow() + timedelta(minutes=30)}, SECRET_KEY, algorithm=ALGORITHM)
    await set_password_reset_token(req.email, token, datetime.utcnow() + timedelta(minutes=30))
    try:
        reset_url = os.getenv("RESET_URL_BASE", "http://localhost:5173") + f"/reset?token={token}"
        send_email(req.email, "Reset your Vocal IQ password", f"Use this token to reset your password: {token}\nOr open: {reset_url}")
    except Exception as e:
        logger.warning(f"Failed to send reset email: {e}")
    return {"message": "If the email exists, a reset link has been sent"}

@app.post("/auth/reset-password")
async def reset_password(req: ResetPasswordRequest):
    try:
        decoded = jwt.decode(req.token, SECRET_KEY, algorithms=[ALGORITHM])
        if decoded.get("purpose") != "reset":
            raise HTTPException(status_code=400, detail="Invalid token")
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid or expired token")

    new_hash = get_password_hash(req.new_password)
    if not await reset_password_with_token(req.token, new_hash):
        raise HTTPException(status_code=400, detail="Invalid or expired token")
    return {"message": "Password has been reset"}

# Admin-only dependencies
def assert_admin(current_user: dict):
    if not current_user.get("is_admin", False):
        raise HTTPException(status_code=403, detail="Admin privileges required")
    return True

@app.get("/admin/users")
async def admin_list_users(limit: int = 100, current_user: dict = Depends(get_current_user)):
    assert_admin(current_user)
    return await list_users(limit)

@app.get("/admin/recordings")
async def admin_list_recordings(limit: int = 100, current_user: dict = Depends(get_current_user)):
    assert_admin(current_user)
    return await list_recent_recordings(limit)

@app.get("/admin/metrics/summary")
async def admin_metrics_summary(current_user: dict = Depends(get_current_user)):
    assert_admin(current_user)
    return await get_usage_metrics()

@app.post("/token", response_model=Token)
async def login_endpoint(form_data: OAuth2PasswordRequestForm = Depends()):
    user = await get_user_by_username(form_data.username)
    if not user or not verify_password(form_data.password, user["hashed_password"]):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    access_token = create_access_token(data={"sub": user["username"]}, expires_delta=timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    return {"access_token": access_token, "token_type": "bearer"}

@app.get("/users/me", response_model=UserDB)
async def read_users_me(current_user: dict = Depends(get_current_user)):
    return current_user

@app.get("/test")
async def test_endpoint():
    return {"message": "Backend is running and reachable!"}

@app.get("/test-analyzer")
async def test_analyzer_endpoint():
    try:
        # Test if voice analyzer can be initialized
        test_analyzer = VoiceAnalyzer()
        return {"message": "Voice analyzer initialized successfully!", "status": "ok"}
    except Exception as e:
        logger.error(f"Voice analyzer initialization failed: {str(e)}")
        return {"message": f"Voice analyzer initialization failed: {str(e)}", "status": "error"}

voice_analyzer = VoiceAnalyzer()
enhanced_analyzer = EnhancedAnalyzer()
data_exporter = DataExporter()
chart_generator = ChartGenerator()
pdf_generator = VoiceAnalysisPDFGenerator()

@app.post("/test-analyze-audio")
async def test_analyze_audio_endpoint(
    file: UploadFile = File(...),
    session_type: str = Form("practice"),
    topic: str = Form("general")
):
    """Test endpoint for audio analysis without authentication"""
    temp_file_path = None
    try:
        logger.info(f"Received TEST audio analysis request")
        logger.info(f"File: {file.filename}, Size: {file.size}, Content-Type: {file.content_type}")
        logger.info(f"Session type: {session_type}, Topic: {topic}")
        
        # Validate file
        if not file.filename:
            raise HTTPException(status_code=400, detail="No file provided")
        
        if file.size == 0:
            raise HTTPException(status_code=400, detail="Empty file provided")
        
        # Create temporary file
        with tempfile.NamedTemporaryFile(delete=False, suffix=".webm") as temp_file:
            content = await file.read()
            temp_file.write(content)
            temp_file_path = temp_file.name
            logger.info(f"Created temporary file: {temp_file_path}")

        # Analyze audio
        logger.info("Starting audio analysis...")
        analysis_results = await voice_analyzer.analyze_audio(temp_file_path)
        logger.info("Audio analysis completed successfully")

        return {"id": "test", **analysis_results}
        
    except HTTPException:
        # Re-raise HTTP exceptions
        raise
    except Exception as e:
        logger.error(f"Unexpected error in test_analyze_audio_endpoint: {str(e)}")
        logger.error(f"Exception type: {type(e).__name__}")
        import traceback
        logger.error(f"Traceback: {traceback.format_exc()}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")
    finally:
        # Clean up temporary file
        if temp_file_path and Path(temp_file_path).exists():
            try:
                Path(temp_file_path).unlink()
                logger.info(f"Cleaned up temporary file: {temp_file_path}")
            except Exception as cleanup_error:
                logger.warning(f"Failed to clean up temporary file {temp_file_path}: {str(cleanup_error)}")

@app.post("/analyze-audio")
async def analyze_audio_endpoint(
    request: Request,
    file: UploadFile = File(...),
    session_type: str = Form("practice"),
    topic: str = Form("general"),
    current_user: dict = Depends(get_current_user)
):
    temp_file_path = None
    try:
        # Log detailed request information
        logger.info("=== Incoming Request Details ===")
        logger.info(f"Method: {request.method}")
        logger.info(f"URL: {request.url}")
        logger.info(f"Headers: {dict(request.headers)}")
        logger.info(f"Form data: {await request.form()}")
        
        logger.info("=== File Details ===")
        logger.info(f"User: {current_user['username']}")
        logger.info(f"File name: {file.filename}")
        logger.info(f"File size: {file.size} bytes")
        logger.info(f"Content type: {file.content_type}")
        logger.info(f"Session type: {session_type}")
        logger.info(f"Topic: {topic}")
        
        # Validate file
        if not file.filename:
            raise HTTPException(status_code=400, detail="No file provided")
        
        if file.size == 0:
            raise HTTPException(status_code=400, detail="Empty file provided")
        
        # Create temporary file
        with tempfile.NamedTemporaryFile(delete=False, suffix=".webm") as temp_file:
            content = await file.read()
            temp_file.write(content)
            temp_file_path = temp_file.name
            logger.info(f"Created temporary file: {temp_file_path}")

        # Analyze audio
        logger.info("Starting audio analysis...")
        analysis_results = await voice_analyzer.analyze_audio(temp_file_path)
        logger.info("Audio analysis completed successfully")

        # Save to database
        try:
            user_id = ObjectId(current_user["_id"])
            recording_db = RecordingDB(
                user_id=user_id,
                file_path=temp_file_path,
                session_type=session_type,
                topic=topic,
                analysis_result=analysis_results,
                analysis_summary=json.dumps(analysis_results, indent=2)
            )
            recording_id = await create_recording(recording_db)
            logger.info(f"Recording saved to database with ID: {recording_id}")

            session_db = PracticeSessionDB(
                user_id=user_id,
                recording_id=ObjectId(recording_id),
                session_type=session_type,
                topic=topic,
                analysis_result=analysis_results,
            )
            await create_practice_session(session_db)
            logger.info("Practice session saved to database")

        except Exception as db_error:
            logger.error(f"Database error: {str(db_error)}")
            # Don't fail the request if database save fails
            logger.warning("Continuing with analysis results despite database error")

        return {"id": recording_id if 'recording_id' in locals() else "temp", **analysis_results}
        
    except HTTPException:
        # Re-raise HTTP exceptions
        raise
    except Exception as e:
        logger.error(f"Unexpected error in analyze_audio_endpoint: {str(e)}")
        logger.error(f"Exception type: {type(e).__name__}")
        import traceback
        logger.error(f"Traceback: {traceback.format_exc()}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")
    finally:
        # Clean up temporary file
        if temp_file_path and Path(temp_file_path).exists():
            try:
                Path(temp_file_path).unlink()
                logger.info(f"Cleaned up temporary file: {temp_file_path}")
            except Exception as cleanup_error:
                logger.warning(f"Failed to clean up temporary file {temp_file_path}: {str(cleanup_error)}")

def convert_objectid_to_str(obj):
    """Recursively convert ObjectId to string in a dictionary."""
    if isinstance(obj, ObjectId):
        return str(obj)
    elif isinstance(obj, dict):
        return {k: convert_objectid_to_str(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [convert_objectid_to_str(item) for item in obj]
    return obj

@app.get("/user/progress")
async def get_user_progress_endpoint(current_user: dict = Depends(get_current_user)):
    try:
        print("DEBUG: /user/progress endpoint called")
        # Handle _id as either str or ObjectId
        user_id = current_user.get("_id")
        if not isinstance(user_id, ObjectId):
            user_id = ObjectId(user_id)
        recordings_list = await get_user_recordings(user_id)

        if not recordings_list:
            return {"total_recordings": 0, "latest_metrics": None}

        clarity_scores = []
        confidence_scores = []
        speech_rates = []

        for r in recordings_list:
            analysis_result = r.get("analysis_result", {})
            audio_metrics = analysis_result.get("audio_metrics", {})

            clarity_data = audio_metrics.get("clarity", {})
            if "clarity_score" in clarity_data:
                clarity_scores.append(clarity_data["clarity_score"])

            emotion_data = audio_metrics.get("emotion", {})
            if "emotion_confidence" in emotion_data:
                confidence_scores.append(emotion_data["emotion_confidence"])

            rhythm_data = audio_metrics.get("rhythm", {})
            if "speech_rate" in rhythm_data:
                speech_rates.append(rhythm_data["speech_rate"])

        metrics_data = ProgressMetricsDB(
            user_id=user_id,
            clarity_trend=sum(clarity_scores) / len(clarity_scores) if clarity_scores else 0,
            confidence_trend=sum(confidence_scores) / len(confidence_scores) if confidence_scores else 0,
            speech_rate_trend=sum(speech_rates) / len(speech_rates) if speech_rates else 0,
            emotion_expression_score=sum(confidence_scores) / len(confidence_scores) if confidence_scores else 0,
            vocabulary_score=0.0,
            overall_improvement=calculate_overall_improvement(recordings_list),
            current_goals=[],
            completed_goals=[],
            badges_earned=[]
        )

        # Persist metrics but do not fail the request if DB write fails
        try:
            await update_progress_metrics(metrics_data)
        except Exception as persist_error:
            logger.warning(f"Failed to persist progress metrics: {persist_error}")

        # Convert ObjectId to string in the response
        response_data = {
            "total_recordings": len(recordings_list),
            "latest_metrics": convert_objectid_to_str(metrics_data.model_dump(by_alias=True))
        }
        return response_data
        
    except Exception as e:
        logger.error(f"Error in get_user_progress_endpoint: {str(e)}")
        logger.error(f"Exception type: {type(e).__name__}")
        import traceback
        logger.error(f"Traceback: {traceback.format_exc()}")
        raise HTTPException(status_code=500, detail=f"Error fetching progress data: {str(e)}")

@app.get("/practice-sessions")
async def get_practice_sessions_endpoint(current_user: dict = Depends(get_current_user)):
    try:
        sessions = await get_user_practice_sessions(ObjectId(current_user["_id"]))
        return convert_objectid_to_str(sessions)
    except Exception as e:
        logger.error(f"Error in get_practice_sessions_endpoint: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error fetching practice sessions: {str(e)}")

@app.get("/user/recordings")
async def get_user_recordings_endpoint(current_user: dict = Depends(get_current_user)):
    recordings_list = await get_user_recordings(ObjectId(current_user["_id"]))

    if not recordings_list:
        return {
            "message": "No recordings found",
            "recordings": []
        }

    formatted_recordings = [
        {
            "id": str(r["_id"]),
            "file_path": r["file_path"],
            "session_type": r["session_type"],
            "topic": r["topic"],
            "analysis_result": r["analysis_result"],
            "analysis_summary": r["analysis_summary"],
            "created_at": r["created_at"].isoformat()
        }
        for r in recordings_list
    ]

    return {
        "total_recordings": len(formatted_recordings),
        "recordings": formatted_recordings
    }

def calculate_overall_improvement(recordings: List[Dict]) -> float:
    if len(recordings) < 2:
        return 0.0

    first_result = recordings[-1].get("analysis_result", {})
    latest_result = recordings[0].get("analysis_result", {})

    first_audio_metrics = first_result.get("audio_metrics", {})
    latest_audio_metrics = latest_result.get("audio_metrics", {})

    first_clarity = first_audio_metrics.get("clarity", {}).get("clarity_score", 0.0)
    latest_clarity = latest_audio_metrics.get("clarity", {}).get("clarity_score", 0.0)

    first_confidence = first_audio_metrics.get("emotion", {}).get("emotion_confidence", 0.0)
    latest_confidence = latest_audio_metrics.get("emotion", {}).get("emotion_confidence", 0.0)

    first_speech_rate = first_audio_metrics.get("rhythm", {}).get("speech_rate", 0.0)
    latest_speech_rate = latest_audio_metrics.get("rhythm", {}).get("speech_rate", 0.0)

    clarity_improvement = latest_clarity - first_clarity
    confidence_improvement = latest_confidence - first_confidence
    rhythm_improvement = first_speech_rate - latest_speech_rate

    weighted_improvement = (
        clarity_improvement * 0.4 +
        confidence_improvement * 0.3 +
        rhythm_improvement * 0.3
    )

    return max(0.0, min(1.0, weighted_improvement + 0.5))

@app.get("/test-db")
async def test_db_endpoint():
    """Test database connection"""
    try:
        # Test database connection
        await init_db()
        return {"message": "Database connection successful!", "status": "ok"}
    except Exception as e:
        logger.error(f"Database connection failed: {str(e)}")
        return {"message": f"Database connection failed: {str(e)}", "status": "error"}

# Enhanced Analysis Endpoints
@app.post("/analyze-audio-enhanced")
async def analyze_audio_enhanced_endpoint(
    file: UploadFile = File(...),
    session_type: str = Form("practice"),
    topic: str = Form("general"),
    current_user: dict = Depends(get_current_user)
):
    """Enhanced audio analysis with language detection and voice cloning detection"""
    temp_file_path = None
    try:
        logger.info(f"Received enhanced audio analysis request from user: {current_user['username']}")
        
        # Validate file
        if not file.filename or file.size == 0:
            raise HTTPException(status_code=400, detail="Invalid file provided")
        
        # Create temporary file
        with tempfile.NamedTemporaryFile(delete=False, suffix=".webm") as temp_file:
            content = await file.read()
            temp_file.write(content)
            temp_file_path = temp_file.name
        
        # Perform enhanced analysis
        enhanced_results = enhanced_analyzer.analyze_audio_enhanced(temp_file_path)
        
        # Log language detection results for debugging
        language_detection = enhanced_results.get("language_detection", {})
        logger.info(f"Language detection result: {language_detection.get('detected_language', 'unknown')} "
                   f"({language_detection.get('language_name', 'Unknown')}) "
                   f"with confidence: {language_detection.get('confidence', 0):.2f}")
        
        if language_detection.get('detection_features'):
            features = language_detection['detection_features']
            logger.info(f"Detection features - Centroid: {features.get('spectral_centroid', 0):.2f}, "
                       f"Rolloff: {features.get('spectral_rolloff', 0):.2f}, "
                       f"ZCR: {features.get('zero_crossing_rate', 0):.4f}, "
                       f"MFCC_std: {features.get('mfcc_std', 0):.2f}")
            logger.info(f"Language scores - Telugu: {features.get('telugu_score', 0)}, "
                       f"Kannada: {features.get('kannada_score', 0)}, "
                       f"Hindi: {features.get('hindi_score', 0)}")
        
        # Perform regular voice analysis
        voice_analysis = await voice_analyzer.analyze_audio(temp_file_path)
        
        # Combine results
        combined_results = {
            **voice_analysis,
            "enhanced_features": enhanced_results
        }
        
        # Save to database with enhanced data
        try:
            user_id = ObjectId(current_user["_id"])
            recording_db = RecordingDB(
                user_id=user_id,
                file_path=temp_file_path,
                session_type=session_type,
                topic=topic,
                analysis_result=combined_results,
                analysis_summary=json.dumps(combined_results, indent=2),
                detected_language=enhanced_results.get("language_detection", {}).get("detected_language"),
                voice_cloning_score=enhanced_results.get("voice_cloning_detection", {}).get("confidence_score"),
                transcription=enhanced_results.get("language_detection", {}).get("transcription")
            )
            recording_id = await create_recording(recording_db)
            
            session_db = PracticeSessionDB(
                user_id=user_id,
                recording_id=ObjectId(recording_id),
                session_type=session_type,
                topic=topic,
                analysis_result=combined_results,
                language=enhanced_results.get("language_detection", {}).get("detected_language"),
                voice_cloning_detected="ai" if enhanced_results.get("voice_cloning_detection", {}).get("is_ai_generated") else "human"
            )
            await create_practice_session(session_db)
            
        except Exception as db_error:
            logger.error(f"Database error: {str(db_error)}")
        
        return {
            "id": recording_id if 'recording_id' in locals() else "temp",
            **combined_results
        }
        
    except Exception as e:
        logger.error(f"Enhanced analysis error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Enhanced analysis failed: {str(e)}")
    finally:
        if temp_file_path and Path(temp_file_path).exists():
            try:
                Path(temp_file_path).unlink()
            except Exception:
                pass

@app.post("/export-data")
async def export_data_endpoint(
    export_request: ExportRequest,
    current_user: dict = Depends(get_current_user)
):
    """Export analysis data to PDF or CSV format"""
    try:
        user_id = ObjectId(current_user["_id"])
        recordings = await get_user_recordings(user_id)
        
        if not recordings:
            raise HTTPException(status_code=404, detail="No recordings found to export")
        
        if export_request.format.lower() == "csv":
            csv_content = data_exporter.export_to_csv(recordings, export_request.model_dump())
            
            # Generate filename
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"vocal_iq_analysis_{timestamp}.csv"
            
            return StreamingResponse(
                io.StringIO(csv_content),
                media_type="text/csv",
                headers={"Content-Disposition": f"attachment; filename={filename}"}
            )
        
        elif export_request.format.lower() == "pdf":
            pdf_content = data_exporter.export_to_pdf(recordings, current_user, export_request.model_dump())
            
            # Generate filename
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"vocal_iq_analysis_{timestamp}.pdf"
            
            return StreamingResponse(
                io.BytesIO(pdf_content),
                media_type="application/pdf",
                headers={"Content-Disposition": f"attachment; filename={filename}"}
            )
        
        else:
            raise HTTPException(status_code=400, detail="Unsupported export format. Use 'csv' or 'pdf'")
            
    except Exception as e:
        logger.error(f"Export error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Export failed: {str(e)}")

@app.get("/debug-charts")
async def debug_charts_endpoint(current_user: dict = Depends(get_current_user)):
    """Debug endpoint for chart generation"""
    try:
        user_id = ObjectId(current_user["_id"])
        recordings = await get_user_recordings(user_id)
        
        debug_info = {
            "user_id": str(user_id),
            "username": current_user["username"],
            "recordings_count": len(recordings) if recordings else 0,
            "has_recordings": bool(recordings),
            "chart_generator_initialized": hasattr(chart_generator, 'generate_comparison_chart')
        }
        
        if recordings:
            # Test chart generation
            try:
                chart_data = chart_generator.generate_comparison_chart(recordings)
                debug_info["chart_generation_success"] = True
                debug_info["chart_data_size"] = len(chart_data)
            except Exception as chart_error:
                debug_info["chart_generation_success"] = False
                debug_info["chart_error"] = str(chart_error)
        
        return debug_info
        
    except Exception as e:
        logger.error(f"Debug charts error: {str(e)}")
        return {"error": str(e), "traceback": str(e.__traceback__)}

@app.get("/comparison-charts")
async def get_comparison_charts_endpoint(current_user: dict = Depends(get_current_user)):
    """Generate comparison charts for user's recordings"""
    try:
        user_id = ObjectId(current_user["_id"])
        recordings = await get_user_recordings(user_id)
        
        if not recordings:
            # Return a simple text response instead of 404
            return StreamingResponse(
                io.BytesIO(b"No recordings found. Please record some audio first."),
                media_type="text/plain",
                headers={"Content-Disposition": "inline; filename=no_data.txt"}
            )
        
        # Generate comparison chart
        chart_data = chart_generator.generate_comparison_chart(recordings)
        
        if not chart_data:
            # Return a simple text response instead of 500
            return StreamingResponse(
                io.BytesIO(b"Failed to generate chart. Please try again."),
                media_type="text/plain",
                headers={"Content-Disposition": "inline; filename=error.txt"}
            )
        
        return StreamingResponse(
            io.BytesIO(chart_data),
            media_type="text/plain",  # Changed from image/png to text/plain
            headers={"Content-Disposition": "inline; filename=comparison_chart.txt"}
        )
        
    except Exception as e:
        logger.error(f"Chart generation error: {str(e)}")
        # Return error response instead of raising exception
        return StreamingResponse(
            io.BytesIO(f"Chart generation failed: {str(e)}".encode()),
            media_type="text/plain",
            headers={"Content-Disposition": "inline; filename=error.txt"}
        )

@app.get("/language-charts")
async def get_language_charts_endpoint(current_user: dict = Depends(get_current_user)):
    """Generate language distribution charts"""
    try:
        user_id = ObjectId(current_user["_id"])
        recordings = await get_user_recordings(user_id)
        
        if not recordings:
            # Return a simple text response instead of 404
            return StreamingResponse(
                io.BytesIO(b"No recordings found. Please record some audio first."),
                media_type="text/plain",
                headers={"Content-Disposition": "inline; filename=no_data.txt"}
            )
        
        # Generate language chart
        chart_data = chart_generator.generate_language_chart(recordings)
        
        if not chart_data:
            # Return a simple text response instead of 500
            return StreamingResponse(
                io.BytesIO(b"Failed to generate language chart. Please try again."),
                media_type="text/plain",
                headers={"Content-Disposition": "inline; filename=error.txt"}
            )
        
        return StreamingResponse(
            io.BytesIO(chart_data),
            media_type="text/plain",  # Changed from image/png to text/plain
            headers={"Content-Disposition": "inline; filename=language_chart.txt"}
        )
        
    except Exception as e:
        logger.error(f"Language chart generation error: {str(e)}")
        # Return error response instead of raising exception
        return StreamingResponse(
            io.BytesIO(f"Language chart generation failed: {str(e)}".encode()),
            media_type="text/plain",
            headers={"Content-Disposition": "inline; filename=error.txt"}
        )

@app.get("/supported-languages")
async def get_supported_languages_endpoint():
    """Get list of supported languages for analysis"""
    try:
        languages = {
            'en': 'English',
            'hi': 'Hindi',
            'kn': 'Kannada',
            'te': 'Telugu'
        }
        
        return {
            "supported_languages": languages,
            "total_languages": len(languages),
            "default_language": "en"
        }
        
    except Exception as e:
        logger.error(f"Language list error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to get language list: {str(e)}")

@app.get("/favicon.ico")
async def favicon():
    """Return empty favicon to prevent 404 errors"""
    from fastapi.responses import Response
    return Response(status_code=204)

@app.post("/export-analysis-pdf")
async def export_analysis_pdf_endpoint(
    analysis_data: dict,
    current_user: dict = Depends(get_current_user)
):
    """Export voice analysis results as PDF"""
    try:
        logger.info(f"Generating PDF for user: {current_user['username']}")
        
        # Generate PDF
        pdf_content = pdf_generator.generate_voice_analysis_pdf(analysis_data, current_user)
        
        # Generate filename
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"voice_analysis_{current_user['username']}_{timestamp}.pdf"
        
        return StreamingResponse(
            io.BytesIO(pdf_content),
            media_type="application/pdf",
            headers={"Content-Disposition": f"attachment; filename={filename}"}
        )
        
    except Exception as e:
        logger.error(f"PDF export error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"PDF export failed: {str(e)}")

@app.get("/export-analysis-pdf/{recording_id}")
async def export_recording_pdf_endpoint(
    recording_id: str,
    current_user: dict = Depends(get_current_user)
):
    """Export specific recording analysis as PDF"""
    try:
        logger.info(f"Generating PDF for recording {recording_id} by user: {current_user['username']}")
        
        # Get recording data
        user_id = ObjectId(current_user["_id"])
        recordings = await get_user_recordings(user_id)
        
        # Find the specific recording
        target_recording = None
        for recording in recordings:
            if str(recording["_id"]) == recording_id:
                target_recording = recording
                break
        
        if not target_recording:
            raise HTTPException(status_code=404, detail="Recording not found")
        
        # Prepare analysis data
        analysis_data = {
            "audio_metrics": target_recording.get("analysis_result", {}).get("audio_metrics", {}),
            "transcription": target_recording.get("analysis_result", {}).get("transcription", {}),
            "recommendations": target_recording.get("analysis_result", {}).get("recommendations", {}),
            "metadata": {
                "session_type": target_recording.get("session_type", "practice"),
                "topic": target_recording.get("topic", "general"),
                "duration": target_recording.get("analysis_result", {}).get("audio_metrics", {}).get("duration", 0),
                "created_at": target_recording.get("created_at", datetime.now())
            }
        }
        
        # Generate PDF
        pdf_content = pdf_generator.generate_voice_analysis_pdf(analysis_data, current_user)
        
        # Generate filename
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"voice_analysis_{current_user['username']}_{recording_id}_{timestamp}.pdf"
        
        return StreamingResponse(
            io.BytesIO(pdf_content),
            media_type="application/pdf",
            headers={"Content-Disposition": f"attachment; filename={filename}"}
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Recording PDF export error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"PDF export failed: {str(e)}")

@app.get("/debug-language-detection")
async def debug_language_detection_endpoint(current_user: dict = Depends(get_current_user)):
    """Debug endpoint for language detection"""
    try:
        user_id = ObjectId(current_user["_id"])
        recordings = await get_user_recordings(user_id)
        
        debug_info = {
            "user_id": str(user_id),
            "username": current_user["username"],
            "recordings_count": len(recordings) if recordings else 0,
            "enhanced_analyzer_initialized": hasattr(enhanced_analyzer, 'language_detector'),
            "transcriber_available": enhanced_analyzer.language_detector.transcriber is not None,
            "supported_languages": enhanced_analyzer.language_detector.supported_languages if hasattr(enhanced_analyzer, 'language_detector') else {},
            "detection_method": "Dual (Feature-based + Transcription)",
            "feature_thresholds": {
                "english_centroid_range": "1500-3500 Hz",
                "english_rolloff_range": "2500-6000 Hz", 
                "english_zcr_range": "0.03-0.20",
                "kannada_centroid_range": "1200-1800 Hz",
                "kannada_rolloff_range": "2000-3200 Hz", 
                "kannada_zcr_range": "0.03-0.10",
                "telugu_centroid_range": "1600-2100 Hz",
                "telugu_rolloff_range": "3200-4200 Hz",
                "telugu_zcr_range": "0.06-0.13"
            }
        }
        
        if recordings:
            # Get the most recent recording
            latest_recording = max(recordings, key=lambda x: x.get('created_at', datetime.now()))
            debug_info["latest_recording"] = {
                "id": str(latest_recording.get('_id', '')),
                "created_at": latest_recording.get('created_at', ''),
                "detected_language": latest_recording.get('detected_language', ''),
                "language_confidence": latest_recording.get('language_confidence', 0),
                "transcription": latest_recording.get('transcription', '')[:100] + "..." if latest_recording.get('transcription') else ""
            }
        
        return debug_info
        
    except Exception as e:
        logger.error(f"Debug language detection error: {str(e)}")
        return {"error": str(e)}

@app.get("/debug-ai-detection")
async def debug_ai_detection_endpoint(current_user: dict = Depends(get_current_user)):
    """Debug endpoint for AI voice detection"""
    try:
        user_id = ObjectId(current_user["_id"])
        recordings = await get_user_recordings(user_id)
        
        debug_info = {
            "user_id": str(user_id),
            "username": current_user["username"],
            "recordings_count": len(recordings) if recordings else 0,
            "voice_cloning_detector_initialized": hasattr(enhanced_analyzer, 'voice_cloning_detector'),
            "model_loaded": enhanced_analyzer.voice_cloning_detector.model is not None,
            "scaler_loaded": enhanced_analyzer.voice_cloning_detector.scaler is not None,
            "detection_method": "Enhanced Spectral Analysis",
            "ai_detection_thresholds": {
                "ai_threshold": "0.5 (was 0.7)",
                "high_risk": "> 0.75",
                "medium_risk": "0.55-0.75",
                "low_risk": "< 0.55"
            },
            "feature_analysis": {
                "spectral_consistency": "AI voices have very low variation",
                "mfcc_variation": "AI voices have low MFCC variation",
                "zcr_consistency": "AI voices have unnatural ZCR patterns",
                "rms_consistency": "AI voices have very consistent energy",
                "perfect_patterns": "Multiple indicators together = likely AI"
            }
        }
        
        if recordings:
            # Get the most recent recording
            latest_recording = max(recordings, key=lambda x: x.get('created_at', datetime.now()))
            debug_info["latest_recording"] = {
                "id": str(latest_recording.get('_id', '')),
                "created_at": latest_recording.get('created_at', ''),
                "is_ai_generated": latest_recording.get('is_ai_generated', False),
                "ai_confidence": latest_recording.get('ai_confidence', 0),
                "ai_risk_level": latest_recording.get('ai_risk_level', 'low')
            }
        
        return debug_info
        
    except Exception as e:
        logger.error(f"Debug AI detection error: {str(e)}")
        return {"error": str(e)}

@app.post("/test-language-detection")
async def test_language_detection_endpoint(
    file: UploadFile = File(...),
    current_user: dict = Depends(get_current_user)
):
    """Test endpoint for language detection with detailed debugging"""
    temp_file_path = None
    try:
        logger.info(f"Testing language detection for file: {file.filename}")
        
        # Save uploaded file
        temp_file_path = tempfile.mktemp(suffix='.webm')
        with open(temp_file_path, 'wb') as buffer:
            content = await file.read()
            buffer.write(content)
        
        # Test language detection
        language_result = enhanced_analyzer.language_detector.detect_language_from_audio(temp_file_path)
        
        logger.info(f"Language detection result: {language_result}")
        
        return {
            "message": "Language detection test completed",
            "detected_language": language_result["detected_language"],
            "language_name": language_result["language_name"],
            "confidence": language_result["confidence"],
            "transcription": language_result.get("transcription", ""),
            "detection_features": language_result.get("detection_features", {}),
            "debug_info": {
                "file_size": len(content),
                "file_name": file.filename,
                "detection_method": "enhanced_analyzer"
            }
        }
        
    except Exception as e:
        logger.error(f"Language detection test error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Language detection test failed: {str(e)}")
    finally:
        # Clean up temporary file
        if temp_file_path and os.path.exists(temp_file_path):
            try:
                os.unlink(temp_file_path)
            except Exception as e:
                logger.warning(f"Failed to delete temp file {temp_file_path}: {str(e)}")

@app.post("/api/analyze-audio")
async def api_analyze_audio_endpoint(
    file: UploadFile = File(...),
    session_type: str = Form("practice"),
    topic: str = Form("general"),
    current_user: dict = Depends(get_current_user)
):
    """
    API endpoint for audio file upload and analysis.
    This is an alias for /analyze-audio to match frontend expectations.
    """
    try:
        logger.info(f"Received API audio analysis request from user: {current_user['username']}")
        # Simply forward the request to the existing analyze_audio_endpoint
        return await analyze_audio_endpoint(
            file=file,
            session_type=session_type,
            topic=topic,
            current_user=current_user
        )
    except HTTPException as he:
        # Re-raise HTTP exceptions
        raise
    except Exception as e:
        logger.error(f"Error in api_analyze_audio_endpoint: {str(e)}")
        logger.error(f"Exception type: {type(e).__name__}")
        import traceback
        logger.error(f"Traceback: {traceback.format_exc()}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)
