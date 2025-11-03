from typing import Optional, Dict, List
from datetime import datetime
from pydantic import BaseModel, Field
from bson import ObjectId

class PyObjectId(ObjectId):
    @classmethod
    def __get_validators__(cls):
        yield cls.validate

    @classmethod
    def validate(cls, v, field_info):
        if not ObjectId.is_valid(v):
            raise ValueError("Invalid objectid")
        return ObjectId(v)

    @classmethod
    def __get_pydantic_json_schema__(cls, core_schema, handler):
        json_schema = handler(core_schema)
        json_schema.update(
            type="string",
            examples=["5f9f1b9b9c9d1c0b8c8b8c8b"],
        )
        return json_schema

class UserDB(BaseModel):
    id: Optional[PyObjectId] = Field(default=None, alias="_id")
    username: str
    email: str
    hashed_password: str
    created_at: datetime = Field(default_factory=datetime.utcnow)
    preferred_language: str = Field(default="en")

    class Config:
        json_encoders = {ObjectId: str}
        arbitrary_types_allowed = True
        
class RecordingDB(BaseModel):
    id: Optional[PyObjectId] = Field(default=None, alias="_id")
    user_id: PyObjectId
    file_path: str
    session_type: str
    topic: str
    analysis_result: dict
    analysis_summary: str
    created_at: datetime = Field(default_factory=datetime.utcnow)
    detected_language: Optional[str] = None
    voice_cloning_score: Optional[float] = None
    transcription: Optional[str] = None

    class Config:
        json_encoders = {ObjectId: str}
        arbitrary_types_allowed = True

class PracticeSessionDB(BaseModel):
    id: Optional[PyObjectId] = Field(default=None, alias="_id")
    user_id: PyObjectId
    recording_id: PyObjectId
    session_type: str
    topic: str
    analysis_result: dict
    created_at: datetime = Field(default_factory=datetime.utcnow)
    language: Optional[str] = None
    voice_cloning_detected: str = Field(default="human")

    class Config:
        json_encoders = {ObjectId: str}
        arbitrary_types_allowed = True

class ProgressMetricsDB(BaseModel):
    id: Optional[PyObjectId] = Field(default=None, alias="_id")
    user_id: PyObjectId
    metric_date: datetime = Field(default_factory=datetime.utcnow)
    clarity_trend: float
    confidence_trend: float
    speech_rate_trend: float
    emotion_expression_score: float
    vocabulary_score: float
    overall_improvement: float
    current_goals: List[str]
    completed_goals: List[str]
    badges_earned: List[dict]
    language_metrics: Optional[Dict[str, dict]] = None

    class Config:
        json_encoders = {ObjectId: str}
        arbitrary_types_allowed = True

# New models for enhanced features
class LanguageDetectionResult(BaseModel):
    detected_language: str
    confidence: float
    language_name: str
    language_code: str

class VoiceCloningDetectionResult(BaseModel):
    is_ai_generated: bool
    confidence_score: float
    detection_method: str
    risk_level: str  # low, medium, high

class ExportRequest(BaseModel):
    format: str  # "pdf" or "csv"
    date_range: Optional[Dict[str, str]] = None
    include_transcriptions: bool = True
    include_voice_cloning: bool = True 