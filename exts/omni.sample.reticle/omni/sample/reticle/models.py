"""Models used by the CameraReticleExtension"""
import omni.ui as ui

from . import constants


class ReticleModel:
    """Model containing all of the data used by the ReticleOverlay and ReticleMenu

    The ReticleOverlay and ReticleMenu classes need to share the same data and stay
    in sync with updates from user input. This is achieve by passing the same
    ReticleModel object to both classes.
    """
    def __init__(self):
        self.composition_mode = ui.SimpleIntModel(constants.DEFAULT_COMPOSITION_MODE)
        self.action_safe_enabled = ui.SimpleBoolModel(False)
        self.action_safe_percentage = ui.SimpleFloatModel(constants.DEFAULT_ACTION_SAFE_PERCENTAGE, min=0, max=100)
        self.title_safe_enabled = ui.SimpleBoolModel(False)
        self.title_safe_percentage = ui.SimpleFloatModel(constants.DEFAULT_TITLE_SAFE_PERCENTAGE, min=0, max=100)
        self.custom_safe_enabled = ui.SimpleBoolModel(False)
        self.custom_safe_percentage = ui.SimpleFloatModel(constants.DEFAULT_CUSTOM_SAFE_PERCENTAGE, min=0, max=100)
        self.letterbox_enabled = ui.SimpleBoolModel(False)
        self.letterbox_ratio = ui.SimpleFloatModel(constants.DEFAULT_LETTERBOX_RATIO, min=0.001)

        self._register_submodel_callbacks()

        self._callbacks = []

    def _register_submodel_callbacks(self):
        """Register to listen to when any submodel values change."""
        self.composition_mode.add_value_changed_fn(self._reticle_changed)
        self.action_safe_enabled.add_value_changed_fn(self._reticle_changed)
        self.action_safe_percentage.add_value_changed_fn(self._reticle_changed)
        self.title_safe_enabled.add_value_changed_fn(self._reticle_changed)
        self.title_safe_percentage.add_value_changed_fn(self._reticle_changed)
        self.custom_safe_enabled.add_value_changed_fn(self._reticle_changed)
        self.custom_safe_percentage.add_value_changed_fn(self._reticle_changed)
        self.letterbox_enabled.add_value_changed_fn(self._reticle_changed)
        self.letterbox_ratio.add_value_changed_fn(self._reticle_changed)

    def _reticle_changed(self, model):
        """Executes all registered callbacks of this model.

        Args:
            model (Any): The submodel that has changed. [Unused]
        """
        for callback in self._callbacks:
            callback()

    def add_reticle_changed_fn(self, callback):
        """Add a callback to be executed whenever any ReticleModel submodel data changes.

        This is useful for rebuilding the overlay whenever any data changes.

        Args:
            callback (function): The function to call when the reticle model changes.
        """
        self._callbacks.append(callback)
