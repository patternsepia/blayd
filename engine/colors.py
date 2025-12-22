import pygame
import spectra as sp
import hsluv
import sys
from typing import Union, List, Tuple, Dict, Any, Optional

# --- 1. MODULE SELF-REFERENCE ---
_this_module = sys.modules[__name__]

# --- 2. INJECT STANDARD PYGAME COLORS ---
# Allows usage like cn.RED or cn.MINTCREAM immediately.
if pygame.get_init():
    for name, rgb in pygame.color.THECOLORS.items():
        # Inject into module namespace (cn.RED)
        setattr(_this_module, name.upper(), rgb)

# --- 3. CUSTOM COLOR GENERATORS ---

def GRIS(v: int) -> pygame.Color:
    """Returns a robust grey color tuple (v, v, v)."""
    val = max(0, min(255, int(v)))
    return pygame.Color(val, val, val)

# Generate cn.GRIS0 through cn.GRIS255
for i in range(256):
    setattr(_this_module, f"GRIS{i}", GRIS(i))

# --- 4. THE "JUST WORKS" RESOLVER ---

def get(value: Union[str, Tuple, List, Dict, pygame.Color]) -> pygame.Color:
    """
    The universal color resolver. 
    Pass anything reasonable, get a pygame.Color object.
    
    Usage:
        cn.get("red")             -> Color(255, 0, 0)
        cn.get("GRIS128")         -> Color(128, 128, 128)
        cn.get("cornflowerblue")  -> Color(100, 149, 237)
        cn.get((0, 255, 0))       -> Color(0, 255, 0)
    """
    # 1. Already a Color object?
    if isinstance(value, pygame.Color):
        return value

    # 2. Tuple or List? (Assume RGB or RGBA)
    if isinstance(value, (tuple, list)):
        return pygame.Color(*value)

    # 3. Dictionary? (Handle JSON data structures)
    if isinstance(value, dict):
        if "color" in value: return get(value["color"])
        if "name" in value:  return get(value["name"])
        if "hex" in value:   return get(value["hex"])
        # Fallback for simple dicts like {'r': 255, 'g': 0, 'b': 0}
        r = value.get('r', 0)
        g = value.get('g', 0)
        b = value.get('b', 0)
        a = value.get('a', 255)
        return pygame.Color(r, g, b, a)

    # 4. String? (The magic part)
    if isinstance(value, str):
        # A. Check our module constants (e.g., "GRIS50", "MIDNIGHTBLUE")
        if hasattr(_this_module, value):
            return getattr(_this_module, value)
        if hasattr(_this_module, value.upper()):
            return getattr(_this_module, value.upper())

        # B. Check Standard Pygame/Hex/HTML names
        try:
            return pygame.Color(value)
        except ValueError:
            pass
            
    # 5. Fallback (Bright Pink to indicate error visibly)
    print(f"[Color] Warning: Could not resolve color '{value}'. returning MAGENTA.")
    return pygame.Color("magenta")

# --- 5. SPECTRA INTEGRATION ---

def df_scale(colors_list: List[Any]):
    """
    Smart wrapper for spectra.scale().
    Accepts mix of strings, tuples, or pygame.Colors.
    """
    sanitized = []
    for c in colors_list:
        # Use our universal getter to resolve it to a Color first
        col = get(c)
        # Spectra prefers Hex strings
        sanitized.append("#%02x%02x%02x" % (col.r, col.g, col.b))
            
    return sp.scale(sanitized)    

# --- 6. PALETTES & THEMES ---

# Day-Night Cycle
_cycle = df_scale([
    "midnightblue", 
    "lightsalmon",    
    "white",        
    "thistle",        
    "midnightblue"
])

def get_day_night_cycle(t: float) -> Tuple[int, int, int]:
    """t: 0.0 (midnight) -> 0.5 (noon) -> 1.0 (midnight)."""
    vals = _cycle(t).to("rgb").values
    return tuple(int(c) for c in vals)

