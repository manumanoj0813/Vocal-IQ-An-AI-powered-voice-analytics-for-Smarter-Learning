import numpy as np
import librosa
import logging
from typing import Dict
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import StandardScaler
import joblib
import os

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class LanguageDetector:
    """Detects the language of speech using multiple methods"""
    
    def __init__(self):
        self.supported_languages = {
            'en': 'English',
            'hi': 'Hindi',
            'kn': 'Kannada',
            'te': 'Telugu'
        }
        
        # Initialize speech-to-text for transcription
        try:
            from transformers import pipeline
            self.transcriber = pipeline("automatic-speech-recognition", model="openai/whisper-base")
            logger.info("Speech-to-text model loaded successfully")
        except Exception as e:
            logger.warning(f"Could not load speech-to-text model: {e}")
            self.transcriber = None
    
    def detect_language_from_audio(self, audio_path: str) -> Dict:
        """Detect language from audio file using transcription and language detection"""
        try:
            logger.info(f"Starting language detection for: {audio_path}")
            
            # Always try feature-based detection first (more reliable)
            feature_result = self._detect_language_from_features(audio_path)
            
            # Try transcription-based detection as secondary method
            transcription_result = None
            if self.transcriber:
                try:
                    logger.info("Attempting transcription-based language detection")
                    transcription = self.transcriber(audio_path)
                    text = transcription["text"]
                    
                    if text and len(text.strip()) > 5:  # Lower threshold for text length
                        try:
                            from langdetect import detect
                            detected_lang = detect(text)
                            confidence = 0.7  # Moderate confidence for transcription
                            
                            # Special handling for Indian languages
                            if detected_lang in ['en', 'unknown'] and len(text.strip()) > 5:
                                # Check for Indian language characteristics
                                if any(char in text for char in ['ಅ', 'ಆ', 'ಇ', 'ಈ', 'ಉ', 'ಊ', 'ಋ', 'ಎ', 'ಏ', 'ಐ', 'ಒ', 'ಓ', 'ಔ']):
                                    detected_lang = "kn"  # Kannada
                                    confidence = 0.8
                                elif any(char in text for char in ['అ', 'ఆ', 'ఇ', 'ఈ', 'ఉ', 'ఊ', 'ఋ', 'ఎ', 'ఏ', 'ఐ', 'ఒ', 'ఓ', 'ఔ']):
                                    detected_lang = "te"  # Telugu
                                    confidence = 0.8
                                elif any(char in text for char in ['अ', 'आ', 'इ', 'ई', 'उ', 'ऊ', 'ऋ', 'ए', 'ऐ', 'ओ', 'औ']):
                                    detected_lang = "hi"  # Hindi
                                    confidence = 0.8
                            
                            transcription_result = {
                                "detected_language": detected_lang,
                                "confidence": confidence,
                                "language_name": self.supported_languages.get(detected_lang, "Unknown"),
                                "language_code": detected_lang,
                                "transcription": text
                            }
                            
                            logger.info(f"Transcription-based detection: {detected_lang} (confidence: {confidence})")
                            logger.info(f"Transcription: {text[:100]}...")
                            
                        except Exception as lang_error:
                            logger.warning(f"Language detection from transcription failed: {lang_error}")
                    else:
                        logger.warning("Transcription returned empty or short text")
                        
                except Exception as transcribe_error:
                    logger.warning(f"Transcription failed: {transcribe_error}")
            else:
                logger.warning("No transcriber available, using feature-based detection only")
            
            # Choose the best result
            if transcription_result and transcription_result["confidence"] > feature_result["confidence"]:
                logger.info("Using transcription-based result (higher confidence)")
                return transcription_result
            else:
                logger.info("Using feature-based result")
                return feature_result
                
        except Exception as e:
            logger.error(f"Language detection error: {e}")
            # Return safe fallback
            return {
                "detected_language": "en",
                "confidence": 0.3,
                "language_name": "English",
                "language_code": "en",
                "transcription": ""
            }
    
    def _detect_language_from_features(self, audio_path: str) -> Dict:
        """Fallback method using audio features for language detection"""
        try:
            # Load audio
            y, sr = librosa.load(audio_path, sr=16000)
            
            # Extract comprehensive features
            mfcc = librosa.feature.mfcc(y=y, sr=sr, n_mfcc=13)
            spectral_centroid = librosa.feature.spectral_centroid(y=y, sr=sr)
            spectral_rolloff = librosa.feature.spectral_rolloff(y=y, sr=sr)
            spectral_bandwidth = librosa.feature.spectral_bandwidth(y=y, sr=sr)
            zero_crossing_rate = librosa.feature.zero_crossing_rate(y)
            
            # Calculate feature statistics
            avg_centroid = np.mean(spectral_centroid)
            avg_rolloff = np.mean(spectral_rolloff)
            avg_bandwidth = np.mean(spectral_bandwidth)
            avg_zcr = np.mean(zero_crossing_rate)
            mfcc_mean = np.mean(mfcc)
            mfcc_std = np.std(mfcc)
            
            # Enhanced language classification with better Indian language detection
            # Telugu has specific phonetic characteristics that we can identify
            
            # Check for Telugu-specific features
            telugu_score = 0
            if avg_centroid > 1600 and avg_centroid < 2100:  # More specific Telugu frequency range
                telugu_score += 1
            if avg_rolloff > 3200 and avg_rolloff < 4200:  # More specific Telugu rolloff range
                telugu_score += 1
            if avg_zcr > 0.06 and avg_zcr < 0.13:  # More specific Telugu zero crossing rate
                telugu_score += 1
            if mfcc_std > 25 and mfcc_std < 50:  # More specific Telugu MFCC variation
                telugu_score += 1
            
            # Check for Kannada-specific features (improved detection)
            kannada_score = 0
            # Kannada has distinctive phonetic characteristics
            if avg_centroid > 1200 and avg_centroid < 1800:  # Lower frequency range for Kannada
                kannada_score += 2  # Higher weight for centroid
            if avg_rolloff > 2000 and avg_rolloff < 3200:  # Lower rolloff for Kannada
                kannada_score += 1
            if avg_zcr > 0.03 and avg_zcr < 0.10:  # Lower ZCR for Kannada
                kannada_score += 1
            if mfcc_std > 20 and mfcc_std < 45:  # MFCC variation for Kannada
                kannada_score += 1
            if avg_bandwidth > 800 and avg_bandwidth < 1500:  # Bandwidth for Kannada
                kannada_score += 1
            
            # Check for Hindi-specific features
            hindi_score = 0
            if avg_centroid > 1700 and avg_centroid < 2300:
                hindi_score += 1
            if avg_rolloff > 3500 and avg_rolloff < 4800:
                hindi_score += 1
            if avg_zcr > 0.07 and avg_zcr < 0.16:
                hindi_score += 1
            
            # Determine language based on scores with improved detection
            # Use more flexible ranges and better scoring
            
            # Calculate total possible scores for normalization
            max_telugu_score = 4
            max_kannada_score = 5
            max_hindi_score = 3
            
            # Normalize scores
            telugu_ratio = telugu_score / max_telugu_score
            kannada_ratio = kannada_score / max_kannada_score
            hindi_ratio = hindi_score / max_hindi_score
            
            # Check for Indian languages first (they have more specific patterns)
            if kannada_ratio >= 0.8:  # 80% of max score
                detected_lang = "kn"  # Kannada
                confidence = 0.8
            elif telugu_ratio >= 0.8:  # 80% of max score
                detected_lang = "te"  # Telugu
                confidence = 0.8
            elif hindi_ratio >= 0.8:  # 80% of max score
                detected_lang = "hi"  # Hindi
                confidence = 0.8
            elif kannada_ratio >= 0.6 and kannada_ratio > telugu_ratio and kannada_ratio > hindi_ratio:
                detected_lang = "kn"  # Kannada
                confidence = 0.7
            elif telugu_ratio >= 0.6 and telugu_ratio > kannada_ratio and telugu_ratio > hindi_ratio:
                detected_lang = "te"  # Telugu
                confidence = 0.7
            elif hindi_ratio >= 0.6 and hindi_ratio > kannada_ratio and hindi_ratio > telugu_ratio:
                detected_lang = "hi"  # Hindi
                confidence = 0.7
            # Check for English with more flexible ranges
            elif (avg_centroid > 1500 and avg_centroid < 3500 and 
                  avg_rolloff > 2500 and avg_rolloff < 6000 and
                  avg_zcr > 0.03 and avg_zcr < 0.20):
                detected_lang = "en"  # English
                confidence = 0.8
            # Default to English if unclear
            else:
                detected_lang = "en"  # Default to English
                confidence = 0.5
            
            # Log the detection process for debugging
            logger.info(f"Language detection features - Centroid: {avg_centroid:.2f}, Rolloff: {avg_rolloff:.2f}, ZCR: {avg_zcr:.4f}, MFCC_std: {mfcc_std:.2f}")
            logger.info(f"Language scores - Telugu: {telugu_score}, Kannada: {kannada_score}, Hindi: {hindi_score}")
            logger.info(f"Detected language: {detected_lang} with confidence: {confidence}")
            
            return {
                "detected_language": detected_lang,
                "confidence": confidence,
                "language_name": self.supported_languages.get(detected_lang, "Unknown"),
                "language_code": detected_lang,
                "transcription": "",
                "detection_features": {
                    "spectral_centroid": float(avg_centroid),
                    "spectral_rolloff": float(avg_rolloff),
                    "zero_crossing_rate": float(avg_zcr),
                    "mfcc_std": float(mfcc_std),
                    "telugu_score": telugu_score,
                    "kannada_score": kannada_score,
                    "hindi_score": hindi_score
                }
            }
            
        except Exception as e:
            logger.error(f"Feature-based language detection error: {e}")
            return {
                "detected_language": "en",
                "confidence": 0.1,
                "language_name": "English",
                "language_code": "en",
                "transcription": ""
            }

