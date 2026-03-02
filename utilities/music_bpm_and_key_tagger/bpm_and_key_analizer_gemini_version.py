#!/usr/bin/env python3

import os
import re
import sys  # Added for script arguments
import warnings
import numpy as np
import librosa

# --- Configuration ---
AUDIO_EXTENSIONS = (".mp3", ".wav", ".flac", ".aiff", ".m4a")
CAMELOT_MAP = {
    "major": {
        "C": "8B",
        "G": "9B",
        "D": "10B",
        "A": "11B",
        "E": "12B",
        "B": "1B",
        "F#": "2B",
        "C#": "3B",
        "G#": "4B",
        "D#": "5B",
        "A#": "6B",
        "F": "7B",
    },
    "minor": {
        "A": "8A",
        "E": "9A",
        "B": "10A",
        "F#": "11A",
        "C#": "12A",
        "G#": "1A",
        "D#": "2A",
        "A#": "3A",
        "F": "4A",
        "C": "5A",
        "G": "6A",
        "D": "7A",
    },
}
PITCH_CLASSES = ["C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B"]

# --- Individual Analyzer Functions ---


def get_bpm(y, sr):
    """Analyzes and returns the BPM for loaded audio."""
    try:
        # librosa.beat.beat_track returns tempo as a 1-element array
        tempo, _ = librosa.beat.beat_track(y=y, sr=sr)

        # FIX for NumPy warning:
        # Instead of float(tempo), we use float(tempo[0])
        if tempo.size > 0:
            return round(float(tempo[0]))

        print("  -> Could not determine BPM.")
        return 0
    except Exception as e:
        print(f"  -> [BPM Error]: {e}")
        return 0


def get_key(y, sr):
    """Analyzes and returns the Camelot Key for loaded audio."""
    try:
        #import pdb

        #pdb.set_trace()
        chroma = librosa.feature.chroma_stft(y=y, sr=sr)
        chroma_mean = np.mean(chroma, axis=1)

        major_profile = np.array([1, 0, 1, 0, 1, 1, 0, 1, 0, 1, 0, 1])
        minor_profile = np.array([1, 0, 1, 1, 0, 1, 0, 1, 1, 0, 1, 0])

        cor_maj = [
            np.corrcoef(chroma_mean, np.roll(major_profile, i))[0, 1] for i in range(12)
        ]
        cor_min = [
            np.corrcoef(chroma_mean, np.roll(minor_profile, i))[0, 1] for i in range(12)
        ]

        best_maj_i = np.argmax(cor_maj)
        best_min_i = np.argmax(cor_min)

        if cor_maj[best_maj_i] > cor_min[best_min_i]:
            key = PITCH_CLASSES[best_maj_i]
            mode = "major"
        else:
            key = PITCH_CLASSES[best_min_i]
            mode = "minor"

        return CAMELOT_MAP[mode].get(key, "??")
    except Exception as e:
        print(f"  -> [Key Error]: {e}")
        return "00"


# --- Main Processing Function (UPDATED LOGIC) ---


def cleanup_macos_files(folder_path):
    """
    Removes macOS resource fork files (._*) only if a corresponding
    audio file exists (e.g., removes ._song.mp3 only if song.mp3 exists).
    """
    removed_count = 0

    # Get list of all audio files in the directory
    audio_files = set()
    for filename in os.listdir(folder_path):
        if filename.lower().endswith(AUDIO_EXTENSIONS) and not filename.startswith('.'):
            audio_files.add(filename)

    # Check for ._* files and only remove if corresponding audio file exists
    for filename in os.listdir(folder_path):
        if filename.startswith("._"):
            # Get the original filename without the ._ prefix
            original_filename = filename[2:]  # Remove the first 2 characters (._)

            # Only delete if the corresponding audio file exists
            if original_filename in audio_files:
                filepath = os.path.join(folder_path, filename)
                try:
                    os.remove(filepath)
                    removed_count += 1
                except Exception as e:
                    print(f"Warning: Could not remove {filename}: {e}")

    if removed_count > 0:
        print(f"\nCleaned up {removed_count} macOS metadata files (._*)")


