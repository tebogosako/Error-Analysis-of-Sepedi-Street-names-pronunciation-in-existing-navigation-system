# src/audio_loader.py
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from config import *
import librosa
import soundfile as sf
import numpy as np

class AudioLoader:
    def __init__(self):
        self.sample_rate = SAMPLE_RATE
        print(f"AudioLoader initialized with sample rate: {self.sample_rate}")
    
    def load_audio(self, filepath):
        """Load audio file and resample if needed"""
        try:
            audio, sr = librosa.load(filepath, sr=self.sample_rate)
            return audio, sr
        except Exception as e:
            print(f"Error loading {filepath}: {e}")
            return None, None
    
    def find_audio_file(self, directory, street_name):
        """Find audio file with flexible naming"""
        for ext in ['.wav', '.m4a', '.mp3', '.flac']:
            # Try with spaces
            filepath = directory / f'{street_name}{ext}'
            if filepath.exists():
                return filepath
            
            # Try without spaces
            no_space = street_name.replace(' ', '')
            filepath = directory / f'{no_space}{ext}'
            if filepath.exists():
                return filepath
            
            # Try lowercase
            lower = street_name.lower()
            filepath = directory / f'{lower}{ext}'
            if filepath.exists():
                return filepath
            
            # Try lowercase without spaces
            lower_no_space = street_name.lower().replace(' ', '')
            filepath = directory / f'{lower_no_space}{ext}'
            if filepath.exists():
                return filepath
            
            # Try with underscore
            with_underscore = street_name.replace(' ', '_')
            filepath = directory / f'{with_underscore}{ext}'
            if filepath.exists():
                return filepath
            
            # Try with dash
            with_dash = street_name.replace(' ', '-')
            filepath = directory / f'{with_dash}{ext}'
            if filepath.exists():
                return filepath
        
        # Try glob pattern
        pattern = f'*{street_name.replace(" ", "")}*'
        matches = list(directory.glob(f'{pattern}.*'))
        if matches:
            return matches[0]
        
        return None
    
    def load_all_recordings(self):
        """Load all participant and Apple Maps recordings"""
        data = {}
        
        # Load Apple Maps TTS
        print("Loading Apple Maps recordings...")
        data['apple'] = {}
        
        for street in STREET_NAMES:
            found = False
            for ext in ['.wav', '.m4a', '.mp3', '.flac']:
                # Try with spaces (original)
                filepath = APPLE_DIR / f'{street}{ext}'
                if filepath.exists():
                    audio, sr = self.load_audio(filepath)
                    if audio is not None:
                        data['apple'][street] = (audio, sr)
                        print(f"   Loaded: {street}")
                        found = True
                        break
                
                # Try without spaces
                no_space = street.replace(' ', '')
                filepath = APPLE_DIR / f'{no_space}{ext}'
                if filepath.exists():
                    audio, sr = self.load_audio(filepath)
                    if audio is not None:
                        data['apple'][street] = (audio, sr)
                        print(f"   Loaded: {street} (as {no_space})")
                        found = True
                        break
                
                # Try lowercase
                lower = street.lower()
                filepath = APPLE_DIR / f'{lower}{ext}'
                if filepath.exists():
                    audio, sr = self.load_audio(filepath)
                    if audio is not None:
                        data['apple'][street] = (audio, sr)
                        print(f"   Loaded: {street} (as {lower})")
                        found = True
                        break
                
                # Try with underscore
                with_underscore = street.replace(' ', '_')
                filepath = APPLE_DIR / f'{with_underscore}{ext}'
                if filepath.exists():
                    audio, sr = self.load_audio(filepath)
                    if audio is not None:
                        data['apple'][street] = (audio, sr)
                        print(f"   Loaded: {street} (as {with_underscore})")
                        found = True
                        break
            
            if not found:
                print(f"   Could not find: {street}")
                print(f"      Tried: {street}.wav, {street.replace(' ', '')}.wav, {street.lower()}.wav")
        
        if not data['apple']:
            print(f"No Apple Maps recordings found in {APPLE_DIR}")
            print("   Supported formats: .wav, .m4a, .mp3")
            print("   Looking for files like: 'Street 1.wav' or 'street1.wav'")
        
        # Load participant recordings
        print("\nLoading participant recordings...")
        data['participants'] = {}
        for participant in PARTICIPANTS:
            p_dir = PARTICIPANTS_DIR / participant
            if not p_dir.exists():
                print(f"Participant directory not found: {p_dir}")
                continue
                
            data['participants'][participant] = {}
            print(f"   Loading {participant}...")
            
            for street in STREET_NAMES:
                found = False
                for ext in ['.wav', '.m4a', '.mp3', '.flac']:
                    # Try with spaces
                    filepath = p_dir / f'{street}{ext}'
                    if filepath.exists():
                        audio, sr = self.load_audio(filepath)
                        if audio is not None:
                            data['participants'][participant][street] = (audio, sr)
                            found = True
                            break
                    
                    # Try without spaces
                    no_space = street.replace(' ', '')
                    filepath = p_dir / f'{no_space}{ext}'
                    if filepath.exists():
                        audio, sr = self.load_audio(filepath)
                        if audio is not None:
                            data['participants'][participant][street] = (audio, sr)
                            found = True
                            break
                
                if not found:
                    print(f"      Could not find: {street}")
        
        return data
    
    def preprocess_audio(self, audio):
        """Normalize and trim silence"""
        if audio is None:
            return None
        if np.max(np.abs(audio)) > 0:
            audio = audio / np.max(np.abs(audio))
        audio, _ = librosa.effects.trim(audio, top_db=20)
        return audio