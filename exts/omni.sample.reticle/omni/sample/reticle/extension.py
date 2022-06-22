import carb
import omni.ext
from omni.kit.viewport.utility import get_active_viewport_window

from . import constants
from .models import ReticleModel
from .views import ReticleOverlay


class SampleViewportReticleExtension(omni.ext.IExt):

    def on_startup(self, ext_id):
        print("[omni.sample.reticle] SampleViewportReticleExtension startup")

        # Reticle should ideally be used with "Fill Viewport" turned off.
        settings = carb.settings.get_settings()
        settings.set(constants.SETTING_RESOLUTION_FILL, False)

        viewport_window = get_active_viewport_window()
        if viewport_window is not None:
            reticle_model = ReticleModel()
            self.reticle = ReticleOverlay(reticle_model, viewport_window)
            self.reticle.build_viewport_overlay()

    def on_shutdown(self):
        """ Executed when the extension is disabled."""
        print("[omni.sample.reticle] SampleViewportReticleExtension shutdown")
        self.reticle.destroy()