def process_folder(folder_path):
    """
    Iterates through a folder, analyzing and filling in missing
    BPM/Key data in 'XX-BPM-KEY-Name' format.
    """
    if not os.path.isdir(folder_path):
        print(f"Error: Path '{folder_path}' is not a valid directory.")
        return

    print(f"Scanning folder: {folder_path}\n")
    processed_count = 0
    skipped_count = 0

    # REGEX to parse your specific format:
    file_pattern = re.compile(r"^(\d{2})-(\S{2,3})-(\S{1,3})-(.*)$")

    for filename in os.listdir(folder_path):
        # Skip hidden files (files starting with '.')
        if filename.startswith('.'):
            continue

        if not filename.lower().endswith(AUDIO_EXTENSIONS):
            continue

        filepath = os.path.join(folder_path, filename)
        if not os.path.isfile(filepath):
            continue

        new_filename = None
        match = file_pattern.match(filename)

        if match:
            # File matches your format: "01-92-3A-dadada.mp3"
            classification = match.group(1)
            bpm_str = match.group(2)
            key_str = match.group(3)
            rest_of_name = match.group(4)

            # Check if fields are empty (using .startswith('0') is a robust check)
            bpm_is_empty = bpm_str.startswith("0")
            key_is_empty = key_str.startswith("0")

            if not bpm_is_empty and not key_is_empty:
                print(f"Skipping (already processed): {filename}")
                skipped_count += 1
                continue

            # --- We need to analyze at least one part ---
            print(f"Analyzing: {filename} ...")

            final_bpm = bpm_str
            final_key = key_str

            try:
                # Load the file *once*
                with warnings.catch_warnings():
                    warnings.simplefilter("ignore")
                    y, sr = librosa.load(filepath, sr=None)

                # Only analyze what's needed
                if bpm_is_empty:
                    print("  -> Finding BPM...")
                    analyzed_bpm = get_bpm(y, sr)
                    final_bpm = str(analyzed_bpm) if analyzed_bpm else bpm_str

                if key_is_empty:
                    print("  -> Finding Key...")
                    analyzed_key = get_key(y, sr)
                    final_key = analyzed_key if analyzed_key else key_str

                new_filename = (
                    f"{classification}-{final_bpm}-{final_key}-{rest_of_name}"
                )

            except Exception as e:
                print(f"\n[ERROR] Could not load {filename}: {e}")
                continue

        else:
            # File does NOT match format, e.g., "MySong.mp3"
            print(f"Analyzing (new file): {filename} ...")
            try:
                with warnings.catch_warnings():
                    warnings.simplefilter("ignore")
                    y, sr = librosa.load(filepath, sr=None)

                analyzed_bpm = get_bpm(y, sr)
                analyzed_key = get_key(y, sr)

                if analyzed_bpm and analyzed_key:
                    new_filename = f"00-{analyzed_bpm}-{analyzed_key}-{filename}"

            except Exception as e:
                print(f"\n[ERROR] Could not load {filename}: {e}")
                continue

        # --- Perform the renaming ---
        if new_filename and new_filename != filename:
            try:
                new_filepath = os.path.join(folder_path, new_filename)
                os.rename(filepath, new_filepath)
                print(f"Renamed to: {new_filename}\n")
                processed_count += 1
            except OSError as e:
                print(f"\n[ERROR] Could not rename {filename}: {e}")
        elif new_filename and new_filename == filename:
            print("  -> Analysis complete, no rename needed.\n")

    # Clean up macOS metadata files
    cleanup_macos_files(folder_path)

    print("---")
    print("Batch processing complete.")
    print(f"Successfully renamed: {processed_count} files.")
    print(f"Skipped (already processed): {skipped_count} files.")


# --- Main Execution (UPDATED) ---

if __name__ == "__main__":
    print("--- Music Key & BPM Renamer (Smart Fill) ---")
    print("WARNING: This script will rename files in place.\n")

    # Use command-line argument for the path
    if len(sys.argv) < 2:
        print("Error: No folder path provided.")
        print('Usage: python rename_music.py "/path/to/your/folder"')
        sys.exit(1)  # Exit with an error

    path = sys.argv[1]
    process_folder(path)
