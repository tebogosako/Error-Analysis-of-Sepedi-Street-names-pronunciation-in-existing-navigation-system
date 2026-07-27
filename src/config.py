# src/config.py
import os
from pathlib import Path

# Get the project root
BASE_DIR = Path(__file__).parent.parent.absolute()
DATA_DIR = BASE_DIR / 'data'
APPLE_DIR = DATA_DIR / 'apple_maps_recordings'
PARTICIPANTS_DIR = DATA_DIR / 'participants'
OUTPUT_DIR = BASE_DIR / 'outputs'

# Create directories
for dir_path in [DATA_DIR, APPLE_DIR, PARTICIPANTS_DIR, OUTPUT_DIR]:
    dir_path.mkdir(parents=True, exist_ok=True)

# Participants
PARTICIPANTS = ['participant_1', 'participant_2', 'participant_3', 'participant_4']

# Street names - match your file naming
STREET_NAMES = ['Street 1', 'Street 2', 'Street 3', 'Street 4', 'Street 5',
                'Street 6', 'Street 7', 'Street 8', 'Street 9', 'Street 10']

STREET_NAMES_LOWER = [s.lower().replace(' ', '') for s in STREET_NAMES]

SAMPLE_RATE = 16000

print(f"✅ Config loaded from: {BASE_DIR}")
print(f"   Street names: {STREET_NAMES}")