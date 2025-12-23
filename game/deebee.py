import pygame

# --- META SETTINGS ---
TITLE = "Blayd"

# --- VISUAL SCALE ---
TILESIZE = 16

# --- SIMULATION: SCALE ---
CENTIMETERS_PER_TILE = 25
METERS_PER_TILE = CENTIMETERS_PER_TILE / 100
TILES_PER_METER = 1 / METERS_PER_TILE

# --- SIMULATION: LOCOMOTION MULTIPLIERS---
CRAWL_X = 0.375 # about 0.46875 meters per second
SNEAK_X = 0.75 # about 0.9375 meters per second
WALK_X = 1.0 # about 1.25 meters per second
JOG_X = 1.5 # about 1.875 meters per second
RUN_X = 2.0 # about 3.0 meters per second

# --- SIMULATION: BALLISTICS ---
GRAVITY = 9.81 # meters per second squared
T_stp = 15.0 # degrees Celsius
P_stp = 101325 # kilopascals, 1 atmosphere
AIR_ro = 1.225 # kilograms per cubic meter at sea level and 15 degrees Celsius and 101325 kilopascals

# --- UI SETTINGS ---
UI_FONT = 'arial'
UI_FONT_SIZE = 20

import os
import json


def load_settings(defaults: dict = None) -> dict:
    """
    Loads settings.json and merges it with the provided defaults.
    If the file is missing or broken, it silently falls back to defaults.
    """
    if defaults is None:
        defaults = {}

    # Check if file exists to avoid crashing
    settings_file = os.path.join(DATA_DIR, "settings.json")
    if not os.path.exists(settings_file):
        print(f"Warning: Items file not found at {DATA_DIR}")
        return {} 
    try:
        with open(settings_file, "r") as f:
            user_data = json.load(f)
            
        # Merge user_data ON TOP of defaults
        # This allows settings.json to be partial (e.g. only contain window settings)
        return _deep_merge(defaults, user_data)

    except json.JSONDecodeError as e:
        print(f"[Loader] Error: settings.json is malformed ({e}). Using defaults.")
        return defaults

def _deep_merge(base: dict, update: dict) -> dict:
    """
    Recursive merge. 
    If base has {"window": {"w": 800, "h": 600}} 
    and update has {"window": {"w": 1920}}, 
    Result is {"window": {"w": 1920, "h": 600}}.
    """
    # Create a copy so we don't mutate the original 'defaults'
    result = base.copy()
    
    for key, value in update.items():
        # If both sides are dictionaries, dive deeper
        if key in result and isinstance(result[key], dict) and isinstance(value, dict):
            result[key] = _deep_merge(result[key], value)
        else:
            # Otherwise, just overwrite
            result[key] = value
            
    return result

# --- FILE PATHS ---
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ASSET_DIR = os.path.join(BASE_DIR, "assets")
DATA_DIR = os.path.join(BASE_DIR, "data")
SAVE_FILE = os.path.join(DATA_DIR, "saves", "savegame.json")

# --- 1. The Hardcoded Defaults (Safety Net) ---
# Use these if settings.json is missing or broken
_DEFAULT_WIDTH = 800
_DEFAULT_HEIGHT = 600
_DEFAULT_TPS = 100
_DEFAULT_FPS = 60
_DEFAULT_SHOW_FPS = False
_DEFAULT_SHOW_TPS = False
_DEFAULT_VOLUME = 1.0
_DEFAULT_THEME = "default"

# --- 2. Load the User Settings ---
# Load right here at the module level. 
# When main.py imports 'constants', this code runs immediately.
_user_settings = load_settings()
_window_prefs = _user_settings.get("window", {})
_perf_prefs = _user_settings.get("performance", {})
_audio_prefs = _user_settings.get("audio", {})
_color_prefs = _user_settings.get("colors", {})
_log_prefs = _user_settings.get("logging", {})

# Window settings
WIDTH = _window_prefs.get("width", _DEFAULT_WIDTH)
HEIGHT = _window_prefs.get("height", _DEFAULT_HEIGHT)

