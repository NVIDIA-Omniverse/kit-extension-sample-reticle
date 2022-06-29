# Viewport Reticle Kit Extension Sample 
![Camera Reticle Preview](exts/omni.example.reticle/data/preview.png)

The Viewport Reticle Sample extension adds a new menu button to all viewports. From this menu, users can enable and configure:
1. Composition Guidelines
2. Safe Area Guidelines
3. Letterbox

To have a clear design target, we designed the UI as a look-alike of the similar Unreal Engine Cinematic Viewport control. 
Even though this an example for learning how to create extensions using the omni.ui.scene API, feel free to use this 
extension to help compose your shots too.

## Adding This Extension

To add a this extension to your Omniverse app:
1. Go into: Extension Manager -> Gear Icon -> Extension Search Path
2. Add this as a search path: `git://github.com/NVIDIA-Omniverse/kit-extension-sample-reticle?branch=main&dir=exts`