from pathlib import Path

import omni.ui as ui
from omni.ui import color as cl


CURRENT_PATH = Path(__file__).parent.absolute()
ICON_PATH = CURRENT_PATH.parent.parent.parent.joinpath("icons")

cl.action_safe_default = cl(1.0, 0.0, 0.0)
cl.title_safe_default  = cl(1.0, 1.0, 0.0)
cl.custom_safe_default = cl(0.0, 1.0, 0.0)
cl.letterbox_default   = cl(0.0, 0.0, 0.0, 0.75)
cl.comp_lines_default  = cl(1.0, 1.0, 1.0, 0.6)

safe_areas_group_style = {
    "Label:disabled": {
        "color": cl(1.0, 1.0, 1.0, 0.2)
    },
    "FloatSlider:enabled": {
        "draw_mode": ui.SliderDrawMode.HANDLE,
        "background_color": cl(0.75, 0.75, 0.75, 1),
        "color": cl.black
    },
    "FloatSlider:disabled": {
        "draw_mode": ui.SliderDrawMode.HANDLE,
        "background_color": cl(0.75, 0.75, 0.75, 0.2),
        "color": cl(0.0, 0.0, 1.0, 0.2)
    },
    "CheckBox": {
        "background_color": cl(0.75, 0.75, 0.75, 1),
        "color": cl.black
    },
    "Rectangle::ActionSwatch": {
        "background_color": cl.action_safe_default
    },
    "Rectangle::TitleSwatch": {
        "background_color": cl.title_safe_default
    },
    "Rectangle::CustomSwatch": {
        "background_color": cl.custom_safe_default
    }
}
comp_group_style = {
    "Button.Image::Off": {
        "image_url": str(ICON_PATH / "off.png")
    },
    "Button.Image::Thirds": {
        "image_url": str(ICON_PATH / "thirds.png")
    },
    "Button.Image::Quad": {
        "image_url": str(ICON_PATH / "quad.png")
    },
    "Button.Image::Crosshair": {
        "image_url": str(ICON_PATH / "crosshair.png")
    },
    "Button:checked": {
        "background_color": cl(1.0, 1.0, 1.0, 0.2)
    }
}