class VoiceCloningDetector:
    """Detects AI-generated or cloned voices using multiple detection methods"""
    
    def __init__(self):
        self.model_path = "voice_cloning_detector.pkl"
        self.scaler_path = "voice_cloning_scaler.pkl"
        self.model = None
        self.scaler = None
        self._load_or_create_model()
    
    def _load_or_create_model(self):
        """Load existing model or create a new one"""
        try:
            if os.path.exists(self.model_path) and os.path.exists(self.scaler_path):
                self.model = joblib.load(self.model_path)
                self.scaler = joblib.load(self.scaler_path)
                logger.info("Loaded existing voice cloning detection model")
            else:
                self._create_model()
                logger.info("Created new voice cloning detection model")
        except Exception as e:
            logger.warning(f"Could not load model: {e}")
            self._create_model()
    
    def _create_model(self):
        """Create a simple Random Forest model for voice cloning detection"""
        self.model = RandomForestClassifier(n_estimators=100, random_state=42)
        self.scaler = StandardScaler()
        
        # Save the model
        try:
            joblib.dump(self.model, self.model_path)
            joblib.dump(self.scaler, self.scaler_path)
        except Exception as e:
            logger.warning(f"Could not save model: {e}")
    
    def extract_voice_features(self, audio_path: str) -> np.ndarray:
        """Extract features that help identify AI-generated voices"""
        try:
            y, sr = librosa.load(audio_path, sr=22050)
            
            features = []
            
            # 1. Spectral features
            spectral_centroids = librosa.feature.spectral_centroid(y=y, sr=sr)
            spectral_rolloff = librosa.feature.spectral_rolloff(y=y, sr=sr)
            spectral_bandwidth = librosa.feature.spectral_bandwidth(y=y, sr=sr)
            
            # 2. MFCC features
            mfccs = librosa.feature.mfcc(y=y, sr=sr, n_mfcc=13)
            
            # 3. Chroma features
            chroma = librosa.feature.chroma_stft(y=y, sr=sr)
            
            # 4. Zero crossing rate
            zcr = librosa.feature.zero_crossing_rate(y)
            
            # 5. Root mean square energy
            rms = librosa.feature.rms(y=y)
            
            # Aggregate features
            features.extend([
                np.mean(spectral_centroids), np.std(spectral_centroids),
                np.mean(spectral_rolloff), np.std(spectral_rolloff),
                np.mean(spectral_bandwidth), np.std(spectral_bandwidth),
                np.mean(mfccs), np.std(mfccs),
                np.mean(chroma), np.std(chroma),
                np.mean(zcr), np.std(zcr),
                np.mean(rms), np.std(rms)
            ])
            
            return np.array(features)
            
        except Exception as e:
            logger.error(f"Error extracting voice features: {e}")
            # Return default features
            return np.zeros(14)
    
    def detect_voice_cloning(self, audio_path: str) -> Dict:
        """Detect if the voice is AI-generated or cloned"""
        try:
            logger.info(f"Starting AI voice detection for: {audio_path}")
            
            # Extract features
            features = self.extract_voice_features(audio_path)
            features = features.reshape(1, -1)
            
            # Scale features (use transform, not fit_transform)
            if self.scaler:
                try:
                    features_scaled = self.scaler.transform(features)
                except:
                    # If scaler not fitted, use raw features
                    features_scaled = features
            else:
                features_scaled = features
            
            # Make prediction using enhanced heuristic
            confidence_score = self._heuristic_detection(features_scaled[0])
            
            # Also try raw features for comparison
            raw_confidence = self._heuristic_detection(features[0])
            
            # Use the higher confidence score
            final_confidence = max(confidence_score, raw_confidence)
            
            # Lower threshold for better detection (was 0.7, now 0.5)
            is_ai_generated = final_confidence > 0.5
            
            # Determine risk level with more sensitive thresholds
            if final_confidence > 0.75:
                risk_level = "high"
            elif final_confidence > 0.55:
                risk_level = "medium"
            else:
                risk_level = "low"
            
            logger.info(f"AI detection result: {is_ai_generated}, confidence: {final_confidence:.3f}, risk: {risk_level}")
            
            return {
                "is_ai_generated": is_ai_generated,
                "confidence_score": final_confidence,
                "detection_method": "enhanced_spectral_analysis",
                "risk_level": risk_level,
                "raw_features_confidence": raw_confidence,
                "scaled_features_confidence": confidence_score
            }
            
        except Exception as e:
            logger.error(f"Voice cloning detection error: {e}")
            return {
                "is_ai_generated": False,
                "confidence_score": 0.0,
                "detection_method": "error",
                "risk_level": "low"
            }
    
    def _heuristic_detection(self, features: np.ndarray) -> float:
        """Enhanced heuristic for voice cloning detection"""
        try:
            if len(features) < 14:
                return 0.0
                
            # Extract features
            spectral_centroid_mean = features[0]
            spectral_centroid_std = features[1]
            spectral_rolloff_mean = features[2]
            spectral_rolloff_std = features[3]
            spectral_bandwidth_mean = features[4]
            spectral_bandwidth_std = features[5]
            mfcc_mean = features[6]
            mfcc_std = features[7]
            chroma_mean = features[8]
            chroma_std = features[9]
            zcr_mean = features[10]
            zcr_std = features[11]
            rms_mean = features[12]
            rms_std = features[13]
            
            score = 0.0
            
            # Log feature values for debugging
            logger.info(f"AI Detection Features - Centroid: {spectral_centroid_mean:.2f}±{spectral_centroid_std:.2f}, "
                       f"Rolloff: {spectral_rolloff_mean:.2f}±{spectral_rolloff_std:.2f}, "
                       f"MFCC: {mfcc_mean:.2f}±{mfcc_std:.2f}, ZCR: {zcr_mean:.4f}±{zcr_std:.4f}, "
                       f"RMS: {rms_mean:.4f}±{rms_std:.4f}")
            
            # 1. SPECTRAL CONSISTENCY (AI voices are too consistent)
            if spectral_centroid_std < 30:  # Very low variation (AI-like)
                score += 0.5
            elif spectral_centroid_std < 60:
                score += 0.3
            elif spectral_centroid_std < 100:
                score += 0.1
                
            # 2. ROLLOFF CONSISTENCY (AI voices have unnatural rolloff patterns)
            if spectral_rolloff_std < 150:  # Very consistent rolloff
                score += 0.4
            elif spectral_rolloff_std < 300:
                score += 0.2
            elif spectral_rolloff_std < 500:
                score += 0.1
                
            # 3. MFCC VARIATION (AI voices have low MFCC variation)
            if mfcc_std < 8:  # Very low MFCC variation
                score += 0.5
            elif mfcc_std < 15:
                score += 0.3
            elif mfcc_std < 25:
                score += 0.1
                
            # 4. ZERO-CROSSING CONSISTENCY (AI voices have unnatural ZCR patterns)
            if zcr_std < 0.008:  # Very consistent ZCR
                score += 0.4
            elif zcr_std < 0.015:
                score += 0.2
            elif zcr_std < 0.025:
                score += 0.1
                
            # 5. RMS ENERGY CONSISTENCY (AI voices have very consistent energy)
            if rms_std < 0.008:  # Very consistent energy
                score += 0.4
            elif rms_std < 0.015:
                score += 0.2
            elif rms_std < 0.025:
                score += 0.1
                
            # 6. UNNATURAL FREQUENCY RANGES (AI voices often have odd frequency patterns)
            if spectral_centroid_mean > 3500 or spectral_centroid_mean < 800:
                score += 0.3
            elif spectral_centroid_mean > 3000 or spectral_centroid_mean < 1000:
                score += 0.1
                
            # 7. UNNATURAL ROLLOFF RANGES
            if spectral_rolloff_mean > 7000 or spectral_rolloff_mean < 1500:
                score += 0.3
            elif spectral_rolloff_mean > 6000 or spectral_rolloff_mean < 2000:
                score += 0.1
                
            # 8. CHROMA CONSISTENCY (AI voices have unnatural chroma patterns)
            if chroma_std < 0.05:  # Very consistent chroma
                score += 0.3
            elif chroma_std < 0.1:
                score += 0.1
                
            # 9. COMBINED "TOO PERFECT" PATTERNS (Multiple indicators together)
            perfect_patterns = 0
            if spectral_centroid_std < 40: perfect_patterns += 1
            if mfcc_std < 12: perfect_patterns += 1
            if zcr_std < 0.012: perfect_patterns += 1
            if rms_std < 0.012: perfect_patterns += 1
            if chroma_std < 0.08: perfect_patterns += 1
            
            if perfect_patterns >= 4:
                score += 0.6  # Very likely AI
            elif perfect_patterns >= 3:
                score += 0.4  # Likely AI
            elif perfect_patterns >= 2:
                score += 0.2  # Possibly AI
                
            # 10. UNUSUAL COMBINATIONS (AI voices have specific feature combinations)
            if (spectral_centroid_std < 50 and spectral_rolloff_std < 200 and 
                mfcc_std < 15 and zcr_std < 0.015):
                score += 0.4  # AI-like combination
                
            # 11. EXTREME CONSISTENCY (All features too consistent)
            consistency_score = 0
            if spectral_centroid_std < 50: consistency_score += 1
            if spectral_rolloff_std < 200: consistency_score += 1
            if mfcc_std < 15: consistency_score += 1
            if zcr_std < 0.015: consistency_score += 1
            if rms_std < 0.015: consistency_score += 1
            
            if consistency_score >= 4:
                score += 0.5  # Extremely consistent = likely AI
            elif consistency_score >= 3:
                score += 0.3  # Very consistent = possibly AI
                
            final_score = max(0.0, min(1.0, score))
            logger.info(f"AI Detection Score: {final_score:.3f} (from {score:.3f})")
            
            return final_score
            
        except Exception as e:
            logger.error(f"Heuristic detection error: {e}")
            return 0.0

