
import sys
from pathlib import Path
import pandas as pd
import numpy as np
from collections import Counter

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from config import *

class SepediErrorClassifier:
    """Classifies pronunciation errors in Sepedi street names"""
    
    def __init__(self):
        # Sepedi-specific phoneme pairs (sounds that get confused)
        self.phoneme_pairs = [
            ('th', 't'), ('th', 'd'),   # Aspirated vs non-aspirated
            ('sh', 's'), ('sh', 'ch'),  # Alveolar vs postalveolar
            ('ny', 'n'), ('ny', 'ni'),  # Palatal vs alveolar
            ('ng', 'n'), ('ng', 'g'),   # Velar vs alveolar
            ('ph', 'p'), ('ph', 'f'),   # Aspirated bilabial
            ('kh', 'k'), ('kh', 'g'),   # Aspirated velar
            ('hl', 'l'), ('hl', 'dl'),  # Lateral vs alveolar
            ('mp', 'm'), ('mp', 'p'),   # Labial clusters
            ('nt', 'n'), ('nt', 't'),   # Alveolar clusters
            ('ts', 's'), ('ts', 'ch')   # Affricate vs fricative
        ]
        
        # Sepedi consonant clusters
        self.consonant_clusters = ['mp', 'nt', 'ng', 'sh', 'th', 'kh', 'ph', 'hl', 'dl', 'ts', 'ntš']
        
        # Sepedi prefixes (agglutination markers)
        self.sepedi_prefixes = ['di-', 'ba-', 'ma-', 'mo-', 'le-', 'se-', 'ka-', 'na-', 'ga-', 'go-']
        
        # Vowel pairs for stress/tone errors
        self.vowel_pairs = [('a', 'e'), ('e', 'i'), ('i', 'a'), ('o', 'u'), ('u', 'o'), ('a', 'o')]
    
    def classify_error(self, apple_text, participant_text, street_name):
        """
        Classify pronunciation error type
        
        Returns:
            str: Error category
            list: Error details
        """
        apple_words = str(apple_text).lower().split()
        participant_words = str(participant_text).lower().split()
        
        error_types = []
        error_details = []
        
        # Compare word by word
        for i, apple_word in enumerate(apple_words):
            if i < len(participant_words):
                part_word = participant_words[i]
                
                # 1. Phoneme Substitution
                for sep_pair, eng_pair in self.phoneme_pairs:
                    if sep_pair in apple_word and eng_pair in part_word:
                        error_types.append('phoneme_substitution')
                        error_details.append(f"'{sep_pair}' -> '{eng_pair}' in '{apple_word}'")
                        break
                    elif eng_pair in apple_word and sep_pair in part_word:
                        error_types.append('phoneme_substitution')
                        error_details.append(f"'{eng_pair}' -> '{sep_pair}' in '{apple_word}'")
                        break
                
                # 2. Stress/Tone Errors
                for v1, v2 in self.vowel_pairs:
                    if v1 in apple_word and v2 in part_word:
                        error_types.append('stress_tone_error')
                        error_details.append(f"Vowel '{v1}' -> '{v2}' in '{apple_word}'")
                        break
                
                # 3. Consonant Cluster Errors
                for cluster in self.consonant_clusters:
                    if cluster in apple_word and cluster not in part_word:
                        error_types.append('consonant_cluster_error')
                        error_details.append(f"Cluster '{cluster}' simplified in '{apple_word}'")
                        break
                    elif cluster not in apple_word and cluster in part_word:
                        error_types.append('consonant_cluster_error')
                        error_details.append(f"Cluster '{cluster}' incorrectly added")
                        break
                
                # 4. Agglutination Errors
                for prefix in self.sepedi_prefixes:
                    if apple_word.startswith(prefix) and not part_word.startswith(prefix):
                        error_types.append('agglutination_error')
                        error_details.append(f"Prefix '{prefix}' missing in '{apple_word}'")
                        break
                    elif not apple_word.startswith(prefix) and part_word.startswith(prefix):
                        error_types.append('agglutination_error')
                        error_details.append(f"Prefix '{prefix}' incorrectly added")
                        break
        
        # If no specific error but WER is high, classify as general
        if not error_types:
            error_types = ['mispronunciation']
            error_details = ['General pronunciation error']
        
        # Return most frequent error type
        most_common = Counter(error_types).most_common(1)
        return most_common[0][0] if most_common else 'unknown', error_details
    
    def classify_dataframe(self, df):
        """Classify errors for entire dataframe"""
        print("Classifying errors...")
        
        error_categories = []
        error_details_list = []
        
        for idx, row in df.iterrows():
            category, details = self.classify_error(
                row.get('apple_transcription', ''),
                row.get('participant_transcription', ''),
                row.get('street', '')
            )
            error_categories.append(category)
            error_details_list.append('; '.join(details[:3]))  # First 3 details
        
        df['error_category'] = error_categories
        df['error_details'] = error_details_list
        
        return df
    
    def get_error_taxonomy(self):
        """Return the complete error taxonomy"""
        return {
            'phoneme_substitution': {
                'category': 'Phoneme Substitution',
                'description': 'Sounds are replaced with similar but incorrect phonemes',
                'examples': [
                    "'th' pronounced as 't' (e.g., 'thaba' -> 'taba')",
                    "'sh' pronounced as 's' (e.g., 'moshi' -> 'mosi')",
                    "'ng' pronounced as 'n' or 'g'",
                    "'ph' pronounced as 'p' or 'f'"
                ],
                'cause': 'Missing phonemes in English phonetic inventory',
                'impact': 'Changes word meaning or makes it unrecognizable'
            },
            'stress_tone_error': {
                'category': 'Stress/Tone Error',
                'description': 'Incorrect syllable emphasis or tone patterns',
                'examples': [
                    "Wrong vowel pronunciation (e.g., 'a' -> 'e')",
                    "Incorrect stress placement",
                    "Missing tone markers"
                ],
                'cause': 'Tonal nature of Sepedi not captured in models',
                'impact': 'Changes word meaning (tonal distinction lost)'
            },
            'consonant_cluster_error': {
                'category': 'Consonant Cluster Error',
                'description': 'Complex consonant groupings are simplified or mispronounced',
                'examples': [
                    "Cluster 'mp' simplified to 'm' or 'p'",
                    "Cluster 'nt' simplified to 'n' or 't'",
                    "Cluster 'hl' simplified to 'l'"
                ],
                'cause': 'English lacks these consonant clusters',
                'impact': 'Simplified pronunciation, loss of phonemic distinction'
            },
            'agglutination_error': {
                'category': 'Agglutination Error',
                'description': 'Errors in handling prefixes and word structure',
                'examples': [
                    "Prefix 'di-' missing (e.g., 'dikgomo' -> 'kgomo')",
                    "Prefix 'ba-' missing (e.g., 'batho' -> 'tho')",
                    "Incorrect prefix attachment"
                ],
                'cause': 'Agglutinative structure not modeled correctly',
                'impact': 'Incorrect word form and meaning'
            },
            'mispronunciation': {
                'category': 'General Mispronunciation',
                'description': 'General pronunciation errors not fitting specific categories',
                'examples': [
                    "Overall phonetic deviation",
                    "Multiple error types combined"
                ],
                'cause': 'General lack of Sepedi training data',
                'impact': 'Overall poor pronunciation quality'
            }
        }