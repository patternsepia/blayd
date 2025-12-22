import pygame
import hsluv
import spectra as sp
import sys 

# 1. LOAD PYGAME COLORS
_this_module = sys.modules[__name__]
for name, rgb in pygame.color.THECOLORS.items():
    setattr(_this_module, name.upper(), rgb)
    globals()[name.upper()] = rgb

# 2. DEFINE CUSTOM THEME COLORS (That Pygame may not have)

def GRIS(v: int) -> pygame.Color:
    """
    Returns a grey color tuple (v, v, v).
    """
    # Safety clamp to prevent crashes if v is out of bounds
    val = max(0, min(255, int(v)))
    return (val, val, val)

# 2. Leverage GRIS to generate cn.GRIS0 through cn.GRIS255
# Note: Pygame uses GRAY0 - GRAY100, and GREY0 - GREY100, as pct grayness, but we use absolute values.
# This allows us to type cn.GRIS69 or cn.GRIS120 anywhere in ourr code.
for i in range(256):
    setattr(_this_module, f"GRIS{i}", GRIS(i))

def df_scale(colors_list):
    """
    A smart wrapper for sp.scale().
    It accepts a list containing EITHER strings ("red") OR pygame.Color objects.
    It automatically converts Color objects to the Hex strings that Spectra needs.
    """
    sanitized = []
    for c in colors_list:
        if isinstance(c, (tuple, list)):
            # It's a Color object -> Auto-convert to Hex
            sanitized.append("#%02x%02x%02x" % c[:3])
        else:
            # It's already a string -> Keep it as is
            sanitized.append(c)
            
    return sp.scale(sanitized)    

# --- 1. Procedural Entity Colors ---

# --- 2. Lighting & Atmosphere ---
# Define a color cycle for the day-night cycle using Spectra
# define keyframes: Midnight -> Dawn -> Noon -> Dusk -> Midnight
# Now you can mix and match strings and Constants seamlessly!
_cycle = df_scale([
    MIDNIGHTBLUE,   # Uses the injected Pygame constant
    LIGHTSALMON,    # Uses the injected Pygame constant
    WHITE,        # Works with raw strings too!
    THISTLE,        
    MIDNIGHTBLUE
])
def get_day_night_cycle(t: float) -> tuple:
    """
    t: float from 0.0 (midnight) -> 0.5 (noon) -> 1.0 (midnight).
    Returns the ambient light color for the world.
    """
    return tuple(int(c) for c in _cycle(t).to("rgb").values)

# --- 3. UI & Feedback (Spectra & Pygame) ---

# Pre-load bulky colormaps to avoid re-calculating every frame
_veg = df_scale([SLATEGRAY,SIENNA, FORESTGREEN]).domain([0, 10, 100])
def get_terrain_color(pct: float) -> pygame.Color:
    """
    Returns a terrain color based on elevation.
    """
    return pygame.Color(_veg(pct).to("rgb").values)

_enc = df_scale([PALEGREEN,KHAKI, LIGHTSALMON]).domain([0, 100, 200])
def get_enc_color(pct: float) -> pygame.Color:
    """
    Returns an encumbrance color based on load.
    """
    return pygame.Color(_enc(pct).to("rgb").values)

_heat = df_scale([SKYBLUE,PALEGREEN, KHAKI, LIGHTSALMON]).domain([0, 100, 150, 200])
def get_heat_color(pct: float) -> pygame.Color:
    """
    Returns a heat color based on the temp thingy?
    """
    # TDOO: What is the temp thingy?
    return pygame.Color(_heat(pct).to("rgb").values)

# --- 5. Weather & Effects (HSLuv/Pygame) ---

#TODO Aerosols: fog, mist, smoke, dust, sandstorm, toxic

def apply_weather_tint(original: pygame.Color, weather_type: str) -> tuple:
    """
    Tints a sprite or screen color based on weather state.
    """
    tints = {
        "rain": DARKSLATEGREY,  # Dark Blue
        "sandstorm": SANDYBROWN, # Brown/Yellow
        "toxic": YELLOWGREEN,    # Green
        "none": WHITE # No tint
    }
    
    tint = tints.get(weather_type, pygame.Color(0,0,0))
    if weather_type == "none":
        return original

    # Linear interpolation towards the tint color
    return original.lerp(tint, 0.3) # 30% tint strength

