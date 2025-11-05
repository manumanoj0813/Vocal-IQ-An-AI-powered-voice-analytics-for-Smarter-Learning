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
pending_otps = database.pending_otps

# Create indexes
async def init_db():
    try:
        # Drop any existing email indexes to avoid conflicts
        # Try dropping by common auto-generated names first
        for index_name in ["email_1", "email_-1"]:
            try:
                await users.drop_index(index_name)
                logger.info(f"Dropped existing index: {index_name}")
            except Exception:
                pass  # Index doesn't exist or already dropped
        
        # Also check and drop any email indexes by listing
        try:
            existing_indexes = await users.list_indexes().to_list(length=100)
            for index in existing_indexes:
                index_name = index.get("name")
                if index_name == "_id_":
                    continue
                
                index_key = index.get("key", {})
                # Check if index is on email field (handle both dict and list formats)
                is_email_index = False
                if isinstance(index_key, dict):
                    is_email_index = "email" in index_key
                elif isinstance(index_key, list):
                    is_email_index = any(key[0] == "email" for key in index_key if isinstance(key, (list, tuple)))
                
                # Drop any index on email field
                if is_email_index:
                    try:
                        await users.drop_index(index_name)
                        logger.info(f"Dropped existing email index: {index_name}")
                    except Exception as e:
                        logger.warning(f"Could not drop index {index_name}: {str(e)}")
        except Exception as e:
            logger.warning(f"Could not list indexes: {str(e)}")
        
        # Create unique indexes
        await users.create_index("username", unique=True)
        # Create non-unique email index (allows multiple accounts per email)
        # Use explicit name to avoid conflicts
        await users.create_index("email", name="email_index")
        await pending_otps.create_index("email", unique=True)
        
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
        "is_admin": user.get("is_admin", False),
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

async def set_user_otp(username_or_email: str, code: str, expires_at: datetime):
    query = {"$or": [{"username": username_or_email}, {"email": username_or_email}]}
    await users.update_one(query, {"$set": {"otp_code": code, "otp_expires": expires_at}})

async def get_user_by_username_or_email(identifier: str) -> Optional[dict]:
    user = await users.find_one({"$or": [{"username": identifier}, {"email": identifier}]})
    if user:
        return user_helper(user)
    return None

async def clear_user_otp(username: str):
    await users.update_one({"username": username}, {"$unset": {"otp_code": "", "otp_expires": ""}})

async def set_password_reset_token(email: str, token: str, expires_at: datetime):
    await users.update_one({"email": email}, {"$set": {"reset_token": token, "reset_expires": expires_at}})

async def reset_password_with_token(token: str, new_hashed_password: str) -> bool:
    user = await users.find_one({"reset_token": token})
    if not user:
        return False
    if user.get("reset_expires") and user["reset_expires"] < datetime.utcnow():
        return False
    await users.update_one({"_id": user["_id"]}, {"$set": {"hashed_password": new_hashed_password}, "$unset": {"reset_token": "", "reset_expires": ""}})
    return True

# Registration OTP helpers
async def set_registration_otp(email: str, code: str, expires_at: datetime):
    await pending_otps.update_one(
        {"email": email},
        {"$set": {"email": email, "code": code, "expires": expires_at, "purpose": "register"}},
        upsert=True
    )

async def get_and_clear_registration_otp(email: str) -> Optional[dict]:
    doc = await pending_otps.find_one({"email": email})
    if doc:
        await pending_otps.delete_one({"_id": doc["_id"]})
    return doc

async def create_recording(recording_data: RecordingDB) -> str:
    recording_dict = recording_data.model_dump(by_alias=True, exclude=["id"])
    result = await recordings.insert_one(recording_dict)
    return str(result.inserted_id)

async def get_user_recordings(user_id: str) -> List[dict]:
    user_recordings_list = []
    oid = user_id if isinstance(user_id, ObjectId) else ObjectId(user_id)
    async for recording in recordings.find({"user_id": oid}).sort("created_at", -1):
        user_recordings_list.append(recording)
    return user_recordings_list

async def create_practice_session(session_data: PracticeSessionDB) -> str:
    session_dict = session_data.model_dump(by_alias=True, exclude=["id"])
    result = await practice_sessions.insert_one(session_dict)
    return str(result.inserted_id)

async def get_user_practice_sessions(user_id: str) -> List[dict]:
    sessions = []
    oid = user_id if isinstance(user_id, ObjectId) else ObjectId(user_id)
    async for session in practice_sessions.find({"user_id": oid}).sort("created_at", -1):
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
    oid = user_id if isinstance(user_id, ObjectId) else ObjectId(user_id)
    progress = await progress_metrics.find_one({"user_id": oid})
    return progress

# Admin utilities
async def list_users(limit: int = 100) -> List[dict]:
    results = []
    cursor = users.find({}).sort("created_at", -1).limit(limit)
    async for u in cursor:
        results.append(user_helper(u))
    return results

async def list_recent_recordings(limit: int = 100) -> List[dict]:
    results = []
    cursor = recordings.find({}).sort("created_at", -1).limit(limit)
    async for r in cursor:
        results.append(r)
    return results

async def get_usage_metrics() -> Dict[str, int]:
    total_users = await users.count_documents({})
    total_recordings = await recordings.count_documents({})
    from datetime import datetime, timedelta
    since = datetime.utcnow() - timedelta(days=7)
    last7_recordings = await recordings.count_documents({"created_at": {"$gte": since}})
    return {
        "total_users": total_users,
        "total_recordings": total_recordings,
        "recordings_last_7_days": last7_recordings,
    }