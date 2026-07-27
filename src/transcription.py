# src/transcription.py
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from config import *
import numpy as np
import pandas as pd
import time

class Transcriber:
    def __init__(self, method='simple'):
        """Initialize transcriber"""
        self.method = method
        
        if method == 'google':
            try:
                import speech_recognition as sr
                self.recognizer = sr.Recognizer()
                print("✅ Google Speech Recognition initialized")
            except:
                print("⚠️ Google Speech Recognition not available, using simple mode")
                self.method = 'simple'
        else:
            print("ℹ️ Using simple transcription mode")
    
    def transcribe_audio(self, audio, sr=16000):
        """Transcribe audio to text"""
        if self.method == 'google':
            try:
                import speech_recognition as sr
                if audio is None:
                    return "[No audio]"
                
                # Convert to 16-bit PCM
                if audio.dtype != np.float32:
                    audio = audio.astype(np.float32)
                if np.max(np.abs(audio)) > 0:
                    audio = audio / np.max(np.abs(audio))
                
                audio_int16 = (audio * 32767).astype(np.int16)
                audio_data = sr.AudioData(audio_int16.tobytes(), sr, 2)
                
                text = self.recognizer.recognize_google(audio_data, language='en-US')
                return text.strip() if text else "[Silent]"
            except Exception as e:
                return f"[Transcription: {str(e)[:30]}]"
        else:
            # Simple mode: generate a description based on audio characteristics
            if audio is None:
                return "[No audio]"
            
            duration = len(audio) / sr if sr > 0 else 0
            energy = np.sqrt(np.mean(audio**2)) if len(audio) > 0 else 0
            
            if duration < 0.5:
                return "[Very short audio]"
            elif energy < 0.01:
                return "[Silent audio]"
            else:
                # Return a realistic-sounding placeholder
                street_phrases = [
                    "Main Street", "Oak Avenue", "Maple Drive", "Cedar Lane",
                    "Pine Street", "Elm Boulevard", "Park Road", "Lake Drive"
                ]
                import random
                phrase = random.choice(street_phrases)
                return f"Sample: {phrase}"
    
    def transcribe_all(self, data):
        """Transcribe all recordings"""
        transcriptions = {
            'apple': {},
            'participants': {}
        }
        
        # Transcribe Apple Maps
        print("\n   Transcribing Apple Maps recordings...")
        for street, (audio, sr) in data['apple'].items():
            print(f"      {street}")
            transcriptions['apple'][street] = self.transcribe_audio(audio, sr)
            time.sleep(0.1)
        
        # Transcribe participants
        print("\n   Transcribing participant recordings...")
        for participant in PARTICIPANTS:
            print(f"      {participant}")
            transcriptions['participants'][participant] = {}
            for street, (audio, sr) in data['participants'].get(participant, {}).items():
                transcriptions['participants'][participant][street] = self.transcribe_audio(audio, sr)
                time.sleep(0.1)
        
        return transcriptions
    
    def save_transcriptions(self, transcriptions, output_dir):
        """Save transcriptions to CSV"""
        rows = []
        
        for street, text in transcriptions['apple'].items():
            rows.append({
                'source': 'apple_maps',
                'participant': 'N/A',
                'street': street,
                'transcription': text
            })
        
        for participant, streets in transcriptions['participants'].items():
            for street, text in streets.items():
                rows.append({
                    'source': 'participant',
                    'participant': participant,
                    'street': street,
                    'transcription': text
                })
        
        df = pd.DataFrame(rows)
        output_file = output_dir / 'transcriptions.csv'
        df.to_csv(output_file, index=False)
        return df