# Terrain / Encumbrance / Heat
_veg = df_scale(["slategray", "sienna", "forestgreen"]).domain([0, 10, 100])
_enc = df_scale(["palegreen", "khaki", "lightsalmon"]).domain([0, 100, 200])
_heat = df_scale(["skyblue", "palegreen", "khaki", "lightsalmon"]).domain([0, 100, 150, 200])

def get_terrain_color(pct: float) -> pygame.Color:
    return pygame.Color(*[int(c) for c in _veg(pct).to("rgb").values])

def get_enc_color(pct: float) -> pygame.Color:
    return pygame.Color(*[int(c) for c in _enc(pct).to("rgb").values])

def get_heat_color(pct: float) -> pygame.Color:
    return pygame.Color(*[int(c) for c in _heat(pct).to("rgb").values])

# --- 7. WEATHER & TINTS ---

def apply_weather_tint(original: pygame.Color, weather_type: str) -> pygame.Color:
    original = get(original) # Ensure input is valid
    
    tints = {
        "rain":      get("darkslategray"),
        "sandstorm": get("sandybrown"),
        "toxic":     get("yellowgreen"),
        "none":      get("white")
    }
    
    tint = tints.get(weather_type, get("white"))
    if weather_type == "none" or not tint:
        return original

    return original.lerp(tint, 0.3)

# --- 8. CONFIGURATION & STATE ---

_SETTINGS = {} 
_ACTIVE_ENCUMBRANCE = _enc
_ACTIVE_THERMAL = _heat
_ACTIVE_UI_THEME = {"text": "whitesmoke", "bg": "black", "highlight": "cornflowerblue"}
_ACTIVE_CB_MATRIX = None

_CB_MATRICES = {
    "protanopia":  [[0.567, 0.433, 0.0], [0.558, 0.442, 0.0], [0.0, 0.242, 0.758]],
    "deuteranopia":[[0.625, 0.375, 0.0], [0.700, 0.300, 0.0], [0.0, 0.300, 0.700]],
}

# --- REGISTRIES ---
# Replaced hex with readable names or GRIS values

_ENCUMBRANCE_SCALES = {
    "default": _enc,
    "high_contrast": df_scale(["white", "gray", "black"]).domain([0, 50, 100]),
}

_THERMAL_SCALES = {
    "default": _heat,
    "industrial": df_scale(["GRIS34", "goldenrod", "orangered"]).domain([0, 100, 200]),
}

_UI_THEMES = {
    "default": {"text": "whitesmoke", "bg": "black", "highlight": "cornflowerblue"},
    "paper":   {"text": "GRIS6",      "bg": "beige", "highlight": "maroon"},
}

def configure(settings_data: Dict[str, Any]):
    global _SETTINGS, _ACTIVE_UI_THEME, _ACTIVE_CB_MATRIX
    
    _SETTINGS = settings_data.get("color", {})

    # UI Theme
    key_ui = _SETTINGS.get("ui_theme", "default")
    _ACTIVE_UI_THEME = _UI_THEMES.get(key_ui, _UI_THEMES["default"])

    # Colorblind Mode
    mode = _SETTINGS.get("colorblind_mode", "off").lower()
    _ACTIVE_CB_MATRIX = _CB_MATRICES.get(mode, None)

# Initialize defaults
configure({"color": {}}) 

def _apply_cb_filter(c: pygame.Color) -> pygame.Color:
    if _ACTIVE_CB_MATRIX is None:
        return c

    r, g, b = c.r, c.g, c.b
    m = _ACTIVE_CB_MATRIX
    nr = r*m[0][0] + g*m[0][1] + b*m[0][2]
    ng = r*m[1][0] + g*m[1][1] + b*m[1][2]
    nb = r*m[2][0] + g*m[2][1] + b*m[2][2]
    
    return pygame.Color(min(255, int(nr)), min(255, int(ng)), min(255, int(nb)), c.a)

def get_ui_color(element: str) -> pygame.Color:
    """Returns a themed UI color (text, bg, highlight) with CB filter applied."""
    color_val = _ACTIVE_UI_THEME.get(element, "magenta")
    return _apply_cb_filter(get(color_val))