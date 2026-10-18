# Sepedi Street Name Pronunciation Error Analysis

This project compares Apple Maps pronunciations of 10 Sepedi street names with reference pronunciations recorded by four native Sepedi speakers.

The native-speaker recordings are the reference pronunciations.  
The Apple Maps recordings are the system outputs being evaluated.

This produces 40 comparisons:

```text
10 street names × 4 participants = 40 comparisons
```

## Project purpose

The project identifies and classifies pronunciation errors made by Apple Maps when pronouncing Sepedi street names. It calculates Word Error Rate (WER) and Character Error Rate (CER), identifies candidate pronunciation differences, and classifies verified errors using a pronunciation error taxonomy.

No random, simulated, or placeholder values are used.

## Repository structure

```text
├── main.py
├── run_final_analysis.py
├── requirements.txt
├── src/
├── data/
│   ├── apple_maps/
│   └── participants/
├── inputs/
│   └── reference_transcriptions.csv
└── outputs/
    ├── comparison_results.csv
    ├── error_review.csv
    ├── error_log.csv
    ├── error_summary.csv
    ├── street_summary.csv
    ├── participant_summary.csv
    └── figures/
```

## Installation

```bash
pip install -r requirements.txt
```

## How to run

1. Add Apple Maps recordings to `data/apple_maps/`.
2. Add participant recordings to `data/participants/participant_1/` to `participant_4/`.
3. Complete `inputs/reference_transcriptions.csv`.
4. Run the initial analysis:

```bash
python main.py
```

5. Open `outputs/error_review.csv` and manually review each pronunciation comparison.
6. Complete the final error category, error code, and linguistic evidence.
7. Generate the final results:

```bash
python run_final_analysis.py
```

## Outputs

| File | Description |
|---|---|
| `comparison_results.csv` | WER and CER for all 40 comparisons |
| `error_review.csv` | Candidate errors requiring manual review |
| `error_log.csv` | Final reviewed pronunciation errors |
| `error_summary.csv` | Frequency of each error category |
| `street_summary.csv` | Average WER and CER by street |
| `participant_summary.csv` | Average WER and CER by participant |
| `figures/` | Error-frequency chart and WER heatmap |

## Error categories

- Correct pronunciation (`CORR-00`)
- Phoneme substitution (`PHON-01`)
- Vowel quality error (`VOW-01`)
- Consonant realisation error (`CONS-01`)
- Stress/tone error (`TONE-01`)
- Consonant cluster error (`CLUS-01`)
- Morpheme substitution (`MORPH-01`)
- Grapheme-to-morpheme conversion error (`G2M-01`)
- Accent transfer (`ACC-01`)
- General mispronunciation (`MISC-01`)

## Author

**Tebogo Sako**  
Student number: 23823739  
HRCOS82 Honours Research Report 
University of South Africa
