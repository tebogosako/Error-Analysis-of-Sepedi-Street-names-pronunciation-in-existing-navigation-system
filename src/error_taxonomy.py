# src/error_taxonomy.py
"""
Error Taxonomy Module for Sepedi Street Name Pronunciation
Defines and manages the error taxonomy
"""

import sys
from pathlib import Path
import pandas as pd

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from config import *

class ErrorTaxonomy:
    """Manages the Sepedi pronunciation error taxonomy"""
    
    def __init__(self):
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
                    "'ph' pronounced as 'p' or 'f'",
                    "'kh' pronounced as 'k' or 'g'"
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
                    "Missing tone markers",
                    "Vowel length changes"
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
                    "Cluster 'hl' simplified to 'l'",
                    "Cluster 'ng' simplified to 'n' or 'g'"
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
                    "Incorrect prefix attachment",
                    "Stem separation issues"
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
                    "Multiple error types combined",
                    "Unclassified phonetic errors"
                ],
                'cause': 'General lack of Sepedi training data',
                'impact': 'Overall poor pronunciation quality',
                'severity': 'Medium'
            }
        }
    
    def get_taxonomy(self):
        """Return the complete taxonomy"""
        return self.taxonomy
    
    def get_category_info(self, category_code):
        """Get information for a specific category"""
        return self.taxonomy.get(category_code, None)
    
    def get_all_categories(self):
        """Get list of all category codes"""
        return list(self.taxonomy.keys())
    
    def get_severity(self, category_code):
        """Get severity level for a category"""
        if category_code in self.taxonomy:
            return self.taxonomy[category_code]['severity']
        return 'Unknown'
    
    def to_dataframe(self):
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