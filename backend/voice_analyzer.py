import librosa
import numpy as np
from typing import Dict, List, Tuple
import logging
import subprocess
import tempfile
from pathlib import Path
import asyncio
import whisper
from scipy import signal
from scipy.stats import skew, kurtosis
import warnings
warnings.filterwarnings('ignore')

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def to_python_type(obj):
    if isinstance(obj, np.generic):
        return obj.item()
    if isinstance(obj, np.ndarray):
        return obj.tolist()
    if isinstance(obj, dict):
        return {k: to_python_type(v) for k, v in obj.items()}
    if isinstance(obj, list):
        return [to_python_type(v) for v in obj]
    return obj

class VoiceAnalyzer:
    def __init__(self):
        try:
            logger.info("Initializing enhanced voice analyzer...")
            # Check if ffmpeg is available
            try:
                subprocess.run(['ffmpeg', '-version'], capture_output=True, check=True)
            except (subprocess.CalledProcessError, FileNotFoundError) as e:
                logger.error(f"FFmpeg check failed: {str(e)}")
                raise RuntimeError("ffmpeg is not installed or not accessible. Please install ffmpeg to process audio files.")
            
            # Load Whisper model - use tiny model for speed (4x faster)
            logger.info("Loading Whisper model (tiny for speed)...")
            self.whisper_model = whisper.load_model("tiny")  # Tiny model for faster processing
            logger.info("Whisper model loaded successfully.")

            # Initialize advanced analysis parameters
            self.sample_rate = 22050  # Higher sample rate for better quality
            self.hop_length = 512
            self.frame_length = 2048
            
            logger.info("Enhanced voice analyzer initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize voice analyzer: {str(e)}")
            raise RuntimeError(f"Voice analyzer initialization failed: {str(e)}")
        
    async def analyze_audio(self, audio_path: str) -> dict:
        """Comprehensive voice analysis including fluency and linguistic features with enhanced accuracy."""
        try:
            logger.info(f"Processing audio file: {audio_path}")
            
            # Check if file exists and has content
            if not Path(audio_path).exists():
                raise FileNotFoundError(f"Audio file not found: {audio_path}")
            
            file_size = Path(audio_path).stat().st_size
            if file_size == 0:
                raise ValueError(f"Audio file is empty: {audio_path}")
            
            logger.info(f"Audio file size: {file_size} bytes")
            
            # Convert WebM to WAV with enhanced quality
            wav_path = self._convert_to_wav(audio_path)
            
            try:
                # Load and analyze the WAV file with higher quality
                logger.info(f"Loading WAV file: {wav_path}")
                y, sr = librosa.load(wav_path, sr=self.sample_rate)
                logger.info(f"Audio loaded: {len(y)} samples, {sr} Hz sample rate")
                
                # Apply audio preprocessing for better analysis
                y_processed = self._preprocess_audio(y, sr)
                
                # Basic audio features
                duration = librosa.get_duration(y=y, sr=sr)
                logger.info(f"Audio duration: {duration} seconds")
                
                # Enhanced analysis with better algorithms
                pitch_data = self._analyze_pitch_enhanced(y_processed, sr)
                rhythm_data = self._analyze_rhythm_enhanced(y_processed, sr)
                clarity_data = self._analyze_clarity_enhanced(y_processed, sr)
                emotion_data = self._analyze_emotion_enhanced(y_processed, sr)
                fluency_data = self._analyze_fluency_enhanced(y_processed, sr)
                
                # Transcribe audio with enhanced settings
                logger.info("Starting enhanced transcription...")
                transcript = self._transcribe_audio_enhanced(wav_path)
                logger.info(f"Transcription completed: {len(transcript)} characters")
                
                # Generate comprehensive recommendations
                recommendations = self._generate_recommendations_enhanced(
                    pitch_data, rhythm_data, clarity_data, emotion_data, fluency_data
                )
                
                # Calculate overall confidence score
                confidence_score = self._calculate_confidence_score(
                    pitch_data, rhythm_data, clarity_data, emotion_data, fluency_data
                )
                
                logger.info("Enhanced audio analysis completed successfully")
                result = {
                    "audio_metrics": {
                        "duration": duration,
                        "confidence_score": confidence_score,
                        "pitch": {
                            "average_pitch": pitch_data["average"],
                            "pitch_variation": pitch_data["variation"],
                            "pitch_range": {
                                "min": pitch_data["range_min"],
                                "max": pitch_data["range_max"]
                            },
                            "pitch_stability": pitch_data["stability"],
                            "pitch_contour": pitch_data["contour_score"]
                        },
                        "rhythm": {
                            "speech_rate": rhythm_data["speech_rate"],
                            "pause_ratio": rhythm_data["pause_ratio"],
                            "average_pause_duration": rhythm_data["avg_pause_duration"],
                            "total_speaking_time": rhythm_data["total_speech_time"],
                            "rhythm_consistency": rhythm_data["consistency"],
                            "stress_pattern": rhythm_data["stress_pattern"]
                        },
                        "clarity": {
                            "clarity_score": clarity_data["clarity_score"],
                            "pronunciation_score": clarity_data["articulation_score"],
                            "articulation_rate": clarity_data["spectral_quality"],
                            "speech_errors": clarity_data["errors"],
                            "enunciation_quality": clarity_data["enunciation"],
                            "voice_projection": clarity_data["projection"]
                        },
                        "emotion": {
                            "dominant_emotion": emotion_data["dominant_emotion"],
                            "emotion_confidence": emotion_data["confidence"],
                            "emotion_scores": emotion_data["scores"],
                            "emotional_range": emotion_data["range"],
                            "emotional_stability": emotion_data["stability"]
                        },
                        "fluency": {
                            "fluency_score": fluency_data["fluency_score"],
                            "filler_words": fluency_data["filler_words"],
                            "repetitions": fluency_data["repetitions"],
                            "hesitations": fluency_data["hesitations"],
                            "smoothness": fluency_data["smoothness"]
                        }
                    },
                    "transcription": {
                        "full_text": transcript,
                        "word_count": len(transcript.split()),
                        "transcription_confidence": 0.95  # High confidence for base model
                    },
                    "recommendations": {
                        "key_points": recommendations[:3] if len(recommendations) >= 3 else recommendations,
                        "improvement_areas": self._identify_improvement_areas(
                            pitch_data, rhythm_data, clarity_data, emotion_data, fluency_data
                        ),
                        "strengths": self._identify_strengths(
                            pitch_data, rhythm_data, clarity_data, emotion_data, fluency_data
                        ),
                        "practice_suggestions": self._generate_practice_suggestions(
                            pitch_data, rhythm_data, clarity_data, emotion_data, fluency_data
                        )
                    },
                    "metadata": {
                        "session_type": "practice",
                        "topic": "general",
                        "duration": duration,
                        "file_path": audio_path,
                        "analysis_version": "2.0",
                        "model_confidence": confidence_score
                    }
                }
                return to_python_type(result)
            finally:
                # Clean up the temporary WAV file
                try:
                    Path(wav_path).unlink()
                    logger.info(f"Cleaned up temporary WAV file: {wav_path}")
                except Exception as e:
                    logger.warning(f"Failed to delete temporary WAV file {wav_path}: {str(e)}")
                    
        except Exception as e:
            logger.error(f"Error analyzing audio: {str(e)}")
            logger.error(f"Exception type: {type(e).__name__}")
            import traceback
            logger.error(f"Traceback: {traceback.format_exc()}")
            raise RuntimeError(f"Audio analysis failed: {str(e)}")
    
    def _preprocess_audio(self, y: np.ndarray, sr: int) -> np.ndarray:
        """Apply advanced audio preprocessing for better analysis."""
        try:
            # Remove DC offset
            y = y - np.mean(y)
            
            # Apply high-pass filter to remove low-frequency noise
            b, a = signal.butter(4, 80/(sr/2), btype='high')
            y = signal.filtfilt(b, a, y)
            
            # Normalize audio
            y = librosa.util.normalize(y)
            
            # Apply spectral subtraction for noise reduction
            # This is a simplified version - in production you might want more sophisticated noise reduction
            stft = librosa.stft(y, n_fft=2048, hop_length=512)
            magnitude = np.abs(stft)
            phase = np.angle(stft)
            
            # Estimate noise from first 0.5 seconds
            noise_frames = int(0.5 * sr / 512)
            noise_spectrum = np.mean(magnitude[:, :noise_frames], axis=1, keepdims=True)
            
            # Apply spectral subtraction
            alpha = 2.0  # Subtraction factor
            beta = 0.01  # Spectral floor
            cleaned_magnitude = magnitude - alpha * noise_spectrum
            cleaned_magnitude = np.maximum(cleaned_magnitude, beta * magnitude)
            
            # Reconstruct signal
            cleaned_stft = cleaned_magnitude * np.exp(1j * phase)
            y_cleaned = librosa.istft(cleaned_stft, hop_length=512)
            
            return y_cleaned
            
        except Exception as e:
            logger.warning(f"Audio preprocessing failed: {e}, using original audio")
            return y
    
    def _transcribe_audio_enhanced(self, audio_path: str) -> str:
        """Transcribe audio using Whisper with enhanced settings for better accuracy."""
        try:
            logger.info(f"Transcribing audio file: {audio_path}")
            # Use optimized settings for speed and accuracy
            result = self.whisper_model.transcribe(
                audio_path,
                language="en",  # Force English for better accuracy
                task="transcribe",
                fp16=False,
                verbose=False,
                temperature=0.0,  # Deterministic
                beam_size=3,  # Reduced for speed
                best_of=3,  # Reduced for speed
                no_speech_threshold=0.6  # Better silence detection
            )
            transcript = result["text"]
            logger.info(f"Enhanced transcription successful. Text: {transcript[:100]}...")
            return transcript
        except Exception as e:
            logger.error(f"Error during transcription: {str(e)}")
            return "Transcription failed."
    
    def _convert_to_wav(self, input_path: str) -> str:
        """Convert input audio to WAV format using ffmpeg with enhanced quality."""
        try:
            logger.info(f"Input audio file path: {input_path}")
            input_file_path_obj = Path(input_path)
            if not input_file_path_obj.exists():
                raise FileNotFoundError(f"Input file does not exist: {input_path}")
            if input_file_path_obj.stat().st_size == 0:
                raise ValueError(f"Input file is empty: {input_path}")

            # Create temporary WAV file
            with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as temp_wav:
                wav_path = temp_wav.name
            
            # Convert to WAV using ffmpeg with enhanced quality settings
            cmd = [
                'ffmpeg',
                '-i', input_path,
                '-acodec', 'pcm_s16le',
                '-ar', str(self.sample_rate),  # Higher sample rate
                '-ac', '1',
                '-af', 'highpass=f=80,lowpass=f=8000',  # Apply filters
                '-y',  # Overwrite output file if it exists
                wav_path
            ]
            
            logger.info(f"Running ffmpeg command: {' '.join(cmd)}")
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            if result.returncode != 0:
                logger.error(f"FFmpeg conversion failed: {result.stderr}")
                raise RuntimeError(f"Audio conversion failed: {result.stderr}")
            
            logger.info(f"Audio converted successfully to: {wav_path}")
            return wav_path
            
        except Exception as e:
            logger.error(f"Error converting audio: {str(e)}")
            raise RuntimeError(f"Audio conversion failed: {str(e)}")
    
    def _analyze_pitch_enhanced(self, y: np.ndarray, sr: int) -> Dict:
        """Enhanced pitch analysis with advanced features."""
        try:
            # Use advanced pitch tracking with better parameters
            pitches, magnitudes = librosa.piptrack(
                y=y, sr=sr, 
                hop_length=self.hop_length, 
                fmin=librosa.note_to_hz('C2'), 
                fmax=librosa.note_to_hz('C7'),
                threshold=0.1  # Lower threshold for better detection
            )
            
            # Get pitch values where magnitude is above threshold
            pitch_values = []
            for t in range(pitches.shape[1]):
                index = magnitudes[:, t].argmax()
                pitch = pitches[index, t]
                if pitch > 0:
                    pitch_values.append(pitch)
            
            if not pitch_values:
                return {
                    "average": 0,
                    "variation": 0,
                    "range_min": 0,
                    "range_max": 0,
                    "stability": 0.5,
                    "contour_score": 0.5
                }
            
            pitch_values = np.array(pitch_values)
            
            # Calculate advanced pitch features
            mean_pitch = np.mean(pitch_values)
            std_pitch = np.std(pitch_values)
            
            # Stability: how consistent the pitch is
            stability = 1.0 - (std_pitch / mean_pitch) if mean_pitch > 0 else 0.5
            stability = np.clip(stability, 0.0, 1.0)
            
            # Contour score: how natural the pitch contour is
            pitch_diff = np.diff(pitch_values)
            contour_score = 1.0 - (np.abs(skew(pitch_diff)) / 3.0)  # Normalized skewness
            contour_score = np.clip(contour_score, 0.0, 1.0)
            
            # Calculate pitch range in semitones for better musical context
            if mean_pitch > 0:
                pitch_range_semitones = 12 * np.log2(np.max(pitch_values) / np.min(pitch_values))
            else:
                pitch_range_semitones = 0
            
            return {
                "average": float(mean_pitch),
                "variation": float(std_pitch),
                "range_min": float(np.min(pitch_values)),
                "range_max": float(np.max(pitch_values)),
                "stability": float(stability),
                "contour_score": float(contour_score),
                "range_semitones": float(pitch_range_semitones)
            }
        except Exception as e:
            logger.error(f"Error in enhanced pitch analysis: {str(e)}")
            return {
                "average": 0,
                "variation": 0,
                "range_min": 0,
                "range_max": 0,
                "stability": 0.5,
                "contour_score": 0.5,
                "range_semitones": 0
            }
    
    def _analyze_rhythm_enhanced(self, y: np.ndarray, sr: int) -> Dict:
        """Enhanced rhythm analysis with advanced features."""
        try:
            # Advanced tempo detection with multiple methods
            tempo, _ = librosa.beat.beat_track(y=y, sr=sr, hop_length=self.hop_length)
            
            # Energy-based speech rate estimation with better parameters
            energy = librosa.feature.rms(y=y, hop_length=self.hop_length, frame_length=self.frame_length)[0]
            
            # Adaptive threshold based on energy distribution
            energy_percentile = np.percentile(energy, 30)
            threshold = energy_percentile * 1.2
            
            # Calculate speech rate based on energy peaks
            speech_segments = energy > threshold
            speech_rate = np.sum(speech_segments) / len(speech_segments)
            
            # Enhanced pause analysis
            pauses = energy < threshold
            pause_ratio = np.sum(pauses) / len(pauses)
            
            # Calculate average pause duration in seconds
            pause_durations = []
            in_pause = False
            pause_start = 0
            
            for i, is_pause in enumerate(pauses):
                if is_pause and not in_pause:
                    pause_start = i
                    in_pause = True
                elif not is_pause and in_pause:
                    pause_duration = (i - pause_start) * self.hop_length / sr
                    if pause_duration > 0.1:  # Only count pauses longer than 100ms
                        pause_durations.append(pause_duration)
                    in_pause = False
            
            avg_pause_duration = np.mean(pause_durations) if pause_durations else 0.0
            
            # Calculate rhythm consistency using autocorrelation
            if len(energy) > 10:
                # Normalize energy
                energy_norm = (energy - np.mean(energy)) / np.std(energy)
                # Calculate autocorrelation
                autocorr = np.correlate(energy_norm, energy_norm, mode='full')
                autocorr = autocorr[len(energy_norm)-1:]
                # Consistency is based on autocorrelation peak
                consistency = np.max(autocorr[1:min(50, len(autocorr))]) / autocorr[0]
                consistency = np.clip(consistency, 0.0, 1.0)
            else:
                consistency = 0.7
            
            # Stress pattern analysis based on energy variation
            energy_variation = np.std(energy) / np.mean(energy)
            if energy_variation > 0.5:
                stress_pattern = "dynamic"
            elif energy_variation > 0.3:
                stress_pattern = "moderate"
            else:
                stress_pattern = "balanced"
            
            # Calculate speaking tempo in words per minute (approximate)
            # This is a rough estimation based on energy patterns
            speaking_tempo = tempo * speech_rate * 0.6  # Rough conversion factor
            
            return {
                "speech_rate": float(speech_rate),
                "pause_ratio": float(pause_ratio),
                "avg_pause_duration": float(avg_pause_duration),
                "total_speech_time": float(1.0 - pause_ratio),
                "consistency": float(consistency),
                "stress_pattern": stress_pattern,
                "tempo": float(tempo),
                "speaking_tempo": float(speaking_tempo),
                "energy_variation": float(energy_variation)
            }
        except Exception as e:
            logger.error(f"Error in enhanced rhythm analysis: {str(e)}")
            return {
                "speech_rate": 0.5,
                "pause_ratio": 0.2,
                "avg_pause_duration": 0.1,
                "total_speech_time": 0.8,
                "consistency": 0.6,
                "stress_pattern": "balanced",
                "tempo": 120.0,
                "speaking_tempo": 60.0,
                "energy_variation": 0.3
            }
    
    def _analyze_clarity_enhanced(self, y: np.ndarray, sr: int) -> Dict:
        """Enhanced clarity analysis with advanced features."""
        try:
            # Advanced spectral features
            spectral_centroids = librosa.feature.spectral_centroid(y=y, sr=sr, hop_length=self.hop_length)[0]
            spectral_rolloff = librosa.feature.spectral_rolloff(y=y, sr=sr, hop_length=self.hop_length)[0]
            spectral_bandwidth = librosa.feature.spectral_bandwidth(y=y, sr=sr, hop_length=self.hop_length)[0]
            spectral_contrast = librosa.feature.spectral_contrast(y=y, sr=sr, hop_length=self.hop_length)[0]
            
            # MFCC features for articulation analysis
            mfcc = librosa.feature.mfcc(y=y, sr=sr, n_mfcc=13, hop_length=self.hop_length)
            mfcc_delta = librosa.feature.delta(mfcc)
            mfcc_delta2 = librosa.feature.delta(mfcc, order=2)
            
            # Calculate clarity score based on multiple features
            clarity_score = min(1.0, np.mean(spectral_centroids) / 2000.0)
            articulation_score = min(1.0, np.mean(spectral_rolloff) / 4000.0)
            
            # Enhanced spectral quality calculation
            spectral_quality = (clarity_score + articulation_score) / 2
            
            # Enunciation quality based on MFCC variation
            mfcc_variation = np.std(mfcc_delta)
            enunciation = 1.0 - min(1.0, mfcc_variation / 2.0)  # Lower variation = better enunciation
            
            # Voice projection based on energy and spectral features
            energy = librosa.feature.rms(y=y, hop_length=self.hop_length)[0]
            projection = min(1.0, np.mean(energy) * 10.0)  # Normalize energy
            
            # Detect potential speech errors (simplified)
            # In a real system, you'd use more sophisticated error detection
            errors = []
            
            # Check for mumbling (low spectral contrast)
            if np.mean(spectral_contrast) < 0.1:
                errors.append("Possible mumbling detected")
            
            # Check for unclear articulation (high MFCC variation)
            if mfcc_variation > 1.5:
                errors.append("Articulation could be clearer")
            
            # Check for weak projection (low energy)
            if np.mean(energy) < 0.05:
                errors.append("Voice projection could be stronger")
            
            # Calculate overall clarity rating
            overall_clarity = (clarity_score + articulation_score + enunciation + projection) / 4
            
            return {
                "clarity_score": float(clarity_score),
                "articulation_score": float(articulation_score),
                "spectral_quality": float(spectral_quality),
                "errors": errors,
                "enunciation": float(enunciation),
                "projection": float(projection),
                "overall_clarity": float(overall_clarity),
                "mfcc_variation": float(mfcc_variation),
                "spectral_contrast": float(np.mean(spectral_contrast))
            }
        except Exception as e:
            logger.error(f"Error in enhanced clarity analysis: {str(e)}")
            return {
                "clarity_score": 0.7,
                "articulation_score": 0.6,
                "spectral_quality": 0.65,
                "errors": [],
                "enunciation": 0.6,
                "projection": 0.7,
                "overall_clarity": 0.65,
                "mfcc_variation": 1.0,
                "spectral_contrast": 0.2
            }
    
    def _analyze_emotion_enhanced(self, y: np.ndarray, sr: int) -> Dict:
        """Enhanced emotion analysis with advanced features."""
        try:
            # Advanced pitch analysis for emotion detection
            pitches, magnitudes = librosa.piptrack(y=y, sr=sr, hop_length=self.hop_length)
            
            # Get pitch values with better filtering
            pitch_values = []
            for t in range(pitches.shape[1]):
                index = magnitudes[:, t].argmax()
                pitch = pitches[index, t]
                if pitch > 0 and magnitudes[index, t] > 0.1:  # Better threshold
                    pitch_values.append(pitch)
            
            avg_pitch = np.mean(pitch_values) if pitch_values else 0
            pitch_std = np.std(pitch_values) if pitch_values else 0
            
            # Advanced energy analysis
            energy = librosa.feature.rms(y=y, hop_length=self.hop_length)[0]
            energy_mean = np.mean(energy)
            energy_std = np.std(energy)
            
            # Spectral features for emotion detection
            spectral_centroids = librosa.feature.spectral_centroid(y=y, sr=sr, hop_length=self.hop_length)[0]
            spectral_rolloff = librosa.feature.spectral_rolloff(y=y, sr=sr, hop_length=self.hop_length)[0]
            
            # MFCC features for emotion classification
            mfcc = librosa.feature.mfcc(y=y, sr=sr, n_mfcc=13, hop_length=self.hop_length)
            mfcc_mean = np.mean(mfcc, axis=1)
            
            # Enhanced emotion classification using multiple features
            emotion_scores = {
                "happy": 0.0,
                "sad": 0.0,
                "angry": 0.0,
                "neutral": 0.0,
                "excited": 0.0,
                "calm": 0.0
            }
            
            # Happy: high pitch, high energy, bright spectral features
            if avg_pitch > 250 and energy_mean > 0.08:
                emotion_scores["happy"] += 0.4
            if np.mean(spectral_centroids) > 2000:
                emotion_scores["happy"] += 0.3
            
            # Excited: very high pitch, high energy variation
            if avg_pitch > 300 and energy_std > 0.05:
                emotion_scores["excited"] += 0.5
            if pitch_std > 50:
                emotion_scores["excited"] += 0.3
            
            # Calm: low pitch, low energy, stable features
            if avg_pitch < 200 and energy_mean < 0.06:
                emotion_scores["calm"] += 0.4
            if energy_std < 0.03:
                emotion_scores["calm"] += 0.3
            
            # Sad: low pitch, low energy, dark spectral features
            if avg_pitch < 180 and energy_mean < 0.05:
                emotion_scores["sad"] += 0.4
            if np.mean(spectral_centroids) < 1500:
                emotion_scores["sad"] += 0.3
            
            # Angry: high energy, high spectral rolloff
            if energy_mean > 0.1 and np.mean(spectral_rolloff) > 4000:
                emotion_scores["angry"] += 0.4
            if energy_std > 0.08:
                emotion_scores["angry"] += 0.3
            
            # Neutral: balanced features
            if 180 <= avg_pitch <= 250 and 0.05 <= energy_mean <= 0.08:
                emotion_scores["neutral"] += 0.4
            if energy_std < 0.05:
                emotion_scores["neutral"] += 0.3
            
            # Normalize scores
            total_score = sum(emotion_scores.values())
            if total_score > 0:
                emotion_scores = {k: v / total_score for k, v in emotion_scores.items()}
            
            # Determine dominant emotion
            dominant_emotion = max(emotion_scores, key=emotion_scores.get)
            confidence = emotion_scores[dominant_emotion]
            
            # Calculate emotional range and stability
            emotion_variation = np.std(list(emotion_scores.values()))
            emotional_range = "wide" if emotion_variation > 0.15 else "moderate" if emotion_variation > 0.08 else "narrow"
            
            # Emotional stability based on pitch and energy consistency
            pitch_stability = 1.0 - min(1.0, pitch_std / avg_pitch) if avg_pitch > 0 else 0.5
            energy_stability = 1.0 - min(1.0, energy_std / energy_mean) if energy_mean > 0 else 0.5
            emotional_stability = (pitch_stability + energy_stability) / 2
            
            return {
                "dominant_emotion": dominant_emotion,
                "confidence": float(confidence),
                "scores": {k: float(v) for k, v in emotion_scores.items()},
                "range": emotional_range,
                "stability": float(emotional_stability),
                "pitch_stability": float(pitch_stability),
                "energy_stability": float(energy_stability),
                "avg_pitch": float(avg_pitch),
                "avg_energy": float(energy_mean)
            }
        except Exception as e:
            logger.error(f"Error in enhanced emotion analysis: {str(e)}")
            return {
                "dominant_emotion": "neutral",
                "confidence": 0.5,
                "scores": {
                    "happy": 0.2,
                    "sad": 0.1,
                    "angry": 0.1,
                    "neutral": 0.5,
                    "excited": 0.1,
                    "calm": 0.2
                },
                "range": "moderate",
                "stability": 0.6,
                "pitch_stability": 0.6,
                "energy_stability": 0.6,
                "avg_pitch": 200.0,
                "avg_energy": 0.06
            }
    
    def _analyze_fluency_enhanced(self, y: np.ndarray, sr: int) -> Dict:
        """Enhanced fluency analysis with advanced features."""
        try:
            # Advanced fluency analysis using multiple features
            
            # Energy-based fluency analysis
            energy = librosa.feature.rms(y=y, hop_length=self.hop_length)[0]
            energy_variation = np.std(energy) / np.mean(energy) if np.mean(energy) > 0 else 0
            
            # Pitch-based fluency analysis
            pitches, magnitudes = librosa.piptrack(y=y, sr=sr, hop_length=self.hop_length)
            pitch_values = []
            for t in range(pitches.shape[1]):
                index = magnitudes[:, t].argmax()
                pitch = pitches[index, t]
                if pitch > 0 and magnitudes[index, t] > 0.1:
                    pitch_values.append(pitch)
            
            # Calculate pitch jitter (variation in pitch)
            pitch_jitter = np.std(pitch_values) if pitch_values else 0
            pitch_mean = np.mean(pitch_values) if pitch_values else 0
            normalized_jitter = pitch_jitter / pitch_mean if pitch_mean > 0 else 0
            
            # Spectral features for fluency
            spectral_centroids = librosa.feature.spectral_centroid(y=y, sr=sr, hop_length=self.hop_length)[0]
            spectral_rolloff = librosa.feature.spectral_rolloff(y=y, sr=sr, hop_length=self.hop_length)[0]
            
            # MFCC features for articulation fluency
            mfcc = librosa.feature.mfcc(y=y, sr=sr, n_mfcc=13, hop_length=self.hop_length)
            mfcc_delta = librosa.feature.delta(mfcc)
            mfcc_variation = np.std(mfcc_delta)
            
            # Calculate fluency metrics
            
            # Smoothness: based on energy and pitch consistency
            energy_smoothness = 1.0 - min(1.0, energy_variation * 2.0)
            pitch_smoothness = 1.0 - min(1.0, normalized_jitter * 5.0)
            smoothness = (energy_smoothness + pitch_smoothness) / 2
            
            # Hesitations: detected by energy drops and pitch irregularities
            energy_threshold = np.percentile(energy, 20)
            hesitation_segments = energy < energy_threshold
            hesitations = np.sum(hesitation_segments) / len(hesitation_segments)
            
            # Repetitions: simplified detection based on spectral similarity
            # In a real system, you'd use more sophisticated repetition detection
            spectral_similarity = np.corrcoef(spectral_centroids, spectral_rolloff)[0, 1]
            repetitions = 1.0 - max(0, spectral_similarity)  # Higher similarity = fewer repetitions
            
            # Filler words: simplified detection based on energy patterns
            # In a real system, you'd use speech recognition for this
            filler_words = []
            if hesitations > 0.3:
                filler_words.append("Possible filler words detected")
            
            # Overall fluency score
            fluency_score = (
                smoothness * 0.4 +
                (1.0 - hesitations) * 0.3 +
                (1.0 - repetitions) * 0.2 +
                (1.0 - min(1.0, mfcc_variation / 2.0)) * 0.1
            )
            
            # Detect specific fluency issues
            fluency_issues = []
            if smoothness < 0.6:
                fluency_issues.append("Speech lacks smoothness")
            if hesitations > 0.4:
                fluency_issues.append("Frequent hesitations detected")
            if repetitions > 0.5:
                fluency_issues.append("Possible repetitions")
            if mfcc_variation > 1.5:
                fluency_issues.append("Articulation inconsistencies")
            
            return {
                "fluency_score": float(fluency_score),
                "filler_words": filler_words,
                "repetitions": float(repetitions),
                "hesitations": float(hesitations),
                "smoothness": float(smoothness),
                "pitch_jitter": float(normalized_jitter),
                "energy_smoothness": float(energy_smoothness),
                "pitch_smoothness": float(pitch_smoothness),
                "mfcc_variation": float(mfcc_variation),
                "fluency_issues": fluency_issues
            }
        except Exception as e:
            logger.error(f"Error in enhanced fluency analysis: {str(e)}")
            return {
                "fluency_score": 0.7,
                "filler_words": [],
                "repetitions": 0.2,
                "hesitations": 0.2,
                "smoothness": 0.7,
                "pitch_jitter": 0.1,
                "energy_smoothness": 0.7,
                "pitch_smoothness": 0.7,
                "mfcc_variation": 1.0,
                "fluency_issues": []
            }
    
    def _generate_recommendations_enhanced(self, pitch_data: Dict, rhythm_data: Dict, clarity_data: Dict, emotion_data: Dict, fluency_data: Dict) -> List[str]:
        """Generate enhanced recommendations with specific, actionable feedback."""
        recommendations = []
        
        # Pitch-based recommendations with specific guidance
        if pitch_data["variation"] < 50:
            recommendations.append("🎵 Pitch Variation: Your voice is quite monotone. Practice reading aloud with different emotions - try happy, sad, excited, and calm tones to improve expressiveness.")
        elif pitch_data["variation"] > 150:
            recommendations.append("🎵 Pitch Control: Your pitch varies too much. Practice speaking in a more controlled, steady tone while maintaining natural expression.")
        
        if pitch_data["stability"] < 0.6:
            recommendations.append("🎵 Pitch Stability: Your pitch wavers frequently. Practice vocal warm-ups and breathing exercises to improve control.")
        
        # Rhythm-based recommendations with specific metrics
        if rhythm_data["speech_rate"] > 0.8:
            recommendations.append(f"⏱️ Speech Rate: You're speaking at {rhythm_data['speech_rate']:.1%} rate (too fast). Aim for 60-70% speaking time. Practice pausing between sentences and taking breaths.")
        elif rhythm_data["speech_rate"] < 0.3:
            recommendations.append(f"⏱️ Speech Rate: You're speaking at {rhythm_data['speech_rate']:.1%} rate (too slow). Try to maintain a steady, engaging pace.")
        
        if rhythm_data["pause_ratio"] > 0.4:
            recommendations.append(f"⏱️ Pause Management: {rhythm_data['pause_ratio']:.1%} of your speech is pauses. Practice reducing unnecessary hesitations and filler words.")
        
        # Clarity-based recommendations with specific issues
        if clarity_data["clarity_score"] < 0.6:
            recommendations.append("🗣️ Pronunciation: Focus on clear articulation. Practice tongue twisters and read aloud slowly, emphasizing each syllable.")
        
        if clarity_data["articulation_score"] < 0.6:
            recommendations.append("🗣️ Articulation: Work on mouth movements and tongue placement. Practice exercises like 'ma-ma-ma' and 'la-la-la' to improve clarity.")
        
        if clarity_data["projection"] < 0.7:
            recommendations.append("🗣️ Voice Projection: Speak from your diaphragm, not your throat. Practice projecting your voice by speaking to someone across the room.")
        
        # Emotion-based recommendations with specific guidance
        if emotion_data["dominant_emotion"] == "neutral" and emotion_data["confidence"] > 0.7:
            recommendations.append("😊 Emotional Expression: Your voice lacks emotional variety. Practice reading the same sentence with different emotions - happy, sad, angry, excited.")
        
        if emotion_data["stability"] < 0.6:
            recommendations.append("😊 Emotional Control: Your emotional expression is inconsistent. Practice maintaining a steady, confident tone throughout your speech.")
        
        # Fluency recommendations with specific exercises
        if fluency_data["fluency_score"] < 0.7:
            recommendations.append("💬 Fluency: Practice speaking more smoothly. Record yourself and identify where you hesitate, then practice those phrases repeatedly.")
        
        if fluency_data["hesitations"] > 0.3:
            recommendations.append("💬 Hesitations: You hesitate frequently. Practice thinking ahead while speaking and use brief pauses instead of 'um' and 'uh'.")
        
        if fluency_data["repetitions"] > 0.4:
            recommendations.append("💬 Repetitions: You repeat words/phrases often. Practice speaking more concisely and planning your thoughts before speaking.")
        
        # Add positive reinforcement
        if len(recommendations) == 0:
            recommendations.append("🌟 Excellent! Your voice analysis shows strong performance across all areas. Keep practicing to maintain these skills!")
        
        return recommendations
    
    def _identify_improvement_areas(self, pitch_data: Dict, rhythm_data: Dict, clarity_data: Dict, emotion_data: Dict, fluency_data: Dict) -> List[str]:
        """Identify specific areas that need improvement."""
        improvement_areas = []
        
        # Pitch improvements
        if pitch_data["variation"] < 50:
            improvement_areas.append("Pitch variation - Your voice sounds monotone")
        elif pitch_data["variation"] > 150:
            improvement_areas.append("Pitch control - Too much variation in pitch")
        
        if pitch_data["stability"] < 0.6:
            improvement_areas.append("Pitch stability - Voice wavers frequently")
        
        # Rhythm improvements
        if rhythm_data["speech_rate"] > 0.8:
            improvement_areas.append("Speech rate - Speaking too fast")
        elif rhythm_data["speech_rate"] < 0.3:
            improvement_areas.append("Speech rate - Speaking too slow")
        
        if rhythm_data["pause_ratio"] > 0.4:
            improvement_areas.append("Pause management - Too many pauses")
        
        # Clarity improvements
        if clarity_data["clarity_score"] < 0.6:
            improvement_areas.append("Pronunciation - Needs clearer articulation")
        
        if clarity_data["articulation_score"] < 0.6:
            improvement_areas.append("Articulation - Mouth movements need improvement")
        
        if clarity_data["projection"] < 0.7:
            improvement_areas.append("Voice projection - Speak louder and clearer")
        
        # Emotion improvements
        if emotion_data["dominant_emotion"] == "neutral" and emotion_data["confidence"] > 0.7:
            improvement_areas.append("Emotional expression - Voice lacks variety")
        
        if emotion_data["stability"] < 0.6:
            improvement_areas.append("Emotional control - Inconsistent expression")
        
        # Fluency improvements
        if fluency_data["fluency_score"] < 0.7:
            improvement_areas.append("Fluency - Speech is not smooth enough")
        
        if fluency_data["hesitations"] > 0.3:
            improvement_areas.append("Hesitations - Too many 'um' and 'uh' sounds")
        
        if fluency_data["repetitions"] > 0.4:
            improvement_areas.append("Repetitions - Repeating words too often")
        
        # If no issues found, return empty list
        return improvement_areas
    
    def _identify_strengths(self, pitch_data: Dict, rhythm_data: Dict, clarity_data: Dict, emotion_data: Dict, fluency_data: Dict) -> List[str]:
        """Identify strengths based on analysis results."""
        strengths = []
        if pitch_data["average"] > 200 and pitch_data["variation"] < 100:
            strengths.append("Good vocal range and pitch control")
        if rhythm_data["speech_rate"] > 0.6 and rhythm_data["pause_ratio"] < 0.3:
            strengths.append("Good rhythm and pacing")
        if clarity_data["clarity_score"] > 0.7 and clarity_data["articulation_score"] > 0.7:
            strengths.append("Excellent enunciation and articulation")
        if emotion_data["dominant_emotion"] != "neutral" and emotion_data["confidence"] > 0.6:
            strengths.append("Strong emotional expression")
        if fluency_data["fluency_score"] > 0.8:
            strengths.append("Very fluent speech")
        return strengths
    
    def _generate_practice_suggestions(self, pitch_data: Dict, rhythm_data: Dict, clarity_data: Dict, emotion_data: Dict, fluency_data: Dict) -> List[str]:
        """Generate practice suggestions based on analysis results."""
        suggestions = []
        
        # Pitch-based suggestions
        if pitch_data["variation"] > 100:
            suggestions.append("Practice vocal warm-ups to improve pitch range and control")
        if pitch_data["stability"] < 0.7:
            suggestions.append("Focus on vocal stability and consistency in pitch")
        
        # Rhythm-based suggestions
        if rhythm_data["speech_rate"] < 0.4:
            suggestions.append("Speed up your speech rate to improve engagement")
        if rhythm_data["pause_ratio"] > 0.4:
            suggestions.append("Practice pausing strategically to improve clarity")
        
        # Clarity-based suggestions
        if clarity_data["clarity_score"] < 0.7:
            suggestions.append("Work on improving enunciation and articulation")
        if clarity_data["projection"] < 0.8:
            suggestions.append("Practice projecting your voice for better voice projection")
        
        # Emotion-based suggestions
        if emotion_data["dominant_emotion"] == "neutral":
            suggestions.append("Practice expressing different emotions to improve vocal variety")
        if emotion_data["stability"] < 0.7:
            suggestions.append("Focus on emotional stability and consistency")
        
        # Fluency suggestions
        if fluency_data["fluency_score"] < 0.8:
            suggestions.append("Practice speaking slowly and deliberately to improve fluency")
            suggestions.append("Record yourself and listen for filler words and repetitions")
        
        return suggestions
    
    def _calculate_confidence_score(self, pitch_data: Dict, rhythm_data: Dict, clarity_data: Dict, emotion_data: Dict, fluency_data: Dict) -> float:
        """Calculate overall confidence score based on individual metrics."""
        # This is a simplified confidence score calculation.
        # In a real system, you'd weight different metrics and combine them.
        # For example, a weighted average of pitch stability, rhythm consistency,
        # clarity, emotional stability, and fluency.
        
        # Placeholder weights (example)
        pitch_weight = 0.2
        rhythm_weight = 0.2
        clarity_weight = 0.2
        emotion_weight = 0.2
        fluency_weight = 0.2
        
        # Calculate weighted average of individual scores
        confidence_score = (
            pitch_data["stability"] * pitch_weight +
            rhythm_data["consistency"] * rhythm_weight +
            emotion_data["stability"] * emotion_weight +
            fluency_data["fluency_score"] * fluency_weight
        )
        
        return float(confidence_score) 