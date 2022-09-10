from functools import partial

import carb
import omni.ui as ui
from omni.ui import color as cl
from omni.ui import scene

from . import constants
from .constants import CompositionGuidelines
from .models import ReticleModel
from . import styles


class ReticleOverlay:
    """The reticle viewport overlay.

    Build the reticle graphics and ReticleMenu button on the given viewport window.
    """
    _instances = []

    def __init__(self, model: ReticleModel, vp_win: ui.Window, ext_id: str):
        """ReticleOverlay constructor

        Args:
            model (ReticleModel): The reticle model
            vp_win (Window): The viewport window to build the overlay on.
            ext_id (str): The extension id.
        """
        self.model = model
        self.vp_win = vp_win
        self.ext_id = ext_id
        # Rebuild the overlay whenever the viewport window changes
        self.vp_win.set_height_changed_fn(self.on_window_changed)
        self.vp_win.set_width_changed_fn(self.on_window_changed)
        self._view_change_sub = None
        try:
            # VP2 resolution change sub
            self._view_change_sub = self.vp_win.viewport_api.subscribe_to_view_change(self.on_window_changed)
        except AttributeError:
            carb.log_info("Using Viewport Legacy: Reticle will not automatically update on resolution changes.")
                                                                            
        # Rebuild the overlay whenever the model changes
        self.model.add_reticle_changed_fn(self.build_viewport_overlay)
        ReticleOverlay._instances.append(self)
        resolution = self.vp_win.viewport_api.get_texture_resolution()
        self._aspect_ratio = resolution[0] / resolution[1]

    @classmethod
    def get_instances(cls):
        """Get all created instances of ReticleOverlay"""
        return cls._instances
    
    def __del__(self):
        self.destroy()

    def destroy(self):
        self._view_change_sub = None
        self.scene_view.scene.clear()
        self.scene_view = None
        self.reticle_menu.destroy()
        self.reticle_menu = None
        self.vp_win = None

    def on_window_changed(self, *args):
        """Update aspect ratio and rebuild overlay when viewport window changes."""
        if self.vp_win is None:
            return
        
        settings = carb.settings.get_settings()
        if type(self.vp_win).__name__ == "LegacyViewportWindow":
            fill = settings.get(constants.SETTING_RESOLUTION_FILL)
        else:
            fill = self.vp_win.viewport_api.fill_frame
        
        if fill:
            width = self.vp_win.frame.computed_width + 8
            height = self.vp_win.height
        else:
            width, height = self.vp_win.viewport_api.resolution
        self._aspect_ratio = width / height
        self.build_viewport_overlay()

    def get_aspect_ratio_flip_threshold(self):
        """Get magic number for aspect ratio policy.

        Aspect ratio policy doesn't seem to swap exactly when window_aspect_ratio == window_texture_aspect_ratio.
        This is a hack that approximates where the policy changes.
        """
        return self.get_aspect_ratio() - self.get_aspect_ratio() * 0.05

    def build_viewport_overlay(self, *args):
        """Build all viewport graphics and ReticleMenu button."""
        if self.vp_win is not None:
            # Create a unique frame for our overlay
            with self.vp_win.get_frame(self.ext_id):
                with ui.ZStack():
                    # Set the aspect ratio policy depending if the viewport is wider than it is taller or vice versa.
                    if self.vp_win.width / self.vp_win.height > self.get_aspect_ratio_flip_threshold():
                        self.scene_view = scene.SceneView(aspect_ratio_policy=scene.AspectRatioPolicy.PRESERVE_ASPECT_VERTICAL)
                    else:
                        self.scene_view = scene.SceneView(aspect_ratio_policy=scene.AspectRatioPolicy.PRESERVE_ASPECT_HORIZONTAL)

                    # Build all the scene view guidelines
                    with self.scene_view.scene:
                        if self.model.composition_mode.as_int == CompositionGuidelines.THIRDS:
                            self._build_thirds()
                        elif self.model.composition_mode.as_int == CompositionGuidelines.QUAD:
                            self._build_quad()
                        elif self.model.composition_mode.as_int == CompositionGuidelines.CROSSHAIR:
                            self._build_crosshair()

                        if self.model.action_safe_enabled.as_bool:
                            self._build_safe_rect(self.model.action_safe_percentage.as_float / 100.0,
                                                  color=cl.action_safe_default)
                        if self.model.title_safe_enabled.as_bool:
                            self._build_safe_rect(self.model.title_safe_percentage.as_float / 100.0,
                                                  color=cl.title_safe_default)
                        if self.model.custom_safe_enabled.as_bool:
                            self._build_safe_rect(self.model.custom_safe_percentage.as_float / 100.0,
                                                  color=cl.custom_safe_default)
                        if self.model.letterbox_enabled.as_bool:
                            self._build_letterbox()

                    # Build ReticleMenu button
                    with ui.VStack():
                        ui.Spacer()
                        with ui.HStack(height=0):
                            ui.Spacer()
                            self.reticle_menu = ReticleMenu(self.model)

    def _build_thirds(self):
        """Build the scene ui graphics for the Thirds composition mode."""
        aspect_ratio = self.get_aspect_ratio()
        line_color = cl.comp_lines_default
        inverse_ratio = 1 / aspect_ratio
        if self.scene_view.aspect_ratio_policy == scene.AspectRatioPolicy.PRESERVE_ASPECT_VERTICAL:
            scene.Line([-0.333 * aspect_ratio, -1, 0], [-0.333 * aspect_ratio, 1, 0], color=line_color)
            scene.Line([0.333 * aspect_ratio, -1, 0], [0.333 * aspect_ratio, 1, 0], color=line_color)
            scene.Line([-aspect_ratio, -0.333, 0], [aspect_ratio, -0.333, 0], color=line_color)
            scene.Line([-aspect_ratio, 0.333, 0], [aspect_ratio, 0.333, 0], color=line_color)
        else:
            scene.Line([-1, -0.333 * inverse_ratio, 0], [1, -0.333 * inverse_ratio, 0], color=line_color)
            scene.Line([-1, 0.333 * inverse_ratio, 0], [1, 0.333 * inverse_ratio, 0], color=line_color)
            scene.Line([-0.333, -inverse_ratio, 0], [-0.333, inverse_ratio, 0], color=line_color)
            scene.Line([0.333, -inverse_ratio, 0], [0.333, inverse_ratio, 0], color=line_color)

    def _build_quad(self):
        """Build the scene ui graphics for the Quad composition mode."""
        aspect_ratio = self.get_aspect_ratio()
        line_color = cl.comp_lines_default
        inverse_ratio = 1 / aspect_ratio
        if self.scene_view.aspect_ratio_policy == scene.AspectRatioPolicy.PRESERVE_ASPECT_VERTICAL:
            scene.Line([0, -1, 0], [0, 1, 0], color=line_color)
            scene.Line([-aspect_ratio, 0, 0], [aspect_ratio, 0, 0], color=line_color)
        else:
            scene.Line([0, -inverse_ratio, 0], [0, inverse_ratio, 0], color=line_color)
            scene.Line([-1, 0, 0], [1, 0, 0], color=line_color)

    def _build_crosshair(self):
        """Build the scene ui graphics for the Crosshair composition mode."""
        aspect_ratio = self.get_aspect_ratio()
        line_color = cl.comp_lines_default
        if self.scene_view.aspect_ratio_policy == scene.AspectRatioPolicy.PRESERVE_ASPECT_VERTICAL:
            scene.Line([0, 0.05 * aspect_ratio, 0], [0, 0.1 * aspect_ratio, 0], color=line_color)
            scene.Line([0, -0.05 * aspect_ratio, 0], [0, -0.1 * aspect_ratio, 0], color=line_color)
            scene.Line([0.05 * aspect_ratio, 0, 0], [0.1 * aspect_ratio, 0, 0], color=line_color)
            scene.Line([-0.05 * aspect_ratio, 0, 0], [-0.1 * aspect_ratio, 0, 0], color=line_color)
        else:
            scene.Line([0, 0.05 * 1, 0], [0, 0.1 * 1, 0], color=line_color)
            scene.Line([0, -0.05 * 1, 0], [0, -0.1 * 1, 0], color=line_color)
            scene.Line([0.05 * 1, 0, 0], [0.1 * 1, 0, 0], color=line_color)
            scene.Line([-0.05 * 1, 0, 0], [-0.1 * 1, 0, 0], color=line_color)

        scene.Points([[0.00005, 0, 0]], sizes=[2], colors=[line_color])

    def _build_safe_rect(self, percentage, color):
        """Build the scene ui graphics for the safe area rectangle

        Args:
            percentage (float): The 0-1 percentage the render target that the rectangle should fill.
            color: The color to draw the rectangle wireframe with.
        """
        aspect_ratio = self.get_aspect_ratio()
        inverse_ratio = 1 / aspect_ratio
        if self.scene_view.aspect_ratio_policy == scene.AspectRatioPolicy.PRESERVE_ASPECT_VERTICAL:
            scene.Rectangle(aspect_ratio*2*percentage, 1*2*percentage, thickness=1, wireframe=True, color=color)
        else:
            scene.Rectangle(1*2*percentage, inverse_ratio*2*percentage, thickness=1, wireframe=True, color=color)

    def _build_letterbox(self):
        """Build the scene ui graphics for the letterbox."""
        aspect_ratio = self.get_aspect_ratio()
        letterbox_color = cl.letterbox_default
        letterbox_ratio = self.model.letterbox_ratio.as_float

        def build_letterbox_helper(width, height, x_offset, y_offset):
            move = scene.Matrix44.get_translation_matrix(x_offset, y_offset, 0)
            with scene.Transform(transform=move):
                scene.Rectangle(width * 2, height * 2, thickness=0, wireframe=False, color=letterbox_color)
            move = scene.Matrix44.get_translation_matrix(-x_offset, -y_offset, 0)
            with scene.Transform(transform=move):
                scene.Rectangle(width * 2, height * 2, thickness=0, wireframe=False, color=letterbox_color)

        if self.scene_view.aspect_ratio_policy == scene.AspectRatioPolicy.PRESERVE_ASPECT_VERTICAL:
            if letterbox_ratio >= aspect_ratio:
                height = 1 - aspect_ratio / letterbox_ratio
                rect_height = height / 2
                rect_offset = 1 - rect_height
                build_letterbox_helper(aspect_ratio, rect_height, 0, rect_offset)
            else:
                width = aspect_ratio - letterbox_ratio
                rect_width = width / 2
                rect_offset = aspect_ratio - rect_width
                build_letterbox_helper(rect_width, 1, rect_offset, 0)
        else:
            inverse_ratio = 1 / aspect_ratio
            if letterbox_ratio >= aspect_ratio:
                height = inverse_ratio - 1 / letterbox_ratio
                rect_height = height / 2
                rect_offset = inverse_ratio - rect_height
                build_letterbox_helper(1, rect_height, 0, rect_offset)
            else:
                width = (aspect_ratio - letterbox_ratio) * inverse_ratio
                rect_width = width / 2
                rect_offset = 1 - rect_width
                build_letterbox_helper(rect_width, inverse_ratio, rect_offset, 0)

    def get_aspect_ratio(self):
        """Get the aspect ratio of the viewport.

        Returns:
            float: The viewport aspect ratio.
        """
        return self._aspect_ratio


