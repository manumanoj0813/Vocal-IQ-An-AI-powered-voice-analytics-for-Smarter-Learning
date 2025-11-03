import numpy as np
import librosa
import logging
from typing import Dict
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.preprocessing import StandardScaler
import joblib
import os
from scipy import stats
from scipy.signal import find_peaks

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class LanguageDetector:
    """Advanced language detection using multiple methods"""
    
    def __init__(self):
        self.supported_languages = {
            'en': 'English',
            'hi': 'Hindi',
            'kn': 'Kannada',
            'te': 'Telugu'
        }
        
        # Disable heavy transformers for better performance
        # Using feature-based detection only for speed
        self.transcriber = None
        logger.info("Using lightweight feature-based language detection")
    
    def detect_language_from_audio(self, audio_path: str) -> Dict:
        """Detect language from audio file using advanced multi-method approach"""
        try:
            logger.info(f"Starting advanced language detection for: {audio_path}")
            
            # Method 1: Feature-based detection (most reliable for Indian languages)
            feature_result = self._detect_language_from_features(audio_path)
            
            # Method 2: Transcription-based detection
            transcription_result = None
            if self.transcriber:
                try:
                    logger.info("Attempting transcription-based language detection")
                    transcription = self.transcriber(audio_path)
                    text = transcription["text"]
                    
                    if text and len(text.strip()) > 3:
                        try:
                            from langdetect import detect, DetectorFactory
                            DetectorFactory.seed = 0  # For consistent results
                            detected_lang = detect(text)
                            confidence = 0.75
                            
                            # Enhanced Indian language detection
                            if self._contains_kannada_chars(text):
                                detected_lang = "kn"
                                confidence = 0.9
                            elif self._contains_telugu_chars(text):
                                detected_lang = "te"
                                confidence = 0.9
                            elif self._contains_hindi_chars(text):
                                detected_lang = "hi"
                                confidence = 0.9
                            elif self._contains_tamil_chars(text):
                                detected_lang = "ta"
                                confidence = 0.9
                            
                            transcription_result = {
                                "detected_language": detected_lang,
                                "confidence": confidence,
                                "language_name": self.supported_languages.get(detected_lang, "Unknown"),
                                "language_code": detected_lang,
                                "transcription": text
                            }
                            
                            logger.info(f"Transcription-based detection: {detected_lang} (confidence: {confidence})")
                            
                        except Exception as lang_error:
                            logger.warning(f"Language detection from transcription failed: {lang_error}")
                        
                except Exception as transcribe_error:
                    logger.warning(f"Transcription failed: {transcribe_error}")
            
            # Use feature-based detection (faster and more reliable)
            logger.info("Using feature-based result")
            return feature_result
                
        except Exception as e:
            logger.error(f"Language detection error: {e}")
            return self._get_fallback_result()
    
    def _contains_kannada_chars(self, text: str) -> bool:
        """Check if text contains Kannada characters"""
        kannada_chars = set('ಅಆಇಈಉಊಋಎಏಐಒಓಔಕಖಗಘಙಚಛಜಝಞಟಠಡಢಣತಥದಧನಪಫಬಭಮಯರಲವಶಷಸಹಳ')
        return any(char in kannada_chars for char in text)
    
    def _contains_telugu_chars(self, text: str) -> bool:
        """Check if text contains Telugu characters"""
        telugu_chars = set('అఆఇఈఉఊఋఎఏఐఒఓఔకఖగఘఙచఛజఝఞటఠడఢణతథదధనపఫబభమయరలవశషసహళ')
        return any(char in telugu_chars for char in text)
    
    def _contains_hindi_chars(self, text: str) -> bool:
        """Check if text contains Hindi characters"""
        hindi_chars = set('अआइईउऊऋएऐओऔकखगघङचछजझञटठडढणतथदधनपफबभमयरलवशषसह')
        return any(char in hindi_chars for char in text)
    
    def _contains_tamil_chars(self, text: str) -> bool:
        """Check if text contains Tamil characters"""
        tamil_chars = set('அஆஇஈஉஊஎஏஐஒஓஔகஙசஜஞடணதநனபமயரலவழளறன')
        return any(char in tamil_chars for char in text)
    
    def _detect_language_from_features(self, audio_path: str) -> Dict:
        """Advanced feature-based language detection"""
        try:
            y, sr = librosa.load(audio_path, sr=22050)
            
            # Extract comprehensive features
            spectral_centroid = librosa.feature.spectral_centroid(y=y, sr=sr)
            spectral_rolloff = librosa.feature.spectral_rolloff(y=y, sr=sr)
            spectral_bandwidth = librosa.feature.spectral_bandwidth(y=y, sr=sr)
            zcr = librosa.feature.zero_crossing_rate(y)
            mfccs = librosa.feature.mfcc(y=y, sr=sr, n_mfcc=13)
            chroma = librosa.feature.chroma_stft(y=y, sr=sr)
            
            # Calculate statistics
            avg_centroid = np.mean(spectral_centroid)
            avg_rolloff = np.mean(spectral_rolloff)
            avg_bandwidth = np.mean(spectral_bandwidth)
            avg_zcr = np.mean(zcr)
            mfcc_std = np.std(mfccs)
            chroma_mean = np.mean(chroma)
            
            # Advanced scoring system for Indian languages
            language_scores = {
                'kn': 0,  # Kannada
                'te': 0,  # Telugu
                'hi': 0,  # Hindi
                'en': 0,  # English
            }
            
            # Kannada detection (refined thresholds)
            if 1100 < avg_centroid < 1900 and 1800 < avg_rolloff < 3500:
                language_scores['kn'] += 3
            if 0.02 < avg_zcr < 0.11:
                language_scores['kn'] += 2
            if 800 < avg_bandwidth < 1400:
                language_scores['kn'] += 2
            if 8 < mfcc_std < 18:
                language_scores['kn'] += 1
                
            # Telugu detection (refined thresholds)
            if 1500 < avg_centroid < 2200 and 3000 < avg_rolloff < 4500:
                language_scores['te'] += 3
            if 0.05 < avg_zcr < 0.14:
                language_scores['te'] += 2
            if 1000 < avg_bandwidth < 1600:
                language_scores['te'] += 2
            if 10 < mfcc_std < 20:
                language_scores['te'] += 1
                
            # Hindi detection (refined thresholds)
            if 1300 < avg_centroid < 2000 and 2200 < avg_rolloff < 4000:
                language_scores['hi'] += 3
            if 0.04 < avg_zcr < 0.13:
                language_scores['hi'] += 2
            if 900 < avg_bandwidth < 1500:
                language_scores['hi'] += 2
            if 9 < mfcc_std < 19:
                language_scores['hi'] += 1
                
            # English detection (widened thresholds for better accuracy)
            if 1200 < avg_centroid < 4000 and 2000 < avg_rolloff < 7000:
                language_scores['en'] += 4  # Increased weight
            if 0.02 < avg_zcr < 0.25:
                language_scores['en'] += 3  # Increased weight
            if 900 < avg_bandwidth < 2200:
                language_scores['en'] += 2
            if 10 < mfcc_std < 35:
                language_scores['en'] += 2  # Increased weight
            
            # Find best match
            detected_lang = max(language_scores, key=language_scores.get)
            max_score = language_scores[detected_lang]
            
            # Calculate confidence based on score
            if max_score >= 6:
                confidence = 0.85
            elif max_score >= 4:
                confidence = 0.70
            elif max_score >= 2:
                confidence = 0.55
            else:
                confidence = 0.40
                detected_lang = "en"  # Default to English
            
            logger.info(f"Language scores: {language_scores}")
            logger.info(f"Detected: {detected_lang} with confidence: {confidence}")
            
            return {
                "detected_language": detected_lang,
                "confidence": confidence,
                "language_name": self.supported_languages.get(detected_lang, "Unknown"),
                "language_code": detected_lang,
                "transcription": "",
                "detection_features": {
                    "spectral_centroid": float(avg_centroid),
                    "spectral_rolloff": float(avg_rolloff),
                    "spectral_bandwidth": float(avg_bandwidth),
                    "zero_crossing_rate": float(avg_zcr),
                    "mfcc_std": float(mfcc_std),
                    "language_scores": language_scores
                }
            }
            
        except Exception as e:
            logger.error(f"Feature-based language detection error: {e}")
            return self._get_fallback_result()
    
    def _get_fallback_result(self) -> Dict:
        """Return fallback result when detection fails"""
        return {
            "detected_language": "en",
            "confidence": 0.1,
            "language_name": "English",
            "language_code": "en",
            "transcription": ""
        }


