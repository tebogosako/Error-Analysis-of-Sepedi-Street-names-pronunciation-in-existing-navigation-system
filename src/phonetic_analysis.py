import parselmouth
from parselmouth import praat
import numpy as np
import pandas as pd
from pathlib import Path
from config import *
import string

class PhoneticAnalyzer:
    def __init__(self):
        pass
    
    def extract_phonetic_features(self, audio, sr):
        """Extract pronunciation features using Praat"""
        # Convert to Praat sound object
        sound = parselmouth.Sound(audio, sampling_frequency=sr)
        
        # Extract formants (vowel characteristics)
        formant = sound.to_formant_burg()
        
        # Extract pitch
        pitch = sound.to_pitch()
        
        # Extract intensity
        intensity = sound.to_intensity()
        
        features = {
            'duration': len(audio) / sr,
            'mean_pitch': pitch.get_mean() if pitch.get_mean() else 0,
            'mean_intensity': intensity.get_average(),
            'formant_f1': formant.get_mean(1) if formant.get_mean(1) else 0,
            'formant_f2': formant.get_mean(2) if formant.get_mean(2) else 0,
            'formant_f3': formant.get_mean(3) if formant.get_mean(3) else 0,
        }
        return features
    
    def calculate_phonetic_distance(self, audio1, sr1, audio2, sr2):
        """Calculate distance between two audio samples"""
        # Dynamic Time Warping distance
        # Resample if needed
        if sr1 != sr2:
            # Resample to common rate
            pass
        
        # MFCC comparison
        mfcc1 = self.get_mfcc(audio1, sr1)
        mfcc2 = self.get_mfcc(audio2, sr2)
        
        # DTW distance
        distance = self.dtw_distance(mfcc1, mfcc2)
        return distance
    
    def get_mfcc(self, audio, sr, n_mfcc=13):
        """Extract MFCC features"""
        import librosa
        mfcc = librosa.feature.mfcc(y=audio, sr=sr, n_mfcc=n_mfcc)
        return mfcc.T  # Transpose for DTW
    
    def dtw_distance(self, x, y):
        """Dynamic Time Warping distance"""
        from scipy.spatial.distance import cdist
        from scipy.spatial.distance import euclidean
        from fastdtw import fastdtw
        
        distance, _ = fastdtw(x, y, dist=euclidean)
        return distance
    
    def analyze_all(self, data, transcriptions):
        """Perform phonetic analysis on all recordings"""
        results = []
        
        # Compare each participant's recording to Apple Maps
        for participant in PARTICIPANTS:
            for street in STREET_NAMES:
                if street in data['apple'] and street in data['participants'][participant]:
                    apple_audio, apple_sr = data['apple'][street]
                    part_audio, part_sr = data['participants'][participant][street]
                    
                    # Get phonetic features
                    apple_features = self.extract_phonetic_features(apple_audio, apple_sr)
                    part_features = self.extract_phonetic_features(part_audio, part_sr)
                    
                    # Calculate distance
                    distance = self.calculate_phonetic_distance(
                        apple_audio, apple_sr, part_audio, part_sr
                    )
                    
                    # Get transcriptions
                    apple_text = transcriptions['apple'].get(street, '')
                    part_text = transcriptions['participants'][participant].get(street, '')
                    
                    results.append({
                        'participant': participant,
                        'street': street,
                        'apple_transcription': apple_text,
                        'participant_transcription': part_text,
                        'dtw_distance': distance,
                        'duration_diff': part_features['duration'] - apple_features['duration'],
                        'pitch_diff': part_features['mean_pitch'] - apple_features['mean_pitch'],
                        'intensity_diff': part_features['mean_intensity'] - apple_features['mean_intensity'],
                        'f1_diff': part_features['formant_f1'] - apple_features['formant_f1'],
                        'f2_diff': part_features['formant_f2'] - apple_features['formant_f2'],
                    })
        
        return pd.DataFrame(results)