class EnhancedAnalyzer:
    """Combines language detection and voice cloning detection"""
    
    def __init__(self):
        self.language_detector = LanguageDetector()
        self.voice_cloning_detector = VoiceCloningDetector()
        logger.info("Enhanced analyzer initialized successfully")
    
    def analyze_audio_enhanced(self, audio_path: str) -> Dict:
        """Perform enhanced analysis including language and voice cloning detection"""
        try:
            # Language detection
            language_result = self.language_detector.detect_language_from_audio(audio_path)
            
            # Voice cloning detection
            voice_cloning_result = self.voice_cloning_detector.detect_voice_cloning(audio_path)
            
            return {
                "language_detection": language_result,
                "voice_cloning_detection": voice_cloning_result,
                "enhanced_analysis": {
                    "multilingual_support": True,
                    "ai_detection_enabled": True,
                    "analysis_timestamp": str(np.datetime64('now'))
                }
            }
            
        except Exception as e:
            logger.error(f"Enhanced analysis error: {e}")
            return {
                "language_detection": {
                    "detected_language": "en",
                    "confidence": 0.0,
                    "language_name": "English",
                    "language_code": "en",
                    "transcription": ""
                },
                "voice_cloning_detection": {
                    "is_ai_generated": False,
                    "confidence_score": 0.0,
                    "detection_method": "error",
                    "risk_level": "low"
                },
                "enhanced_analysis": {
                    "multilingual_support": False,
                    "ai_detection_enabled": False,
                    "analysis_timestamp": str(np.datetime64('now'))
                }
            } 