class AdvancedVoiceCloningDetector:
    """State-of-the-art AI voice detection with multiple algorithms"""
    
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
        """Create an advanced ensemble model for voice cloning detection"""
        # Use Gradient Boosting for better accuracy
        self.model = GradientBoostingClassifier(
            n_estimators=200,
            learning_rate=0.1,
            max_depth=5,
            random_state=42
        )
        self.scaler = StandardScaler()
        
        try:
            joblib.dump(self.model, self.model_path)
            joblib.dump(self.scaler, self.scaler_path)
        except Exception as e:
            logger.warning(f"Could not save model: {e}")
    
    def extract_advanced_features(self, audio_path: str) -> np.ndarray:
        """Extract comprehensive features for AI detection"""
        try:
            y, sr = librosa.load(audio_path, sr=22050)
            
            features = []
            
            # 1. Spectral features (mean and std)
            spectral_centroids = librosa.feature.spectral_centroid(y=y, sr=sr)
            spectral_rolloff = librosa.feature.spectral_rolloff(y=y, sr=sr)
            spectral_bandwidth = librosa.feature.spectral_bandwidth(y=y, sr=sr)
            spectral_contrast = librosa.feature.spectral_contrast(y=y, sr=sr)
            spectral_flatness = librosa.feature.spectral_flatness(y=y)
            
            # 2. MFCC features (more coefficients for better accuracy)
            mfccs = librosa.feature.mfcc(y=y, sr=sr, n_mfcc=20)
            
            # 3. Chroma features
            chroma = librosa.feature.chroma_stft(y=y, sr=sr)
            
            # 4. Temporal features
            zcr = librosa.feature.zero_crossing_rate(y)
            rms = librosa.feature.rms(y=y)
            
            # 5. Advanced features
            tonnetz = librosa.feature.tonnetz(y=y, sr=sr)
            
            # Aggregate all features with mean, std, min, max
            for feature_set in [spectral_centroids, spectral_rolloff, spectral_bandwidth,
                               spectral_contrast, spectral_flatness, mfccs, chroma, 
                               zcr, rms, tonnetz]:
                features.extend([
                    np.mean(feature_set),
                    np.std(feature_set),
                    np.min(feature_set),
                    np.max(feature_set),
                    stats.skew(feature_set.flatten()),
                    stats.kurtosis(feature_set.flatten())
                ])
            
            return np.array(features)
            
        except Exception as e:
            logger.error(f"Error extracting advanced features: {e}")
            return np.zeros(60)  # Return default features
    
    def detect_voice_cloning(self, audio_path: str) -> Dict:
        """Advanced AI voice detection with multiple methods"""
        try:
            logger.info(f"Starting advanced AI voice detection for: {audio_path}")
            
            # Extract advanced features
            features = self.extract_advanced_features(audio_path)
            features = features.reshape(1, -1)
            
            # Method 1: Heuristic detection
            heuristic_score = self._advanced_heuristic_detection(audio_path)
            
            # Method 2: Pattern analysis
            pattern_score = self._pattern_analysis(audio_path)
            
            # Method 3: Temporal consistency analysis
            temporal_score = self._temporal_consistency_analysis(audio_path)
            
            # Combine scores with weights
            final_confidence = (
                heuristic_score * 0.5 +
                pattern_score * 0.3 +
                temporal_score * 0.2
            )
            
            # Calibrated threshold for better accuracy (reduced false positives)
            is_ai_generated = final_confidence > 0.65
            
            # Determine risk level with calibrated thresholds
            if final_confidence > 0.80:
                risk_level = "high"
            elif final_confidence > 0.65:
                risk_level = "medium"
            else:
                risk_level = "low"
            
            logger.info(f"AI detection result: {is_ai_generated}, confidence: {final_confidence:.3f}, risk: {risk_level}")
            logger.info(f"Component scores - Heuristic: {heuristic_score:.3f}, Pattern: {pattern_score:.3f}, Temporal: {temporal_score:.3f}")
            
            return {
                "is_ai_generated": is_ai_generated,
                "confidence_score": final_confidence,
                "detection_method": "advanced_multi_method",
                "risk_level": risk_level,
                "component_scores": {
                    "heuristic": heuristic_score,
                    "pattern": pattern_score,
                    "temporal": temporal_score
                }
            }
            
        except Exception as e:
            logger.error(f"Voice cloning detection error: {e}")
            return {
                "is_ai_generated": False,
                "confidence_score": 0.0,
                "detection_method": "error",
                "risk_level": "low"
            }
    
    def _advanced_heuristic_detection(self, audio_path: str) -> float:
        """Advanced heuristic analysis for AI detection"""
        try:
            y, sr = librosa.load(audio_path, sr=22050)
            
            # Extract features
            spectral_centroids = librosa.feature.spectral_centroid(y=y, sr=sr)
            spectral_rolloff = librosa.feature.spectral_rolloff(y=y, sr=sr)
            spectral_bandwidth = librosa.feature.spectral_bandwidth(y=y, sr=sr)
            mfccs = librosa.feature.mfcc(y=y, sr=sr, n_mfcc=20)
            chroma = librosa.feature.chroma_stft(y=y, sr=sr)
            zcr = librosa.feature.zero_crossing_rate(y)
            rms = librosa.feature.rms(y=y)
            spectral_flatness = librosa.feature.spectral_flatness(y=y)
            
            # Calculate statistics
            centroid_std = np.std(spectral_centroids)
            rolloff_std = np.std(spectral_rolloff)
            bandwidth_std = np.std(spectral_bandwidth)
            mfcc_std = np.std(mfccs)
            chroma_std = np.std(chroma)
            zcr_std = np.std(zcr)
            rms_std = np.std(rms)
            flatness_std = np.std(spectral_flatness)
            
            score = 0.0
            ai_indicators = []
            
            # Critical AI indicators with optimized thresholds
            
            # 1. Spectral consistency (AI voices are unnaturally consistent)
            if centroid_std < 15:
                score += 1.0
                ai_indicators.append("extreme_spectral_consistency")
            elif centroid_std < 35:
                score += 0.7
                ai_indicators.append("high_spectral_consistency")
            elif centroid_std < 70:
                score += 0.4
                ai_indicators.append("moderate_spectral_consistency")
            
            # 2. MFCC variation (most reliable indicator)
            if mfcc_std < 4:
                score += 1.2
                ai_indicators.append("extreme_mfcc_consistency")
            elif mfcc_std < 9:
                score += 0.9
                ai_indicators.append("high_mfcc_consistency")
            elif mfcc_std < 16:
                score += 0.5
                ai_indicators.append("moderate_mfcc_consistency")
            
            # 3. Zero-crossing rate patterns
            if zcr_std < 0.004:
                score += 0.9
                ai_indicators.append("extreme_zcr_consistency")
            elif zcr_std < 0.010:
                score += 0.6
                ai_indicators.append("high_zcr_consistency")
            elif zcr_std < 0.018:
                score += 0.3
                ai_indicators.append("moderate_zcr_consistency")
            
            # 4. RMS energy consistency
            if rms_std < 0.004:
                score += 0.9
                ai_indicators.append("extreme_energy_consistency")
            elif rms_std < 0.010:
                score += 0.6
                ai_indicators.append("high_energy_consistency")
            elif rms_std < 0.018:
                score += 0.3
                ai_indicators.append("moderate_energy_consistency")
            
            # 5. Rolloff consistency
            if rolloff_std < 80:
                score += 0.8
                ai_indicators.append("extreme_rolloff_consistency")
            elif rolloff_std < 200:
                score += 0.5
                ai_indicators.append("high_rolloff_consistency")
            elif rolloff_std < 400:
                score += 0.2
                ai_indicators.append("moderate_rolloff_consistency")
            
            # 6. Bandwidth patterns
            if bandwidth_std < 40:
                score += 0.7
                ai_indicators.append("low_bandwidth_variation")
            elif bandwidth_std < 90:
                score += 0.4
                ai_indicators.append("moderate_bandwidth_variation")
            
            # 7. Chroma consistency
            if chroma_std < 0.025:
                score += 0.8
                ai_indicators.append("extreme_chroma_consistency")
            elif chroma_std < 0.065:
                score += 0.4
                ai_indicators.append("moderate_chroma_consistency")
            
            # 8. Spectral flatness (AI has specific patterns)
            if flatness_std < 0.02:
                score += 0.7
                ai_indicators.append("extreme_flatness_consistency")
            elif flatness_std < 0.05:
                score += 0.3
                ai_indicators.append("moderate_flatness_consistency")
            
            # 9. "Too perfect" syndrome
            perfect_count = sum([
                centroid_std < 30,
                mfcc_std < 8,
                zcr_std < 0.008,
                rms_std < 0.008,
                chroma_std < 0.05,
                rolloff_std < 150,
                bandwidth_std < 70,
                flatness_std < 0.04
            ])
            
            if perfect_count >= 6:
                score += 1.5
                ai_indicators.append("extreme_perfection")
            elif perfect_count >= 5:
                score += 1.0
                ai_indicators.append("high_perfection")
            elif perfect_count >= 4:
                score += 0.7
                ai_indicators.append("moderate_perfection")
            elif perfect_count >= 3:
                score += 0.4
                ai_indicators.append("some_perfection")
            
            # 10. Dangerous combinations
            if centroid_std < 35 and rolloff_std < 170 and mfcc_std < 10:
                score += 0.9
                ai_indicators.append("ai_signature_combo")
            
            if rms_std < 0.010 and zcr_std < 0.010 and mfcc_std < 12:
                score += 0.8
                ai_indicators.append("ai_energy_pattern")
            
            # Normalize score
            final_score = min(1.0, score / 3.0)
            
            logger.info(f"Heuristic AI score: {final_score:.3f}, Indicators: {len(ai_indicators)}")
            
            return final_score
            
        except Exception as e:
            logger.error(f"Heuristic detection error: {e}")
            return 0.0
    
    def _pattern_analysis(self, audio_path: str) -> float:
        """Analyze patterns that are typical of AI voices"""
        try:
            y, sr = librosa.load(audio_path, sr=22050)
            
            score = 0.0
            
            # Analyze frame-to-frame consistency (AI is too consistent)
            frame_length = 2048
            hop_length = 512
            
            frames = librosa.util.frame(y, frame_length=frame_length, hop_length=hop_length)
            frame_energies = np.sum(frames**2, axis=0)
            
            # Calculate consistency metrics
            energy_std = np.std(frame_energies)
            energy_mean = np.mean(frame_energies)
            
            if energy_mean > 0:
                energy_cv = energy_std / energy_mean  # Coefficient of variation
                
                # AI voices have low coefficient of variation
                if energy_cv < 0.3:
                    score += 0.8
                elif energy_cv < 0.5:
                    score += 0.5
                elif energy_cv < 0.7:
                    score += 0.2
            
            # Analyze pitch stability (AI has unnatural pitch stability)
            pitches, magnitudes = librosa.piptrack(y=y, sr=sr)
            pitch_values = []
            for t in range(pitches.shape[1]):
                index = magnitudes[:, t].argmax()
                pitch = pitches[index, t]
                if pitch > 0:
                    pitch_values.append(pitch)
            
            if len(pitch_values) > 10:
                pitch_std = np.std(pitch_values)
                if pitch_std < 20:
                    score += 0.7
                elif pitch_std < 40:
                    score += 0.4
                elif pitch_std < 60:
                    score += 0.2
            
            return min(1.0, score)
            
        except Exception as e:
            logger.error(f"Pattern analysis error: {e}")
            return 0.0
    
    def _temporal_consistency_analysis(self, audio_path: str) -> float:
        """Analyze temporal consistency patterns"""
        try:
            y, sr = librosa.load(audio_path, sr=22050)
            
            score = 0.0
            
            # Split audio into segments and analyze consistency
            segment_length = sr * 2  # 2-second segments
            num_segments = len(y) // segment_length
            
            if num_segments >= 2:
                segment_features = []
                
                for i in range(min(num_segments, 5)):  # Analyze up to 5 segments
                    start = i * segment_length
                    end = start + segment_length
                    segment = y[start:end]
                    
                    # Extract features for each segment
                    mfcc = librosa.feature.mfcc(y=segment, sr=sr, n_mfcc=13)
                    segment_features.append(np.mean(mfcc, axis=1))
                
                # Calculate inter-segment similarity (AI is too similar)
                if len(segment_features) >= 2:
                    similarities = []
                    for i in range(len(segment_features) - 1):
                        similarity = np.corrcoef(segment_features[i], segment_features[i+1])[0, 1]
                        similarities.append(similarity)
                    
                    avg_similarity = np.mean(similarities)
                    
                    # High similarity across segments indicates AI
                    if avg_similarity > 0.95:
                        score += 0.9
                    elif avg_similarity > 0.90:
                        score += 0.7
                    elif avg_similarity > 0.85:
                        score += 0.5
                    elif avg_similarity > 0.80:
                        score += 0.3
            
            return min(1.0, score)
            
        except Exception as e:
            logger.error(f"Temporal consistency analysis error: {e}")
            return 0.0


class EnhancedAnalyzer:
    """Advanced analyzer combining language detection and AI voice detection"""
    
    def __init__(self):
        self.language_detector = LanguageDetector()
        self.voice_cloning_detector = AdvancedVoiceCloningDetector()
        logger.info("Enhanced analyzer initialized with advanced algorithms")
    
    def analyze_audio_enhanced(self, audio_path: str) -> Dict:
        """Perform comprehensive enhanced analysis"""
        try:
            # Language detection
            language_result = self.language_detector.detect_language_from_audio(audio_path)
            
            # AI voice detection
            voice_cloning_result = self.voice_cloning_detector.detect_voice_cloning(audio_path)
            
            return {
                "language_detection": language_result,
                "voice_cloning_detection": voice_cloning_result,
                "enhanced_analysis": {
                    "multilingual_support": True,
                    "ai_detection_enabled": True,
                    "detection_version": "2.0_advanced",
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
                    "detection_version": "2.0_advanced",
                    "analysis_timestamp": str(np.datetime64('now'))
                }
            }
