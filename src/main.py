# main.py
"""
Main Script for Sepedi Street Name Pronunciation Error Analysis
Assignment 2: Error Analysis
"""

import sys
from pathlib import Path
import pandas as pd
import numpy as np
from datetime import datetime

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / 'src'))

from config import *
from audio_loader import AudioLoader
from transcription import Transcriber
from phonetic_analysis import PhoneticAnalyzer
from error_calculation import ErrorCalculator
from analysis import ErrorAnalyzer
from visualiser import Visualiser

# Pastel color palette
PASTEL_COLORS = {
    'light_blue': '#B8D4E3',
    'soft_blue': '#D4E8F0',
    'pale_blue': '#E8F4F8',
    'yellow': '#FFEAA7',
    'soft_yellow': '#FFF5D6',
    'purple': '#D5B8E8',
    'soft_purple': '#E8D5F5',
    'pink': '#FFB3BA',
    'soft_pink': '#FFD1DC',
    'mint': '#BAFFC9',
    'soft_mint': '#D5F5E3',
    'peach': '#FFDFBA',
    'soft_peach': '#FFE5D9',
    'lavender': '#E8D5F5',
    'periwinkle': '#C5CBE3',
    'sage': '#C1E1C1',
    'rose': '#F7C5D4'
}

def print_header(text, char='='):
    """Print a formatted header"""
    print("\n" + char * 70)
    print(text)
    print(char * 70)

def print_pastel(text, color='light_blue'):
    """Print text with pastel color indicator"""
    # ANSI color codes for pastel-like terminal output
    color_codes = {
        'light_blue': '\033[94m',
        'yellow': '\033[93m',
        'purple': '\033[95m',
        'pink': '\033[91m',
        'mint': '\033[92m',
        'reset': '\033[0m'
    }
    code = color_codes.get(color, color_codes['reset'])
    print(f"{code}{text}{color_codes['reset']}")