class ReticleMenu:
    """The popup reticle menu"""
    def __init__(self, model: ReticleModel):
        """ReticleMenu constructor

        Stores the model and builds the Reticle button.

        Args:
            model (ReticleModel): The reticle model
        """
        self.model = model
        self.button = ui.Button("Reticle", width=0, height=0, mouse_pressed_fn=self.show_reticle_menu,
                                style={"margin": 10, "padding": 5, "color": cl.white})
        self.reticle_menu = None

    def destroy(self):
        self.button.destroy()
        self.button = None
        self.reticle_menu = None

    def on_group_check_changed(self, safe_area_group, model):
        """Enables/disables safe area groups

        When a safe area checkbox state changes, all the widgets of the respective
        group should be enabled/disabled.

        Args:
            safe_area_group (HStack): The safe area group to enable/disable
            model (SimpleBoolModel): The safe group checkbox model.
        """
        safe_area_group.enabled = model.as_bool

    def on_composition_mode_changed(self, guideline_type):
        """Sets the selected composition mode.

        When a composition button is clicked, it should be checked on and the other
        buttons should be checked off. Sets the composition mode on the ReticleModel too.

        Args:
            guideline_type (_type_): _description_
        """
        self.model.composition_mode.set_value(guideline_type)
        self.comp_off_button.checked = guideline_type == CompositionGuidelines.OFF
        self.comp_thirds_button.checked = guideline_type == CompositionGuidelines.THIRDS
        self.comp_quad_button.checked = guideline_type == CompositionGuidelines.QUAD
        self.comp_crosshair_button.checked = guideline_type == CompositionGuidelines.CROSSHAIR

    def show_reticle_menu(self, x, y, button, modifier):
        """Build and show the reticle menu popup."""
        self.reticle_menu = ui.Menu("Reticle", width=400, height=200)
        self.reticle_menu.clear()

        with self.reticle_menu:
            with ui.Frame(width=0, height=100):
                with ui.HStack():
                    with ui.VStack():
                        ui.Label("Composition", alignment=ui.Alignment.LEFT, height=30)
                        with ui.VGrid(style=styles.comp_group_style, width=150, height=0,
                                      column_count=2, row_height=75):
                            current_comp_mode = self.model.composition_mode.as_int
                            with ui.HStack():
                                off_checked = current_comp_mode == CompositionGuidelines.OFF
                                callback = partial(self.on_composition_mode_changed, CompositionGuidelines.OFF)
                                self.comp_off_button = ui.Button("Off", name="Off", checked=off_checked,
                                                                 width=70, height=70, clicked_fn=callback)
                            with ui.HStack():
                                thirds_checked = current_comp_mode == CompositionGuidelines.THIRDS
                                callback = partial(self.on_composition_mode_changed, CompositionGuidelines.THIRDS)
                                self.comp_thirds_button = ui.Button("Thirds", name="Thirds", checked=thirds_checked,
                                                                    width=70, height=70, clicked_fn=callback)
                            with ui.HStack():
                                quad_checked = current_comp_mode == CompositionGuidelines.QUAD
                                callback = partial(self.on_composition_mode_changed, CompositionGuidelines.QUAD)
                                self.comp_quad_button = ui.Button("Quad", name="Quad", checked=quad_checked,
                                                                  width=70, height=70, clicked_fn=callback)
                            with ui.HStack():
                                crosshair_checked = current_comp_mode == CompositionGuidelines.CROSSHAIR
                                callback = partial(self.on_composition_mode_changed,
                                                   CompositionGuidelines.CROSSHAIR)
                                self.comp_crosshair_button = ui.Button("Crosshair", name="Crosshair",
                                                                       checked=crosshair_checked, width=70, height=70,
                                                                       clicked_fn=callback)
                    ui.Spacer(width=10)
                    with ui.VStack(style=styles.safe_areas_group_style):
                        ui.Label("Safe Areas", alignment=ui.Alignment.LEFT, height=30)
                        with ui.HStack(width=0):
                            ui.Spacer(width=20)
                            cb = ui.CheckBox(model=self.model.action_safe_enabled)
                            action_safe_group = ui.HStack(enabled=self.model.action_safe_enabled.as_bool)
                            callback = partial(self.on_group_check_changed, action_safe_group)
                            cb.model.add_value_changed_fn(callback)
                            with action_safe_group:
                                ui.Spacer(width=10)
                                ui.Label("Action Safe", alignment=ui.Alignment.TOP)
                                ui.Spacer(width=14)
                                with ui.VStack():
                                    ui.FloatSlider(self.model.action_safe_percentage, width=100,
                                                   format="%.0f%%", min=0, max=100, step=1)
                                    ui.Rectangle(name="ActionSwatch", height=5)
                                    ui.Spacer()
                        with ui.HStack(width=0):
                            ui.Spacer(width=20)
                            cb = ui.CheckBox(model=self.model.title_safe_enabled)
                            title_safe_group = ui.HStack(enabled=self.model.title_safe_enabled.as_bool)
                            callback = partial(self.on_group_check_changed, title_safe_group)
                            cb.model.add_value_changed_fn(callback)
                            with title_safe_group:
                                ui.Spacer(width=10)
                                ui.Label("Title Safe", alignment=ui.Alignment.TOP)
                                ui.Spacer(width=25)
                                with ui.VStack():
                                    ui.FloatSlider(self.model.title_safe_percentage, width=100,
                                                   format="%.0f%%", min=0, max=100, step=1)
                                    ui.Rectangle(name="TitleSwatch", height=5)
                                    ui.Spacer()
                        with ui.HStack(width=0):
                            ui.Spacer(width=20)
                            cb = ui.CheckBox(model=self.model.custom_safe_enabled)
                            custom_safe_group = ui.HStack(enabled=self.model.custom_safe_enabled.as_bool)
                            callback = partial(self.on_group_check_changed, custom_safe_group)
                            cb.model.add_value_changed_fn(callback)
                            with custom_safe_group:
                                ui.Spacer(width=10)
                                ui.Label("Custom Safe", alignment=ui.Alignment.TOP)
                                ui.Spacer(width=5)
                                with ui.VStack():
                                    ui.FloatSlider(self.model.custom_safe_percentage, width=100,
                                                   format="%.0f%%", min=0, max=100, step=1)
                                    ui.Rectangle(name="CustomSwatch", height=5)
                                    ui.Spacer()
                        ui.Label("Letterbox", alignment=ui.Alignment.LEFT, height=30)
                        with ui.HStack(width=0):
                            ui.Spacer(width=20)
                            cb = ui.CheckBox(model=self.model.letterbox_enabled)
                            letterbox_group = ui.HStack(enabled=self.model.letterbox_enabled.as_bool)
                            callback = partial(self.on_group_check_changed, letterbox_group)
                            cb.model.add_value_changed_fn(callback)
                            with letterbox_group:
                                ui.Spacer(width=10)
                                ui.Label("Letterbox Ratio", alignment=ui.Alignment.TOP)
                                ui.Spacer(width=5)
                                ui.FloatDrag(self.model.letterbox_ratio, width=35, min=0.001, step=0.01)
        self.reticle_menu.show_at(x - self.reticle_menu.width, y - self.reticle_menu.height)
