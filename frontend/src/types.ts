export interface PitchMetrics {
  average: number;
  variation: number;
  range: number;
  stability_score: number;
}

export interface RhythmMetrics {
  speech_rate: number;
  fluency_score: number;
  pause_pattern: number;
  rhythm_consistency: number;
}

export interface ClarityMetrics {
  clarity_score: number;
  pronunciation_accuracy: number;
  articulation_score: number;
}

export interface EmotionMetrics {
  dominant_emotion: string;
  emotion_confidence: number;
  emotion_distribution: Record<string, number>;
}

export interface AudioMetrics {
  duration: number;
  pitch: PitchMetrics;
  rhythm: RhythmMetrics;
  clarity: ClarityMetrics;
  emotion: EmotionMetrics;
}

// Enhanced Features Types
export interface LanguageDetection {
  detected_language: string;
  confidence: number;
  language_name: string;
  language_code: string;
  transcription: string;
}

export interface VoiceCloningDetection {
  is_ai_generated: boolean;
  confidence_score: number;
  detection_method: string;
  risk_level: string;
}

export interface EnhancedFeatures {
  language_detection: LanguageDetection;
  voice_cloning_detection: VoiceCloningDetection;
  enhanced_analysis: {
    multilingual_support: boolean;
    ai_detection_enabled: boolean;
    analysis_timestamp: string;
  };
}

export interface VoiceAnalysis {
  id?: string;
  user_id?: string;
  session_id?: string;
  created_at?: string;
  audio_metrics: {
    duration: number;
    confidence_score: number;
    emotion: {
      dominant_emotion: string;
      emotion_confidence: number;
      emotion_scores: {
        happy: number;
        sad: number;
        angry: number;
        neutral: number;
        excited: number;
        calm: number;
      };
      emotional_range: string;
      emotional_stability: number;
      pitch_stability?: number;
      energy_stability?: number;
      avg_pitch?: number;
      avg_energy?: number;
    };
    clarity: {
      clarity_score: number;
      pronunciation_score: number;
      articulation_rate: number;
      speech_errors: string[];
      enunciation_quality: number;
      voice_projection: number;
      overall_clarity?: number;
      mfcc_variation?: number;
      spectral_contrast?: number;
    };
    rhythm: {
      speech_rate: number;
      pause_ratio: number;
      average_pause_duration: number;
      total_speaking_time: number;
      rhythm_consistency: number;
      stress_pattern: string;
      tempo?: number;
      speaking_tempo?: number;
      energy_variation?: number;
    };
    pitch: {
      average_pitch: number;
      pitch_variation: number;
      pitch_range: {
        min: number;
        max: number;
      };
      pitch_stability: number;
      pitch_contour: number;
      range_semitones?: number;
    };
    fluency: {
      fluency_score: number;
      filler_words: string[];
      repetitions: number;
      hesitations: number;
      smoothness: number;
      pitch_jitter?: number;
      energy_smoothness?: number;
      pitch_smoothness?: number;
      mfcc_variation?: number;
      fluency_issues?: string[];
    };
  };
  transcription: {
    full_text: string;
    word_count: number;
    transcription_confidence: number;
  };
  recommendations: {
    key_points: string[];
    improvement_areas: string[];
    strengths: string[];
    practice_suggestions: string[];
  };
  metadata: {
    session_type: string;
    topic: string;
    duration: number;
    file_path: string;
    analysis_version?: string;
    model_confidence?: number;
  };
  // Enhanced features
  enhanced_features?: EnhancedFeatures;
}

export interface AudioRecorderProps {
  onAnalysisComplete: (analysis: VoiceAnalysis) => void;
  sessionType?: string;
  topic?: string;
}

export interface AnalysisDisplayProps {
  analysis: VoiceAnalysis | null;
}

export interface User {
  id: string;
  username: string;
  email: string;
  created_at: string;
  preferred_language?: string;
}

export interface PracticeSession {
  id: string;
  user_id: string;
  session_type: string;
  topic: string;
  created_at: string;
  completed_at: string | null;
  analysis_id: string | null;
  goals: string[];
  notes: string;
  average_clarity: number;
  average_confidence: number;
  dominant_emotion: string;
  language?: string;
  voice_cloning_detected?: string;
}

export interface ProgressMetrics {
  user_id: string;
  metric_date: string;
  clarity_trend: number;
  confidence_trend: number;
  speech_rate_trend: number;
  emotion_expression_score: number;
  vocabulary_score: number;
  overall_improvement: number;
  current_goals: string[];
  completed_goals: string[];
  badges_earned: Array<{
    id: string;
    name: string;
    description: string;
    earned_date: string;
  }>;
  language_metrics?: Record<string, any>;
}

export interface UserProgress {
  total_recordings: number;
  latest_metrics: ProgressMetrics;
}

export interface ApiError {
  status: number;
  message: string;
}

export interface AuthResponse {
  access_token: string;
  token_type: string;
}

export interface LoginCredentials {
  username: string;
  password: string;
}

export interface RegisterData {
  username: string;
  email: string;
  password: string;
}

export interface AuthState {
  user: User | null;
  isAuthenticated: boolean;
  token: string | null;
}

export interface AuthContextType extends AuthState {
  login: (email: string, password: string) => Promise<void>;
  logout: () => void;
  register: (username: string, email: string, password: string) => Promise<void>;
}

// Export Request Types
export interface ExportRequest {
  format: 'csv' | 'pdf';
  date_range?: {
    start: string;
    end: string;
  };
  include_transcriptions: boolean;
  include_voice_cloning: boolean;
}

// Supported Languages
export interface SupportedLanguages {
  supported_languages: Record<string, string>;
  total_languages: number;
  default_language: string;
} 