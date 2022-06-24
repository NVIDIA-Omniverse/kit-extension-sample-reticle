"""Constants used by the CameraReticleExtension"""
import enum


class CompositionGuidelines(enum.IntEnum):
    """Enum representing all of the composition modes."""
    OFF = 0
    THIRDS = 1
    QUAD = 2
    CROSSHAIR = 3


DEFAULT_ACTION_SAFE_PERCENTAGE = 93
DEFAULT_TITLE_SAFE_PERCENTAGE = 90
DEFAULT_CUSTOM_SAFE_PERCENTAGE = 85
DEFAULT_LETTERBOX_RATIO = 2.35
DEFAULT_COMPOSITION_MODE = CompositionGuidelines.OFF

SETTING_RESOLUTION_WIDTH = "/app/renderer/resolution/width"
SETTING_RESOLUTION_HEIGHT = "/app/renderer/resolution/height"
SETTING_RESOLUTION_FILL = "/app/runLoops/rendering_0/fillResolution"
