#!/usr/bin/env python3
"""
Test script for Kannada language detection
This script helps test if the improved language detection correctly identifies Kannada speech.
"""

import requests
import json
import os
import sys

def test_language_detection(audio_file_path, base_url="http://localhost:8000"):
    """
    Test language detection with an audio file
    """
    if not os.path.exists(audio_file_path):
        print(f"Error: Audio file not found: {audio_file_path}")
        return
    
    print(f"Testing language detection with file: {audio_file_path}")
    print("=" * 50)
    
    # First, get debug info
    try:
        debug_response = requests.get(f"{base_url}/debug-language-detection")
        if debug_response.status_code == 200:
            debug_info = debug_response.json()
            print("✅ Debug endpoint working")
            print(f"Supported languages: {len(debug_info.get('supported_languages', {}))}")
            if debug_info.get('kannada_detection_improved'):
                print("✅ Kannada detection improvements active")
                thresholds = debug_info.get('feature_thresholds', {})
                print(f"Kannada centroid range: {thresholds.get('kannada_centroid_range')}")
                print(f"Kannada priority: {thresholds.get('kannada_priority')}")
        else:
            print(f"❌ Debug endpoint failed: {debug_response.status_code}")
    except Exception as e:
        print(f"❌ Debug endpoint error: {e}")
    
    print("\n" + "=" * 50)
    
    # Test language detection
    try:
        with open(audio_file_path, 'rb') as f:
            files = {'file': (os.path.basename(audio_file_path), f, 'audio/webm')}
            
            # Note: This requires authentication, so you'll need to login first
            # For testing purposes, you can use the test endpoint
            response = requests.post(f"{base_url}/test-language-detection", files=files)
            
            if response.status_code == 200:
                result = response.json()
                print("✅ Language detection test completed")
                print(f"Detected language: {result.get('detected_language')} ({result.get('language_name')})")
                print(f"Confidence: {result.get('confidence', 0):.2f}")
                print(f"Transcription: {result.get('transcription', '')[:100]}...")
                
                # Show detection features
                features = result.get('detection_features', {})
                if features:
                    print("\nDetection Features:")
                    print(f"  Spectral Centroid: {features.get('spectral_centroid', 0):.2f} Hz")
                    print(f"  Spectral Rolloff: {features.get('spectral_rolloff', 0):.2f} Hz")
                    print(f"  Zero Crossing Rate: {features.get('zero_crossing_rate', 0):.4f}")
                    print(f"  MFCC Std: {features.get('mfcc_std', 0):.2f}")
                    print(f"  Kannada Score: {features.get('kannada_score', 0)}")
                    print(f"  Telugu Score: {features.get('telugu_score', 0)}")
                    print(f"  Hindi Score: {features.get('hindi_score', 0)}")
                
                # Check if Kannada was detected
                if result.get('detected_language') == 'kn':
                    print("\n🎉 SUCCESS: Kannada correctly detected!")
                else:
                    print(f"\n⚠️  WARNING: Expected Kannada but got {result.get('language_name')}")
                    print("This might indicate the detection algorithm needs further tuning.")
                    
            else:
                print(f"❌ Language detection failed: {response.status_code}")
                print(f"Response: {response.text}")
                
    except Exception as e:
        print(f"❌ Language detection error: {e}")

def main():
    """
    Main function to run the test
    """
    print("Kannada Language Detection Test")
    print("=" * 50)
    
    if len(sys.argv) < 2:
        print("Usage: python test_kannada_detection.py <audio_file_path>")
        print("Example: python test_kannada_detection.py kannada_speech.webm")
        return
    
    audio_file = sys.argv[1]
    base_url = sys.argv[2] if len(sys.argv) > 2 else "http://localhost:8000"
    
    print(f"Testing with file: {audio_file}")
    print(f"Backend URL: {base_url}")
    print("\nMake sure your backend server is running!")
    print("=" * 50)
    
    test_language_detection(audio_file, base_url)

if __name__ == "__main__":
    main() 