# --- Internal State ---
# These are initially set to safe defaults so the game won't crash 
# if we forget to call configure().
_SETTINGS = {} 
_ACTIVE_ENCUMBRANCE = None
_ACTIVE_THERMAL = None
_ACTIVE_UI_THEME = None
_ACTIVE_CB_MATRIX = None

# --- Registries (The Hardcoded Presets) ---
_ENCUMBRANCE_SCALES = {
    "default": _enc,
    "high_contrast": sp.scale(["#FFFFFF", "#888888", "#000000"]).domain([0, 50, 100]),
}

_THERMAL_SCALES = {
    "default": _heat,
    "industrial": sp.scale(["#222222", "#D4AF37", "#FF4500"]).domain([0, 100, 200]),
}

_UI_THEMES = {
    "default": {"text": "#F0F0F0", "bg": "#000000", "highlight": "#AAAAFF"},
    "paper":   {"text": "#060606", "bg": "#F5F5DC", "highlight": "#451515"},
}

_CB_MATRICES = {
    "protanopia":  [[0.567, 0.433, 0.0], [0.558, 0.442, 0.0], [0.0, 0.242, 0.758]],
    "deuteranopia":[[0.625, 0.375, 0.0], [0.700, 0.300, 0.0], [0.0, 0.300, 0.700]],
}

# --- Configuration Hook ---

def configure(settings_data: dict):
    """
    Called by main.py. Updates the module's internal state based on JSON data.
    """
    global _SETTINGS, _ACTIVE_ENCUMBRANCE, _ACTIVE_THERMAL, _ACTIVE_UI_THEME, _ACTIVE_CB_MATRIX
    
    # Store the raw data
    _SETTINGS = settings_data.get("color", {})

    # 1. Pre-calculate Encumbrance Scale
    key_enc = _SETTINGS.get("encumbrance_scale", "default")
    _ACTIVE_ENCUMBRANCE = _ENCUMBRANCE_SCALES.get(key_enc, _ENCUMBRANCE_SCALES["default"])

    # 2. Pre-calculate Thermal Scale
    key_therm = _SETTINGS.get("thermal_scale", "default")
    _ACTIVE_THERMAL = _THERMAL_SCALES.get(key_therm, _THERMAL_SCALES["default"])

    # 3. Pre-calculate UI Theme
    key_ui = _SETTINGS.get("ui_theme", "default")
    _ACTIVE_UI_THEME = _UI_THEMES.get(key_ui, _UI_THEMES["default"])

    # 4. Pre-calculate Colorblind Matrix (Optimization)
    mode = _SETTINGS.get("colorblind_mode", "off").lower()
    _ACTIVE_CB_MATRIX = _CB_MATRICES.get(mode, None) # None means "off"

# Initialize with defaults immediately so module is safe to import
configure({"color": {}}) 

# --- Helpers ---

def _apply_cb_filter(c: pygame.Color) -> pygame.Color:
    """Applies the PRE-CALCULATED matrix. Fast."""
    if _ACTIVE_CB_MATRIX is None:
        return c

    r, g, b = c.r, c.g, c.b
    m = _ACTIVE_CB_MATRIX
    # Matrix multiplication
    nr = r*m[0][0] + g*m[0][1] + b*m[0][2]
    ng = r*m[1][0] + g*m[1][1] + b*m[1][2]
    nb = r*m[2][0] + g*m[2][1] + b*m[2][2]
    
    return pygame.Color(min(255, int(nr)), min(255, int(ng)), min(255, int(nb)), c.a)

# --- Public API ---

def get_ui_color(element: str) -> pygame.Color:
    hex_code = _ACTIVE_UI_THEME.get(element, "#FF00FF")
    return _apply_cb_filter(pygame.Color(hex_code))