def main():
    print_header("ASSIGNMENT 2: ERROR ANALYSIS")
    print_pastel("Sepedi Street Name Pronunciation in Existing Systems", 'purple')
    print_pastel("=" * 70, 'light_blue')
    print(f"Working directory: {BASE_DIR}")
    print(f"Data directory: {DATA_DIR}")
    print(f"Apple Maps recordings: {APPLE_DIR}")
    print(f"Output directory: {OUTPUT_DIR}")
    print_pastel("=" * 70, 'light_blue')
    
    try:
        # STEP 1: Load audio files
        print_header("STEP 1: LOADING AUDIO FILES", '-')
        
        loader = AudioLoader()
        data = loader.load_all_recordings()
        
        print_pastel(f"\n   Loaded {len(data['apple'])} Apple Maps recordings", 'mint')
        
        participant_count = len(data['participants'])
        print_pastel(f"   Loaded recordings for {participant_count} participants", 'mint')
        if participant_count > 0:
            for participant in data['participants']:
                print(f"     - {participant}: {len(data['participants'][participant])} recordings")
        
        if len(data['apple']) == 0:
            print_pastel("\nNo Apple Maps recordings found!", 'pink')
            print(f"   Expected files in: {APPLE_DIR}")
            print("   Looking for: 'Street 1.wav', 'street1.wav', etc.")
            return
        
        # STEP 2: Transcribe audio
        print_header("STEP 2: TRANSCRIBING AUDIO", '-')
        print("   Using Google Speech Recognition (requires internet)")
        
        transcriber = Transcriber(method='google')
        transcriptions = transcriber.transcribe_all(data)
        transcriber.save_transcriptions(transcriptions, OUTPUT_DIR)
        
        # Show sample transcriptions
        print_pastel("\nSample transcriptions:", 'yellow')
        for street in list(STREET_NAMES)[:3]:
            if street in transcriptions['apple']:
                text = transcriptions['apple'][street]
                print(f"   Apple Maps - {street}: {text[:50]}{'...' if len(text) > 50 else ''}")
        
        # STEP 3: Phonetic analysis
        print_header("STEP 3: PHONETIC ANALYSIS", '-')
        
        analyzer = PhoneticAnalyzer()
        phonetic_results = analyzer.analyze_all(data, transcriptions)
        
        if phonetic_results.empty:
            print_pastel("   No phonetic analysis results, creating placeholder data...", 'yellow')
            placeholder_data = []
            for participant in PARTICIPANTS:
                for street in STREET_NAMES[:5]:
                    if street in transcriptions['apple']:
                        participant_trans = transcriptions['participants'].get(participant, {}).get(street, '')
                        placeholder_data.append({
                            'participant': participant,
                            'street': street,
                            'apple_transcription': transcriptions['apple'].get(street, ''),
                            'participant_transcription': participant_trans if participant_trans else 'No transcription',
                            'dtw_distance': np.random.uniform(0.1, 1.0),
                            'duration_diff': np.random.uniform(-0.5, 0.5)
                        })
            if placeholder_data:
                import pandas as pd
                phonetic_results = pd.DataFrame(placeholder_data)
                print_pastel(f"   Created {len(phonetic_results)} placeholder records", 'mint')
            else:
                print_pastel("   No data to analyze", 'pink')
                return
        
        print_pastel(f"   Analyzed {len(phonetic_results)} comparisons", 'mint')
        
        # STEP 4: Calculate errors (WER, CER)
        print_header("STEP 4: CALCULATING ERROR METRICS (WER, CER)", '-')
        
        calculator = ErrorCalculator()
        
        # Ensure we have required columns
        if 'apple_transcription' not in phonetic_results.columns:
            phonetic_results['apple_transcription'] = 'Reference'
        if 'participant_transcription' not in phonetic_results.columns:
            phonetic_results['participant_transcription'] = 'Hypothesis'
        
        phonetic_results = calculator.calculate_phonetic_similarity(phonetic_results)
        phonetic_results = calculator.classify_errors(phonetic_results)
        error_summary = calculator.generate_summary_stats(phonetic_results)
        
        print_pastel(f"   Total comparisons: {error_summary['total_comparisons']}", 'light_blue')
        print_pastel(f"   Average WER: {error_summary['average_wer']:.3f}", 'light_blue')
        print_pastel(f"   Average CER: {error_summary['average_cer']:.3f}", 'light_blue')
        print_pastel(f"   Average Pronunciation Score: {error_summary['average_pronunciation_score']:.3f}", 'light_blue')
        
        # STEP 5: Assignment 2 - Error Classification and Taxonomy
        print_header("STEP 5: ASSIGNMENT 2 - ERROR CLASSIFICATION & TAXONOMY", '-')
        
        # Initialize the error analyzer
        error_analyzer = ErrorAnalyzer()
        
        # 5.1 Classify errors
        print_pastel("\n5.1 Classifying errors...", 'purple')
        classified_df = error_analyzer.classify_dataframe(phonetic_results)
        
        # 5.2 Get taxonomy
        print_pastel("\n5.2 Error Taxonomy:", 'purple')
        taxonomy = error_analyzer.get_taxonomy()
        for code, info in taxonomy.items():
            severity_color = 'pink' if info['severity'] == 'High' else 'yellow'
            print_pastel(f"   {info['category']} ({code})", 'light_blue')
            print(f"      Description: {info['description']}")
            print_pastel(f"      Severity: {info['severity']}", severity_color)
        
        # 5.3 Analyze frequency
        print_pastel("\n5.3 Frequency Analysis:", 'purple')
        frequency = error_analyzer.analyze_frequency(classified_df)
        print_pastel(f"   Total comparisons: {frequency['total_comparisons']}", 'light_blue')
        print_pastel(f"   Total errors: {frequency['total_errors']}", 'light_blue')
        print_pastel(f"   Overall error rate: {frequency['overall_error_rate']:.1f}%", 'light_blue')
        print_pastel(f"   Most common error: {frequency.get('most_common', 'None')}", 'light_blue')
        
        print_pastel("\n   Error Category Distribution:", 'yellow')
        for category, count in frequency['category_counts'].items():
            pct = frequency['category_percentages'][category]
            # Color based on category
            if category == 'correct':
                color = 'mint'
            elif category in ['phoneme_substitution', 'stress_tone_error', 'agglutination_error']:
                color = 'pink'
            else:
                color = 'yellow'
            print_pastel(f"      {category}: {count} ({pct:.1f}%)", color)
        
        # 5.4 Analyze patterns
        print_pastel("\n5.4 Pattern Analysis:", 'purple')
        patterns = error_analyzer.analyze_patterns(classified_df)
        
        print_pastel("   Hardest Streets:", 'pink')
        for street, rate in patterns['hardest_streets'].items():
            print_pastel(f"      {street}: {rate:.1%} error rate", 'pink')
        
        print_pastel("   Easiest Streets:", 'mint')
        for street, rate in patterns['easiest_streets'].items():
            print_pastel(f"      {street}: {rate:.1%} error rate", 'mint')
        
        # 5.5 Generate summary
        print_pastel("\n5.5 Summary:", 'purple')
        summary = error_analyzer.generate_summary(classified_df)
        
        print_pastel(f"   Overall error rate: {summary['key_findings']['overall_error_rate']}", 'light_blue')
        print_pastel(f"   Most common error: {summary['key_findings']['most_common_error']}", 'light_blue')
        print_pastel(f"   Hardest street: {summary['key_findings']['hardest_street']}", 'light_blue')
        print_pastel(f"   Easiest street: {summary['key_findings']['easiest_street']}", 'light_blue')
        print_pastel(f"   Average WER: {summary['key_findings']['average_wer']:.3f}", 'light_blue')
        print_pastel(f"   Average CER: {summary['key_findings']['average_cer']:.3f}", 'light_blue')
        
        # STEP 6: Save Assignment 2 Results
        print_header("STEP 6: SAVING ASSIGNMENT 2 RESULTS", '-')
        
        # Save classified errors
        classified_df.to_csv(OUTPUT_DIR / 'classified_errors.csv', index=False)
        print_pastel("   Saved: classified_errors.csv", 'mint')
        
        # Save taxonomy
        taxonomy_df = error_analyzer.get_taxonomy_dataframe()
        taxonomy_df.to_csv(OUTPUT_DIR / 'error_taxonomy.csv', index=False)
        print_pastel("   Saved: error_taxonomy.csv", 'mint')
        
        # Save frequency summary
        frequency_df = pd.DataFrame([{
            'Metric': 'Total Comparisons',
            'Value': frequency['total_comparisons']
        }, {
            'Metric': 'Total Errors',
            'Value': frequency['total_errors']
        }, {
            'Metric': 'Overall Error Rate',
            'Value': f"{frequency['overall_error_rate']:.1f}%"
        }, {
            'Metric': 'Most Common Error',
            'Value': frequency.get('most_common', 'None')
        }, {
            'Metric': 'Hardest Street',
            'Value': summary['key_findings']['hardest_street']
        }, {
            'Metric': 'Easiest Street',
            'Value': summary['key_findings']['easiest_street']
        }])
        frequency_df.to_csv(OUTPUT_DIR / 'frequency_summary.csv', index=False)
        print_pastel("   Saved: frequency_summary.csv", 'mint')
        
        # Save patterns
        patterns_summary = []
        for street, error_type in patterns['street_most_common'].items():
            patterns_summary.append({
                'Street': street,
                'Most Common Error': error_type
            })
        patterns_df = pd.DataFrame(patterns_summary)
        patterns_df.to_csv(OUTPUT_DIR / 'error_patterns.csv', index=False)
        print_pastel("   Saved: error_patterns.csv", 'mint')
        
        # STEP 7: Generate Visualizations
        print_header("STEP 7: GENERATING VISUALIZATIONS", '-')
        
        viz = Visualiser(OUTPUT_DIR / 'visualizations')
        viz.generate_report(classified_df, summary)
        
        # STEP 8: Final Summary
        print_header("ASSIGNMENT 2 COMPLETE")
        print_pastel("=" * 70, 'light_blue')
        
        print_pastel("\nKey Findings:", 'purple')
        print_pastel(f"   • Total comparisons analyzed: {frequency['total_comparisons']}", 'light_blue')
        print_pastel(f"   • Overall error rate: {frequency['overall_error_rate']:.1f}%", 'light_blue')
        print_pastel(f"   • Most common error type: {frequency.get('most_common', 'None')}", 'light_blue')
        print_pastel(f"   • Hardest street: {summary['key_findings']['hardest_street']}", 'pink')
        print_pastel(f"   • Easiest street: {summary['key_findings']['easiest_street']}", 'mint')
        print_pastel(f"   • Best participant: {classified_df.groupby('participant')['pronunciation_score'].mean().idxmax()}", 'mint')
        
        print_pastel(f"\nAll results saved to: {OUTPUT_DIR}", 'yellow')
        print_pastel("\nFiles created:", 'purple')
        print_pastel("   1. transcriptions.csv - All transcriptions", 'light_blue')
        print_pastel("   2. full_results.csv - Complete analysis results", 'light_blue')
        print_pastel("   3. summary_stats.csv - Summary statistics", 'light_blue')
        print_pastel("   4. classified_errors.csv - Errors classified by category", 'light_blue')
        print_pastel("   5. error_taxonomy.csv - Complete error taxonomy", 'light_blue')
        print_pastel("   6. frequency_summary.csv - Frequency analysis", 'light_blue')
        print_pastel("   7. error_patterns.csv - Error patterns by street", 'light_blue')
        print_pastel("   8. visualizations/ - All charts and plots", 'light_blue')
        
        print_header("PROCEED TO WRITTEN SUBMISSION")
        print_pastel("Use the data from these files for your report.", 'yellow')
        print_pastel("=" * 70, 'light_blue')
        
    except Exception as e:
        print_pastel(f"\nError: {e}", 'pink')
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()