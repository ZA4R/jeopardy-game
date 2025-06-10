# music.py
import pygame
import os
import glob
import random
import logging 

logger = logging.getLogger(__name__)

# --- Categorized Music Lists (these will be imported) ---
title_music_list = []
final_music_list = []
victory_music_list = []

# Define common audio extensions
AUDIO_EXTENSIONS = ['*.mp3']

# --- Music Loading Function ---
def load_music_files(MUSIC_DIR):
    """
    Loads music file paths from the MUSIC_DIR into categorized lists.
    This function should be called once during game initialization.
    """
    if not os.path.exists(MUSIC_DIR):
        logger.error(f"Music directory '{MUSIC_DIR}' not found. No music will be loaded.")
        return # Exit if directory doesn't exist

    # Clear lists to prevent double-loading if function is called multiple times
    title_music_list.clear()
    final_music_list.clear()
    victory_music_list.clear()



    # Load Title Music
    for ext in AUDIO_EXTENSIONS:
        title_music_list.extend(glob.glob(os.path.join(MUSIC_DIR, f'title*{ext}')))

    # Load Final Music
    for ext in AUDIO_EXTENSIONS:
        final_music_list.extend(glob.glob(os.path.join(MUSIC_DIR, f'final*{ext}')))

    # Load Victory Music
    for ext in AUDIO_EXTENSIONS:
        victory_music_list.extend(glob.glob(os.path.join(MUSIC_DIR, f'winner*{ext}')))



    # Shuffle lists for randomness within categories 
    random.shuffle(title_music_list)
    random.shuffle(final_music_list)
    random.shuffle(victory_music_list)

    logger.info(f"Loaded {len(title_music_list)} title songs, {len(final_music_list)} final songs, {len(victory_music_list)} victory songs.")

# Music Control Functions
def play_music(song_path, loops=-1, volume=0.5):
    """Starts playing a specific music file."""
    if not pygame.mixer.get_init():
        logger.warning("Pygame mixer not initialized. Cannot play music.")
        return

    if not os.path.exists(song_path):
        logger.error(f"Music file not found: {song_path}")
        return

    try:
        pygame.mixer.music.load(song_path)
        pygame.mixer.music.set_volume(volume)
        pygame.mixer.music.play(loops)
        logger.info(f"Playing: {os.path.basename(song_path)}")
    except pygame.error as e:
        logger.error(f"Error playing music '{os.path.basename(song_path)}': {e}")

def stop_music():
    """Stops the currently playing music."""
    if pygame.mixer.get_init() and pygame.mixer.music.get_busy():
        pygame.mixer.music.stop()
        logger.info("Music stopped.")

def set_music_volume(volume):
    """Sets the music volume (0.0 to 1.0)."""
    if pygame.mixer.get_init():
        pygame.mixer.music.set_volume(volume)
    else:
        logger.warning("Pygame mixer not initialized. Cannot set volume.")

