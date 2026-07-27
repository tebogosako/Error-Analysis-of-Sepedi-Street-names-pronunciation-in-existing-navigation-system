# analysis.py
"""
Error Analysis Module for Sepedi Street Name Pronunciation
Compares system outputs with ground truth and classifies errors
"""

import sys
from pathlib import Path
import pandas as pd
import numpy as np
from collections import Counter

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from config import *

class ErrorAnalyzer:
    """Complete error analysis for Sepedi street name pronunciation"""
    
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
        
        # Initialize taxonomy
        self.taxonomy = self._build_taxonomy()
    
    def _build_taxonomy(self):
        """Build the complete error taxonomy"""
        return {
            'phoneme_substitution': {
                'category': 'Phoneme Substitution',
                'code': 'PHON-01',
                'description': 'Sounds are replaced with similar but incorrect phonemes',
                'examples': [
                    "'th' pronounced as 't' (e.g., 'thaba' -> 'taba')",
                    "'sh' pronounced as 's' (e.g., 'moshi' -> 'mosi')",
                    "'ng' pronounced as 'n' or 'g'",
                    "'ph' pronounced as 'p' or 'f'"
                ],
                'cause': 'Missing phonemes in English phonetic inventory',
                'impact': 'Changes word meaning or makes it unrecognizable',
                'severity': 'High'
            },
            'stress_tone_error': {
                'category': 'Stress/Tone Error',
                'code': 'TONE-01',
                'description': 'Incorrect syllable emphasis or tone patterns',
                'examples': [
                    "Wrong vowel pronunciation (e.g., 'a' -> 'e')",
                    "Incorrect stress placement",
                    "Missing tone markers"
                ],
                'cause': 'Tonal nature of Sepedi not captured in models',
                'impact': 'Changes word meaning (tonal distinction lost)',
                'severity': 'High'
            },
            'consonant_cluster_error': {
                'category': 'Consonant Cluster Error',
                'code': 'CLUS-01',
                'description': 'Complex consonant groupings are simplified or mispronounced',
                'examples': [
                    "Cluster 'mp' simplified to 'm' or 'p'",
                    "Cluster 'nt' simplified to 'n' or 't'",
                    "Cluster 'hl' simplified to 'l'"
                ],
                'cause': 'English lacks these consonant clusters',
                'impact': 'Simplified pronunciation, loss of phonemic distinction',
                'severity': 'Medium'
            },
            'agglutination_error': {
                'category': 'Agglutination Error',
                'code': 'AGGL-01',
                'description': 'Errors in handling prefixes and word structure',
                'examples': [
                    "Prefix 'di-' missing (e.g., 'dikgomo' -> 'kgomo')",
                    "Prefix 'ba-' missing (e.g., 'batho' -> 'tho')",
                    "Incorrect prefix attachment"
                ],
                'cause': 'Agglutinative structure not modeled correctly',
                'impact': 'Incorrect word form and meaning',
                'severity': 'High'
            },
            'mispronunciation': {
                'category': 'General Mispronunciation',
                'code': 'MISC-01',
                'description': 'General pronunciation errors not fitting specific categories',
                'examples': [
                    "Overall phonetic deviation",
                    "Multiple error types combined"
                ],
                'cause': 'General lack of Sepedi training data',
                'impact': 'Overall poor pronunciation quality',
                'severity': 'Medium'
            }
        }
    
    def classify_error(self, apple_text, participant_text, street_name):
        """
        Classify pronunciation error type
        
        Returns:
            tuple: (error_category, error_details)
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
            error_details_list.append('; '.join(details[:3]))
        
        df['error_category'] = error_categories
        df['error_details'] = error_details_list
        
        return df
    
    def get_taxonomy(self):
        """Return the complete error taxonomy"""
        return self.taxonomy
    
    def get_taxonomy_dataframe(self):
        """Convert taxonomy to DataFrame"""
        data = []
        for code, info in self.taxonomy.items():
            data.append({
                'Category Code': code,
                'Category Name': info['category'],
                'Description': info['description'],
                'Examples': '; '.join(info['examples'][:3]),
                'Cause': info['cause'],
                'Impact': info['impact'],
                'Severity': info['severity']
            })
        return pd.DataFrame(data)
    
    def analyze_frequency(self, df):
        """Analyze error frequency by category, street, and participant"""
        
        results = {}
        
        # Overall frequency
        results['total_comparisons'] = len(df)
        results['total_errors'] = len(df[df['error_category'] != 'correct'])
        results['overall_error_rate'] = (results['total_errors'] / results['total_comparisons']) * 100 if results['total_comparisons'] > 0 else 0
        
        # Frequency by category
        results['category_counts'] = df['error_category'].value_counts().to_dict()
        results['category_percentages'] = {
            k: (v / results['total_comparisons']) * 100 if results['total_comparisons'] > 0 else 0
            for k, v in results['category_counts'].items()
        }
        
        # Frequency by street
        results['street_error_rates'] = df.groupby('street').apply(
            lambda x: (x['error_category'] != 'correct').sum() / len(x) if len(x) > 0 else 0
        ).to_dict()
        
        # Frequency by participant
        results['participant_error_rates'] = df.groupby('participant').apply(
            lambda x: (x['error_category'] != 'correct').sum() / len(x) if len(x) > 0 else 0
        ).to_dict()
        
        # Most common errors
        if results['category_counts']:
            results['most_common'] = max(results['category_counts'], key=results['category_counts'].get)
            results['most_common_count'] = results['category_counts'][results['most_common']]
            results['most_common_percentage'] = (results['most_common_count'] / results['total_comparisons']) * 100 if results['total_comparisons'] > 0 else 0
        
        # Error type distribution
        error_counts = df['error_type'].value_counts()
        results['error_type_distribution'] = error_counts.to_dict()
        
        return results
    
    def analyze_patterns(self, df):
        """Identify error patterns"""
        
        patterns = {}
        
        # Pattern 1: Most common error by street
        patterns['street_most_common'] = {}
        for street in df['street'].unique():
            street_df = df[df['street'] == street]
            most_common = street_df['error_category'].mode()
            if not most_common.empty:
                patterns['street_most_common'][street] = most_common.iloc[0]
        
        # Pattern 2: Multiple error types per street
        patterns['streets_with_multiple_errors'] = []
        for street in df['street'].unique():
            street_df = df[df['street'] == street]
            error_types = street_df['error_category'].unique()
            if len(error_types) > 2:
                patterns['streets_with_multiple_errors'].append({
                    'street': street,
                    'error_types': list(error_types)
                })
        
        # Pattern 3: Participant error profiles
        patterns['participant_profiles'] = {}
        for participant in df['participant'].unique():
            p_df = df[df['participant'] == participant]
            profiles = p_df['error_category'].value_counts().to_dict()
            patterns['participant_profiles'][participant] = profiles
        
        # Pattern 4: Streets with highest error rates
        street_error_rates = df.groupby('street').apply(
            lambda x: (x['error_category'] != 'correct').sum() / len(x) if len(x) > 0 else 0
        ).sort_values(ascending=False)
        patterns['hardest_streets'] = street_error_rates.head(3).to_dict()
        patterns['easiest_streets'] = street_error_rates.tail(3).to_dict()
        
        # Pattern 5: Error severity analysis
        patterns['severity_analysis'] = {
            'high_severity': len(df[df['error_category'].isin(['phoneme_substitution', 'stress_tone_error', 'agglutination_error'])]),
            'medium_severity': len(df[df['error_category'].isin(['consonant_cluster_error', 'mispronunciation'])])
        }
        
        return patterns
    
    def generate_summary(self, df):
        """Generate comprehensive summary"""
        
        # Get frequency analysis
        frequency = self.analyze_frequency(df)
        
        # Get pattern analysis
        patterns = self.analyze_patterns(df)
        
        # Calculate additional stats
        df['wer'] = pd.to_numeric(df['wer'], errors='coerce')
        df['cer'] = pd.to_numeric(df['cer'], errors='coerce')
        
        summary = {
            'frequency': frequency,
            'patterns': patterns,
            'key_findings': {
                'total_comparisons': frequency['total_comparisons'],
                'overall_error_rate': f"{frequency['overall_error_rate']:.1f}%",
                'most_common_error': frequency.get('most_common', 'None'),
                'hardest_street': list(patterns['hardest_streets'].keys())[0] if patterns['hardest_streets'] else 'None',
                'easiest_street': list(patterns['easiest_streets'].keys())[0] if patterns['easiest_streets'] else 'None',
                'average_wer': df['wer'].mean() if not df['wer'].isna().all() else 0,
                'average_cer': df['cer'].mean() if not df['cer'].isna().all() else 0
            }
        }
        
        return summary