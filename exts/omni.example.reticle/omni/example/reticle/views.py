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

    def __init__(self, model: ReticleModel, vp_win):
        """ReticleOverlay constructor

        Args:
            model (ReticleModel): The reticle model
            vp_win (Window): The viewport window to build the overlay on.
        """
        self.model = model
        self.vp_win = vp_win
        # Rebuild the overlay whenever the viewport window changes
        self.vp_win.set_height_changed_fn(self.on_window_changed)
        self.vp_win.set_width_changed_fn(self.on_window_changed)
        settings = carb.settings.get_settings()
        self._viewport_subs = []
        self._viewport_subs.append(settings.subscribe_to_node_change_events(constants.SETTING_RESOLUTION_WIDTH,
                                                                            self.on_window_changed))
        self._viewport_subs.append(settings.subscribe_to_node_change_events(constants.SETTING_RESOLUTION_HEIGHT,
                                                                            self.on_window_changed))
        self._viewport_subs.append(settings.subscribe_to_node_change_events(constants.SETTING_RESOLUTION_FILL,
                                                                            self.on_window_changed))
        # Rebuild the overlay whenever the model changes
        self.model.add_reticle_changed_fn(self.build_viewport_overlay)
        ReticleOverlay._instances.append(self)
        resolution = self.vp_win.viewport_api.get_texture_resolution()
        self._aspect_ratio = resolution[0] / resolution[1]

    @classmethod
    def get_instances(cls):
        """Get all created instances of ReticleOverlay"""
        return cls._instances

    def destroy(self):
        settings = carb.settings.get_settings()
        for sub in self._viewport_subs:
            settings.unsubscribe_to_change_events(sub)
        self._viewport_subs = None
        self.scene_view.scene.clear()
        self.scene_view = None
        self.reticle_menu.destroy()
        self.reticle_menu = None
        self.vp_win.frame.clear()
        self.vp_win.destroy()
        self.vp_win = None

    def on_window_changed(self, *args):
        """Update aspect ratio and rebuild overlay when viewport window changes."""
        settings = carb.settings.get_settings()
        fill = settings.get(constants.SETTING_RESOLUTION_FILL)
        if fill:
            width = self.vp_win.frame.computed_width + 8
            height = self.vp_win.height
        else:
            width = settings.get(constants.SETTING_RESOLUTION_WIDTH)
            height = settings.get(constants.SETTING_RESOLUTION_HEIGHT)
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
            self.vp_win.frame.clear()
            with self.vp_win.frame:
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
        # TODO: Put thirds composition guidelines logic here
        pass

    def _build_quad(self):
        """Build the scene ui graphics for the Quad composition mode."""
        # TODO: Put quad composition guidelines logic here
        pass

    def _build_crosshair(self):
        """Build the scene ui graphics for the Crosshair composition mode."""
        # TODO: Put crosshair logic here
        pass

    def _build_safe_rect(self, percentage, color):
        """Build the scene ui graphics for the safe area rectangle

        Args:
            percentage (float): The 0-1 percentage the render target that the rectangle should fill.
            color: The color to draw the rectangle wireframe with.
        """
        # TODO: Put safe area rectangle logic here
        pass

    def _build_letterbox(self):
        """Build the scene ui graphics for the letterbox."""
        aspect_ratio = self.get_aspect_ratio()
        letterbox_color = cl.letterbox_default
        letterbox_ratio = self.model.letterbox_ratio.as_float
        
        # TODO: Put letterbox logic here
        pass

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
