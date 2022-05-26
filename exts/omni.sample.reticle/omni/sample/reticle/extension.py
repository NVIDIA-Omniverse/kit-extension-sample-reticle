import traceback

import omni.ext
import omni.ui as ui

from .models import ReticleModel
from .reticle import ReticleOverlay


class CleanupError(Exception):
    pass


class SampleViewportReticleExtension(omni.ext.IExt):

    def on_startup(self, ext_id):
        print("[omni.sample.reticle] SampleViewportReticleExtension startup")
        windows = ui.Workspace.get_windows()
        for window_handle in windows:
            if window_handle.title.startswith("Viewport"):
                window = ui.Window(window_handle.title)
                SampleViewportReticleExtension.create_new_reticle_overlay(window)
        # ui.Workspace.set_window_created_callback(SampleViewportReticleExtension.on_window_created)

    @staticmethod
    def create_new_reticle_overlay(vp_win):
        reticle_model = ReticleModel()
        reticle = ReticleOverlay(reticle_model, vp_win)
        reticle.build_viewport_overlay()

    @staticmethod
    def on_window_created(win_handle):
        """Add a new ReticleOverlay whenever a new viewport window is created.

        Args:
            win_handle (WindowHandle): The window that was created.
        """
        if win_handle.title.startswith("Viewport"):
            window = ui.Window(win_handle.title)
            SampleViewportReticleExtension.create_new_reticle_overlay(window)

    def on_shutdown(self):
        """ Executed when the extension is disabled.

        TODO:
            * Overlay widgets are not removed on shutdown and users can still click on
            the Reticle button and produce an error.
            * I think object references are still being held on for callbacks. I need make sure everything is destroyed.

        Raises:
            CleanupError: Error occurred trying to destroy ReticleOverlay instances.
        """
        print("[omni.sample.reticle] SampleViewportReticleExtension shutdown")
        exception_raised = False
        # Need to explicitly destroy the ViewportWidgets otherwise they'll stick around and consume
        for instance in ReticleOverlay.get_instances():
            try:
                instance.destroy()
            except Exception:
                traceback.print_exc()
                exception_raised = True

        if exception_raised:
            raise CleanupError("One more more exceptions were raised when trying to destroy ReticleOverlay instances.")
