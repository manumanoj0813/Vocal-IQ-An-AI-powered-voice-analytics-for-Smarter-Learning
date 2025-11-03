from reportlab.lib.pagesizes import letter, A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
from datetime import datetime
from typing import Dict, Any
import io
import logging

logger = logging.getLogger(__name__)

class VoiceAnalysisPDFGenerator:
    """Generates PDF reports for voice analysis results"""
    
    def __init__(self):
        self.styles = getSampleStyleSheet()
        self._setup_custom_styles()
    
    def _setup_custom_styles(self):
        """Setup custom paragraph styles for the PDF"""
        # Title style
        self.styles.add(ParagraphStyle(
            name='CustomTitle',
            parent=self.styles['Heading1'],
            fontSize=24,
            spaceAfter=30,
            alignment=TA_CENTER,
            textColor=colors.HexColor('#7a3cff')
        ))
        
        # Section header style
        self.styles.add(ParagraphStyle(
            name='SectionHeader',
            parent=self.styles['Heading2'],
            fontSize=16,
            spaceAfter=12,
            spaceBefore=20,
            textColor=colors.HexColor('#4a5568')
        ))
        
        # Metric style
        self.styles.add(ParagraphStyle(
            name='Metric',
            parent=self.styles['Normal'],
            fontSize=12,
            spaceAfter=6,
            leftIndent=20
        ))
        
        # Recommendation style
        self.styles.add(ParagraphStyle(
            name='Recommendation',
            parent=self.styles['Normal'],
            fontSize=11,
            spaceAfter=8,
            leftIndent=20,
            textColor=colors.HexColor('#2d3748')
        ))
        
        # Score style
        self.styles.add(ParagraphStyle(
            name='Score',
            parent=self.styles['Normal'],
            fontSize=14,
            spaceAfter=6,
            alignment=TA_CENTER,
            textColor=colors.HexColor('#7a3cff')
        ))
    
    def generate_voice_analysis_pdf(self, analysis_data: Dict[str, Any], user_info: Dict[str, Any] = None) -> bytes:
        """Generate PDF report for voice analysis"""
        try:
            buffer = io.BytesIO()
            doc = SimpleDocTemplate(buffer, pagesize=A4, rightMargin=72, leftMargin=72, topMargin=72, bottomMargin=18)
            
            # Build the story (content)
            story = []
            
            # Title
            story.append(Paragraph("Vocal IQ - Voice Analysis Report", self.styles['CustomTitle']))
            story.append(Spacer(1, 20))
            
            # User info and metadata
            if user_info:
                story.append(Paragraph(f"<b>User:</b> {user_info.get('username', 'Unknown')}", self.styles['Normal']))
                story.append(Paragraph(f"<b>Email:</b> {user_info.get('email', 'Not provided')}", self.styles['Normal']))
            
            story.append(Paragraph(f"<b>Analysis Date:</b> {datetime.now().strftime('%B %d, %Y at %I:%M %p')}", self.styles['Normal']))
            story.append(Paragraph(f"<b>Session Type:</b> {analysis_data.get('metadata', {}).get('session_type', 'Practice')}", self.styles['Normal']))
            story.append(Paragraph(f"<b>Duration:</b> {analysis_data.get('audio_metrics', {}).get('duration', 0):.1f} seconds", self.styles['Normal']))
            story.append(Spacer(1, 20))
            
            # Overall Score
            confidence_score = analysis_data.get('audio_metrics', {}).get('confidence_score', 0)
            story.append(Paragraph("Overall Performance Score", self.styles['SectionHeader']))
            story.append(Paragraph(f"{confidence_score:.1%}", self.styles['Score']))
            story.append(Spacer(1, 20))
            
            # Audio Metrics
            audio_metrics = analysis_data.get('audio_metrics', {})
            story.append(Paragraph("Detailed Analysis", self.styles['SectionHeader']))
            
            # Pitch Analysis
            pitch_data = audio_metrics.get('pitch', {})
            story.append(Paragraph("🎵 Pitch Analysis", self.styles['SectionHeader']))
            pitch_table_data = [
                ['Metric', 'Value', 'Status'],
                ['Average Pitch', f"{pitch_data.get('average_pitch', 0):.1f} Hz", self._get_status_text(pitch_data.get('average_pitch', 0), 200, 300)],
                ['Pitch Variation', f"{pitch_data.get('pitch_variation', 0):.1f} Hz", self._get_status_text(pitch_data.get('pitch_variation', 0), 50, 100)],
                ['Pitch Stability', f"{pitch_data.get('pitch_stability', 0):.1%}", self._get_status_text(pitch_data.get('pitch_stability', 0), 0.7, 1.0)],
                ['Pitch Range', f"{pitch_data.get('range_min', 0):.1f} - {pitch_data.get('range_max', 0):.1f} Hz", 'Good' if pitch_data.get('range_max', 0) - pitch_data.get('range_min', 0) > 100 else 'Limited']
            ]
            story.append(self._create_table(pitch_table_data))
            story.append(Spacer(1, 15))
            
            # Rhythm Analysis
            rhythm_data = audio_metrics.get('rhythm', {})
            story.append(Paragraph("⏱️ Rhythm Analysis", self.styles['SectionHeader']))
            rhythm_table_data = [
                ['Metric', 'Value', 'Status'],
                ['Speech Rate', f"{rhythm_data.get('speech_rate', 0):.1%}", self._get_status_text(rhythm_data.get('speech_rate', 0), 0.6, 0.8)],
                ['Pause Ratio', f"{rhythm_data.get('pause_ratio', 0):.1%}", self._get_status_text(rhythm_data.get('pause_ratio', 0), 0.1, 0.3, reverse=True)],
                ['Average Pause Duration', f"{rhythm_data.get('average_pause_duration', 0):.2f} seconds", self._get_status_text(rhythm_data.get('average_pause_duration', 0), 0.5, 1.5)],
                ['Rhythm Consistency', f"{rhythm_data.get('rhythm_consistency', 0):.1%}", self._get_status_text(rhythm_data.get('rhythm_consistency', 0), 0.7, 1.0)]
            ]
            story.append(self._create_table(rhythm_table_data))
            story.append(Spacer(1, 15))
            
            # Clarity Analysis
            clarity_data = audio_metrics.get('clarity', {})
            story.append(Paragraph("🗣️ Clarity Analysis", self.styles['SectionHeader']))
            clarity_table_data = [
                ['Metric', 'Value', 'Status'],
                ['Clarity Score', f"{clarity_data.get('clarity_score', 0):.1%}", self._get_status_text(clarity_data.get('clarity_score', 0), 0.7, 1.0)],
                ['Pronunciation Score', f"{clarity_data.get('pronunciation_score', 0):.1%}", self._get_status_text(clarity_data.get('pronunciation_score', 0), 0.7, 1.0)],
                ['Enunciation Quality', f"{clarity_data.get('enunciation_quality', 0):.1%}", self._get_status_text(clarity_data.get('enunciation_quality', 0), 0.7, 1.0)],
                ['Voice Projection', f"{clarity_data.get('voice_projection', 0):.1%}", self._get_status_text(clarity_data.get('voice_projection', 0), 0.7, 1.0)]
            ]
            story.append(self._create_table(clarity_table_data))
            story.append(Spacer(1, 15))
            
            # Emotion Analysis
            emotion_data = audio_metrics.get('emotion', {})
            story.append(Paragraph("😊 Emotion Analysis", self.styles['SectionHeader']))
            emotion_table_data = [
                ['Metric', 'Value', 'Status'],
                ['Dominant Emotion', emotion_data.get('dominant_emotion', 'Neutral').title(), 'Good' if emotion_data.get('dominant_emotion', 'neutral') != 'neutral' else 'Neutral'],
                ['Emotion Confidence', f"{emotion_data.get('emotion_confidence', 0):.1%}", self._get_status_text(emotion_data.get('emotion_confidence', 0), 0.6, 1.0)],
                ['Emotional Range', emotion_data.get('emotional_range', 'Moderate').title(), 'Good'],
                ['Emotional Stability', f"{emotion_data.get('emotional_stability', 0):.1%}", self._get_status_text(emotion_data.get('emotional_stability', 0), 0.7, 1.0)]
            ]
            story.append(self._create_table(emotion_table_data))
            story.append(Spacer(1, 15))
            
            # Fluency Analysis
            fluency_data = audio_metrics.get('fluency', {})
            story.append(Paragraph("💬 Fluency Analysis", self.styles['SectionHeader']))
            fluency_table_data = [
                ['Metric', 'Value', 'Status'],
                ['Fluency Score', f"{fluency_data.get('fluency_score', 0):.1%}", self._get_status_text(fluency_data.get('fluency_score', 0), 0.7, 1.0)],
                ['Hesitations', f"{fluency_data.get('hesitations', 0):.1%}", self._get_status_text(fluency_data.get('hesitations', 0), 0.1, 0.3, reverse=True)],
                ['Repetitions', f"{fluency_data.get('repetitions', 0):.1%}", self._get_status_text(fluency_data.get('repetitions', 0), 0.1, 0.3, reverse=True)],
                ['Smoothness', f"{fluency_data.get('smoothness', 0):.1%}", self._get_status_text(fluency_data.get('smoothness', 0), 0.7, 1.0)]
            ]
            story.append(self._create_table(fluency_table_data))
            story.append(Spacer(1, 20))
            
            # Transcription
            transcription_data = analysis_data.get('transcription', {})
            if transcription_data.get('full_text'):
                story.append(Paragraph("📝 Transcription", self.styles['SectionHeader']))
                story.append(Paragraph(f"<i>\"{transcription_data.get('full_text', '')}\"</i>", self.styles['Normal']))
                story.append(Paragraph(f"Word Count: {transcription_data.get('word_count', 0)}", self.styles['Normal']))
                story.append(Spacer(1, 20))
            
            # Recommendations
            recommendations = analysis_data.get('recommendations', {})
            story.append(Paragraph("💡 Recommendations & Feedback", self.styles['SectionHeader']))
            
            # Key Points
            key_points = recommendations.get('key_points', [])
            if key_points:
                story.append(Paragraph("<b>Key Areas for Improvement:</b>", self.styles['Normal']))
                for point in key_points:
                    story.append(Paragraph(f"• {point}", self.styles['Recommendation']))
                story.append(Spacer(1, 15))
            
            # Strengths
            strengths = recommendations.get('strengths', [])
            if strengths:
                story.append(Paragraph("<b>Your Strengths:</b>", self.styles['Normal']))
                for strength in strengths:
                    story.append(Paragraph(f"✓ {strength}", self.styles['Recommendation']))
                story.append(Spacer(1, 15))
            
            # Practice Suggestions
            practice_suggestions = recommendations.get('practice_suggestions', [])
            if practice_suggestions:
                story.append(Paragraph("<b>Practice Suggestions:</b>", self.styles['Normal']))
                for suggestion in practice_suggestions:
                    story.append(Paragraph(f"→ {suggestion}", self.styles['Recommendation']))
                story.append(Spacer(1, 15))
            
            # Footer
            story.append(Spacer(1, 30))
            story.append(Paragraph("Generated by Vocal IQ - AI-Powered Voice Analytics", self.styles['Normal']))
            story.append(Paragraph(f"Report generated on {datetime.now().strftime('%B %d, %Y at %I:%M %p')}", self.styles['Normal']))
            
            # Build PDF
            doc.build(story)
            buffer.seek(0)
            return buffer.getvalue()
            
        except Exception as e:
            logger.error(f"Error generating PDF: {str(e)}")
            raise RuntimeError(f"PDF generation failed: {str(e)}")
    
    def _create_table(self, data):
        """Create a formatted table"""
        table = Table(data)
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#f7fafc')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.HexColor('#2d3748')),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 12),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor('#ffffff')),
            ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#e2e8f0')),
            ('FONTSIZE', (0, 1), (-1, -1), 10),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.HexColor('#ffffff'), colors.HexColor('#f8f9fa')])
        ]))
        return table
    
    def _get_status_text(self, value, min_good, max_good, reverse=False):
        """Get status text based on value range"""
        if reverse:
            if value <= min_good:
                return 'Excellent'
            elif value <= max_good:
                return 'Good'
            else:
                return 'Needs Improvement'
        else:
            if min_good <= value <= max_good:
                return 'Good'
            elif value < min_good:
                return 'Below Average'
            else:
                return 'Above Average'
