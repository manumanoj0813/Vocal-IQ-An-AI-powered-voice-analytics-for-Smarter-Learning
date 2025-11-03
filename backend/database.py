import motor.motor_asyncio
from bson import ObjectId
from typing import List, Dict, Optional
from models import UserDB, RecordingDB, PracticeSessionDB, ProgressMetricsDB
from datetime import datetime
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# MongoDB connection URL
MONGODB_URL = "mongodb://localhost:27017"
DATABASE_NAME = "vocal_iq_db"

try:
    # Create async MongoDB client
    client = motor.motor_asyncio.AsyncIOMotorClient(MONGODB_URL)
    database = client[DATABASE_NAME]
    logger.info("Successfully connected to MongoDB")
except Exception as e:
    logger.error(f"Failed to connect to MongoDB: {str(e)}")
    raise

# Collections
users = database.users
recordings = database.recordings
practice_sessions = database.practice_sessions
progress_metrics = database.progress_metrics

# Create indexes
async def init_db():
    try:
        # Create unique indexes
        await users.create_index("username", unique=True)
        await users.create_index("email", unique=True)
        
        # Create compound indexes
        await recordings.create_index([("user_id", 1), ("created_at", -1)])
        await practice_sessions.create_index([("user_id", 1), ("start_time", -1)])
        await progress_metrics.create_index([("user_id", 1), ("metric_date", -1)])
        
        logger.info("Database indexes created successfully")
    except Exception as e:
        logger.error(f"Failed to create database indexes: {str(e)}")
        raise

# Helper functions
def user_helper(user) -> dict:
    return {
        "_id": user["_id"],
        "username": user["username"],
        "email": user["email"],
        "hashed_password": user["hashed_password"],
        "created_at": user["created_at"],
    }

# Database operations
async def create_user(user_data: UserDB) -> str:
    user_dict = user_data.model_dump(by_alias=True, exclude=["id"])
    result = await users.insert_one(user_dict)
    return str(result.inserted_id)

async def get_user_by_username(username: str) -> Optional[dict]:
    user = await users.find_one({"username": username})
    if user:
        return user_helper(user)
    return None

async def get_user_by_email(email: str) -> Optional[dict]:
    user = await users.find_one({"email": email})
    if user:
        return user_helper(user)
    return None

async def create_recording(recording_data: RecordingDB) -> str:
    recording_dict = recording_data.model_dump(by_alias=True, exclude=["id"])
    result = await recordings.insert_one(recording_dict)
    return str(result.inserted_id)

async def get_user_recordings(user_id: str) -> List[dict]:
    user_recordings_list = []
    async for recording in recordings.find({"user_id": ObjectId(user_id)}).sort("created_at", -1):
        user_recordings_list.append(recording)
    return user_recordings_list

async def create_practice_session(session_data: PracticeSessionDB) -> str:
    session_dict = session_data.model_dump(by_alias=True, exclude=["id"])
    result = await practice_sessions.insert_one(session_dict)
    return str(result.inserted_id)

async def get_user_practice_sessions(user_id: str) -> List[dict]:
    sessions = []
    async for session in practice_sessions.find({"user_id": ObjectId(user_id)}).sort("created_at", -1):
        sessions.append(session)
    return sessions

async def update_progress_metrics(metrics_data: ProgressMetricsDB):
    metrics_dict = metrics_data.model_dump(by_alias=True, exclude=["id"])
    await progress_metrics.update_one(
        {"user_id": metrics_data.user_id},
        {"$set": metrics_dict},
        upsert=True
    )

async def get_user_progress(user_id: str) -> Optional[dict]:
    progress = await progress_metrics.find_one({"user_id": ObjectId(user_id)})
    return progress 