# Logging settings
LOG_CONFIG = {
    "level": _log_prefs.get("level", "INFO"),
    "file": os.path.join(DATA_DIR, "logs", _log_prefs.get("filename", "blayd.log")),
    "format": _log_prefs.get("format", "%(asctime)s [%(levelname)s] %(name)s: %(message)s")
}

# Performance settings
TPS = _perf_prefs.get("tps", _DEFAULT_TPS)
FPS = _perf_prefs.get("fps", _DEFAULT_FPS)
SHOW_FPS = _perf_prefs.get("show_fps", _DEFAULT_SHOW_FPS)
SHOW_TPS = _perf_prefs.get("show_tps", _DEFAULT_SHOW_TPS)

# Audio settings
MASTER_VOLUME = _audio_prefs.get("master_volume", _DEFAULT_VOLUME)
MUSIC_VOLUME = _audio_prefs.get("music_volume", _DEFAULT_VOLUME)
SFX_VOLUME = _audio_prefs.get("sfx_volume", _DEFAULT_VOLUME)
AMBIENT_VOLUME = _audio_prefs.get("ambient_volume", _DEFAULT_VOLUME)
VOICE_VOLUME = _audio_prefs.get("voice_volume", _DEFAULT_VOLUME)

# Theme settings
THEME = _color_prefs.get("theme", _DEFAULT_THEME)

# CALCULATED VALUES
GRID_WIDTH = WIDTH // TILESIZE
GRID_HEIGHT = HEIGHT // TILESIZE
SCREEN_CENTER_X = WIDTH / 2
SCREEN_CENTER_Y = HEIGHT / 2
SCREEN_CENTER = (SCREEN_CENTER_X, SCREEN_CENTER_Y)

# --- INPUT BINDINGS ---
KEY_BINDINGS = {
    # --- MOVEMENT ---
    "UP":       [pygame.K_UP, pygame.K_w, pygame.K_KP8],
    "DOWN":     [pygame.K_DOWN, pygame.K_s, pygame.K_KP2],
    "LEFT":     [pygame.K_LEFT, pygame.K_a, pygame.K_KP4],
    "RIGHT":    [pygame.K_RIGHT, pygame.K_d, pygame.K_KP6],
    "WAIT":     [pygame.K_PERIOD, pygame.K_KP5, pygame.K_KP_PERIOD],
    "JUMP":     [pygame.K_SPACE],
    "CYCLE":    [pygame.K_TAB],

    # --- INTERACTION ---
    "PICKUP":   [pygame.K_g],
    "INTERACT": [pygame.K_e],
    "AIM":      [pygame.K_f],
    "FIRE":     [pygame.K_f, pygame.K_RETURN],
    "RELOAD":   [pygame.K_r],
    "OPEN":     [pygame.K_o],
    "CLOSE":    [pygame.K_c],
    "BASH":     [pygame.K_b],
    "ZAP":      [pygame.K_z],

    # --- INVENTORY ---
    "INSPECT":        [pygame.K_i],
    "THROW":          [pygame.K_t],
    "ACTIVATE":       [pygame.K_a],
    "REFILL":         [pygame.K_r],
    "DROP":           [pygame.K_d],
    "EAT":            [pygame.K_e],
    "QUAFF":          [pygame.K_q],
    "WIELD":          [pygame.K_w],
    "WEAR":           [pygame.K_PLUS, pygame.K_KP_PLUS],
    "UNWEAR":         [pygame.K_MINUS, pygame.K_KP_MINUS],
    "ENTER_CONTAINER":[pygame.K_GREATER, pygame.K_PERIOD],
    "EXIT_CONTAINER": [pygame.K_LESS, pygame.K_COMMA],

    # --- SYSTEM ---
    "CONFIRM":  [pygame.K_RETURN, pygame.K_KP_ENTER],
    "CANCEL":   [pygame.K_ESCAPE, pygame.K_BACKSPACE],
    "MENU":     [pygame.K_ESCAPE],
    
    # --- META ---
    "SAVE":     [pygame.K_s], 
    "LOAD":     [pygame.K_l],
    "QUIT":     [pygame.K_q],
    "DEBUG_CONSOLE": [pygame.K_BACKQUOTE],
}
