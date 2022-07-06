# Viewport Reticle Kit Extension Sample 

## [Viewport Reticle (omni.example.reticle)](exts/omni.example.reticle)
![Camera Reticle Preview](exts/omni.example.reticle/data/preview.png)

### About
This extension shows how to build a viewport reticle extension. The focus of this sample extension is to show how to use omni.ui.scene to draw additional graphical primitives on the viewport.

### [README](exts/omni.example.reticle)
See the [README for this extension](exts/omni.example.reticle) to learn more about it including how to use it.

### [Tutorial](tutorial/tutorial.md)
Follow a [step-by-step tutorial](tutorial/tutorial.md) that walks you through how to use omni.ui.scene to build this extension.

## Adding This Extension

To add this extension to your Omniverse app:
1. Go into: Extension Manager -> Gear Icon -> Extension Search Path
2. Add this as a search path: `git://github.com/NVIDIA-Omniverse/kit-extension-sample-reticle?branch=main&dir=exts`


## Linking with an Omniverse app

For a better developer experience, it is recommended to create a folder link named `app` to the *Omniverse Kit* app installed from *Omniverse Launcher*. A convenience script to use is included.

Run:

```bash
> link_app.bat
```

There is also an analogous `link_app.sh` for Linux. If successful you should see `app` folder link in the root of this repo.

If multiple Omniverse apps is installed script will select recommended one. Or you can explicitly pass an app:

```bash
> link_app.bat --app code
```

You can also just pass a path to create link to:

```bash
> link_app.bat --path "C:/Users/bob/AppData/Local/ov/pkg/create-2022.1.3"
```

## Contributing
The source code for this repository is provided as-is and we are not accepting outside contributions.