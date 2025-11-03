import pandas as pd
import numpy as np
from datetime import datetime
from typing import List, Dict
import json
import io
import logging

logger = logging.getLogger(__name__)

class DataExporter:
    """Handles export of analysis data to PDF and CSV formats"""
    
    def __init__(self):
        pass
    
    def export_to_csv(self, recordings: List[Dict], export_request: Dict) -> str:
        """Export analysis data to CSV format"""
        try:
            # Prepare data for CSV
            csv_data = []
            
            for recording in recordings:
                analysis_result = recording.get('analysis_result', {})
                audio_metrics = analysis_result.get('audio_metrics', {})
                
                # Basic recording info
                row = {
                    'Recording ID': str(recording.get('_id', '')),
                    'Date': recording.get('created_at', ''),
                    'Session Type': recording.get('session_type', ''),
                    'Topic': recording.get('topic', ''),
                    'Duration (seconds)': analysis_result.get('duration', 0),
                }
                
                # Language detection
                if export_request.get('include_transcriptions', True):
                    row.update({
                        'Detected Language': recording.get('detected_language', ''),
                        'Language Confidence': recording.get('language_confidence', 0),
                        'Transcription': recording.get('transcription', ''),
                    })
                
                # Voice cloning detection
                if export_request.get('include_voice_cloning', True):
                    row.update({
                        'AI Generated': recording.get('voice_cloning_detected', 'human'),
                        'Voice Cloning Score': recording.get('voice_cloning_score', 0),
                    })
                
                # Audio metrics
                clarity_data = audio_metrics.get('clarity', {})
                confidence_data = audio_metrics.get('confidence', {})
                speech_rate_data = audio_metrics.get('speech_rate', {})
                emotion_data = audio_metrics.get('emotion', {})
                
                row.update({
                    'Clarity Score': clarity_data.get('clarity_score', 0),
                    'Confidence Score': confidence_data.get('confidence_score', 0),
                    'Speech Rate (WPM)': speech_rate_data.get('words_per_minute', 0),
                    'Dominant Emotion': emotion_data.get('dominant_emotion', ''),
                    'Emotion Confidence': emotion_data.get('emotion_confidence', 0),
                })
                
                csv_data.append(row)
            
            # Create DataFrame and export
            df = pd.DataFrame(csv_data)
            
            # Generate filename with timestamp
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"vocal_iq_analysis_{timestamp}.csv"
            
            # Convert to CSV string
            csv_buffer = io.StringIO()
            df.to_csv(csv_buffer, index=False)
            csv_content = csv_buffer.getvalue()
            csv_buffer.close()
            
            logger.info(f"CSV export completed: {len(csv_data)} records")
            return csv_content
            
        except Exception as e:
            logger.error(f"CSV export error: {e}")
            raise
    
    def export_to_pdf(self, recordings: List[Dict], user_info: Dict, export_request: Dict) -> bytes:
        """Export analysis data to PDF format"""
        try:
            # For now, return a simple text-based PDF
            # In production, you'd use reportlab for proper PDF generation
            buffer = io.BytesIO()
            
            # Create a simple text report
            report_content = f"""
Vocal IQ Analysis Report
========================

User: {user_info.get('username', 'Unknown')}
Email: {user_info.get('email', 'Unknown')}
Report Generated: {datetime.now().strftime('%B %d, %Y at %I:%M %p')}

Summary Statistics:
- Total Recordings: {len(recordings)}
- Average Clarity: {self._calculate_avg_clarity(recordings):.2f}
- Average Confidence: {self._calculate_avg_confidence(recordings):.2f}
- Average Speech Rate: {self._calculate_avg_speech_rate(recordings):.1f} WPM

Language Analysis:
{self._format_language_analysis(recordings)}

Voice Cloning Detection:
{self._format_voice_cloning_analysis(recordings)}

Detailed Analysis:
{self._format_detailed_analysis(recordings, export_request)}
            """
            
            buffer.write(report_content.encode('utf-8'))
            buffer.seek(0)
            
            logger.info(f"PDF export completed: {len(recordings)} records")
            return buffer.getvalue()
            
        except Exception as e:
            logger.error(f"PDF export error: {e}")
            raise
    
    def _calculate_avg_clarity(self, recordings: List[Dict]) -> float:
        """Calculate average clarity score"""
        clarity_scores = []
        for recording in recordings:
            analysis_result = recording.get('analysis_result', {})
            audio_metrics = analysis_result.get('audio_metrics', {})
            clarity_data = audio_metrics.get('clarity', {})
            if 'clarity_score' in clarity_data:
                clarity_scores.append(clarity_data['clarity_score'])
        return np.mean(clarity_scores) if clarity_scores else 0.0
    
    def _calculate_avg_confidence(self, recordings: List[Dict]) -> float:
        """Calculate average confidence score"""
        confidence_scores = []
        for recording in recordings:
            analysis_result = recording.get('analysis_result', {})
            audio_metrics = analysis_result.get('audio_metrics', {})
            confidence_data = audio_metrics.get('confidence', {})
            if 'confidence_score' in confidence_data:
                confidence_scores.append(confidence_data['confidence_score'])
        return np.mean(confidence_scores) if confidence_scores else 0.0
    
    def _calculate_avg_speech_rate(self, recordings: List[Dict]) -> float:
        """Calculate average speech rate"""
        speech_rates = []
        for recording in recordings:
            analysis_result = recording.get('analysis_result', {})
            audio_metrics = analysis_result.get('audio_metrics', {})
            speech_rate_data = audio_metrics.get('speech_rate', {})
            if 'words_per_minute' in speech_rate_data:
                speech_rates.append(speech_rate_data['words_per_minute'])
        return np.mean(speech_rates) if speech_rates else 0.0
    
    def _format_language_analysis(self, recordings: List[Dict]) -> str:
        """Format language analysis for report"""
        language_counts = {}
        for recording in recordings:
            lang = recording.get('detected_language', 'unknown')
            language_counts[lang] = language_counts.get(lang, 0) + 1
        
        if not language_counts:
            return "No language data available"
        
        result = ""
        for lang, count in language_counts.items():
            percentage = (count / len(recordings)) * 100
            result += f"- {lang}: {count} recordings ({percentage:.1f}%)\n"
        
        return result
    
    def _format_voice_cloning_analysis(self, recordings: List[Dict]) -> str:
        """Format voice cloning analysis for report"""
        ai_count = 0
        human_count = 0
        scores = []
        
        for recording in recordings:
            detection = recording.get('voice_cloning_detected', 'human')
            score = recording.get('voice_cloning_score', 0)
            
            if detection == 'ai':
                ai_count += 1
            else:
                human_count += 1
            
            scores.append(score)
        
        avg_score = np.mean(scores) if scores else 0.0
        
        return f"""
- Human Voice: {human_count} recordings
- AI Generated: {ai_count} recordings
- Average Cloning Score: {avg_score:.3f}
        """
    
    def _format_detailed_analysis(self, recordings: List[Dict], export_request: Dict) -> str:
        """Format detailed analysis for report"""
        if not recordings:
            return "No recordings available"
        
        # Limit to first 10 recordings for readability
        limited_recordings = recordings[:10]
        
        result = ""
        for i, recording in enumerate(limited_recordings, 1):
            analysis_result = recording.get('analysis_result', {})
            audio_metrics = analysis_result.get('audio_metrics', {})
            
            clarity_data = audio_metrics.get('clarity', {})
            confidence_data = audio_metrics.get('confidence', {})
            speech_rate_data = audio_metrics.get('speech_rate', {})
            
            result += f"""
Recording {i}:
- Date: {recording.get('created_at', '')[:10]}
- Type: {recording.get('session_type', '')}
- Clarity: {clarity_data.get('clarity_score', 0):.1f}
- Confidence: {confidence_data.get('confidence_score', 0):.1f}
- Speech Rate: {speech_rate_data.get('words_per_minute', 0):.0f} WPM
"""
            
            if export_request.get('include_transcriptions', True):
                result += f"- Language: {recording.get('detected_language', '')}\n"
            if export_request.get('include_voice_cloning', True):
                result += f"- AI Detection: {recording.get('voice_cloning_detected', 'human')}\n"
        
        if len(recordings) > 10:
            result += f"\nNote: Showing first 10 of {len(recordings)} recordings"
        
        return result

