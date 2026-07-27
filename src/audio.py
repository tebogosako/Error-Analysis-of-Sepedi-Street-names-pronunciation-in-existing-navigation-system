# debug_audio.py
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / 'src'))

from config import *
import os

print("=" * 70)
print("DEBUGGING AUDIO FILES")
print("=" * 70)

# Check if directories exist
print(f"\nChecking directories:")
print(f"   APPLE_DIR: {APPLE_DIR}")
print(f"   Exists: {APPLE_DIR.exists()}")

if not APPLE_DIR.exists():
    print(f"\nAPPLE_DIR does not exist. Creating...")
    APPLE_DIR.mkdir(parents=True, exist_ok=True)
    print(f"   Created: {APPLE_DIR}")
    print(f"   Please place your Apple Maps recordings here")

# List all files in Apple directory
print(f"\nFiles in {APPLE_DIR}:")
files = list(APPLE_DIR.glob('*'))
if files:
    for f in files:
        if f.is_file():
            size = f.stat().st_size / 1024
            print(f"   - {f.name} ({size:.1f} KB)")
else:
    print(f"   No files found.")

# List all files in Participants directories
print(f"\nParticipant directories:")
for participant in PARTICIPANTS:
    p_dir = PARTICIPANTS_DIR / participant
    print(f"\n   {participant}: {p_dir}")
    print(f"      Exists: {p_dir.exists()}")
    
    if p_dir.exists():
        p_files = list(p_dir.glob('*'))
        if p_files:
            for f in p_files:
                if f.is_file():
                    size = f.stat().st_size / 1024
                    print(f"      - {f.name} ({size:.1f} KB)")
        else:
            print(f"      No files found")
    else:
        print(f"      Directory does not exist")
        print(f"      Creating: {p_dir}")
        p_dir.mkdir(parents=True, exist_ok=True)
        print(f"      Created")

# Check for specific street names
print(f"\nLooking for specific street name files:")
for street in STREET_NAMES:
    found = False
    # Try different variations
    variations = [
        f"{street}.wav",
        f"{street}.m4a",
        f"{street}.mp3",
        f"{street.replace(' ', '')}.wav",
        f"{street.lower()}.wav",
        f"{street.lower().replace(' ', '')}.wav",
    ]
    
    for var in variations:
        filepath = APPLE_DIR / var
        if filepath.exists():
            print(f"   Found: {var}")
            found = True
            break
    
    if not found:
        print(f"   Not found: {street} (tried: {', '.join(variations[:3])})")

print("\n" + "=" * 70)