class ChartGenerator:
    """Generates comparison charts and visualizations"""
    
    def __init__(self):
        pass
    
    def generate_comparison_chart(self, recordings: List[Dict]) -> bytes:
        """Generate a comparison chart showing progress over time"""
        try:
            if not recordings:
                return b""
            
            # Sort recordings by date
            sorted_recordings = sorted(recordings, key=lambda x: x.get('created_at', datetime.now()))
            
            dates = []
            clarity_scores = []
            confidence_scores = []
            speech_rates = []
            
            for recording in sorted_recordings:
                analysis_result = recording.get('analysis_result', {})
                audio_metrics = analysis_result.get('audio_metrics', {})
                
                dates.append(recording.get('created_at', datetime.now()))
                
                clarity_data = audio_metrics.get('clarity', {})
                confidence_data = audio_metrics.get('confidence', {})
                speech_rate_data = audio_metrics.get('speech_rate', {})
                
                clarity_scores.append(clarity_data.get('clarity_score', 0))
                confidence_scores.append(confidence_data.get('confidence_score', 0))
                speech_rates.append(speech_rate_data.get('words_per_minute', 0))
            
            # Create a simple text-based chart representation
            chart_data = f"""
Progress Chart Data:
===================

Dates: {[str(d)[:10] for d in dates]}
Clarity Scores: {clarity_scores}
Confidence Scores: {confidence_scores}
Speech Rates: {speech_rates}

Chart Summary:
- Average Clarity: {np.mean(clarity_scores):.2f}
- Average Confidence: {np.mean(confidence_scores):.2f}
- Average Speech Rate: {np.mean(speech_rates):.1f} WPM
- Total Recordings: {len(recordings)}
            """
            
            return chart_data.encode('utf-8')
            
        except Exception as e:
            logger.error(f"Chart generation error: {e}")
            return b""
    
    def generate_language_chart(self, recordings: List[Dict]) -> bytes:
        """Generate a pie chart showing language distribution"""
        try:
            if not recordings:
                return b""
            
            language_counts = {}
            for recording in recordings:
                lang = recording.get('detected_language', 'unknown')
                language_counts[lang] = language_counts.get(lang, 0) + 1
            
            if not language_counts:
                return b""
            
            # Create a simple text-based chart representation
            chart_data = f"""
Language Distribution Chart:
============================

Language Counts:
"""
            for lang, count in language_counts.items():
                percentage = (count / len(recordings)) * 100
                chart_data += f"- {lang}: {count} ({percentage:.1f}%)\n"
            
            chart_data += f"\nTotal Recordings: {len(recordings)}"
            
            return chart_data.encode('utf-8')
            
        except Exception as e:
            logger.error(f"Language chart generation error: {e}")
            return b"" 