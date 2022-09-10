# Changelog
All notable changes to this project will be documented in this file.

## [Unreleased]

## [1.3.1] - 2022-09-09
### Changed
- Fixed on_window_changed callback for VP2

## [1.3.0] - 2022-09-09
### Changed
- Fixed bad use of viewport window frame for VP2
- Now using ViewportAPI.subscribe_to_view_change() to update reticle on resolution changes.

## [1.2.0] - 2022-06-24
### Changed
- Refactored to omni.example.reticle
- Updated preview.png
- Cleaned up READMEs

### Removed
- menu.png

## [1.1.0] - 2022-06-22
### Changed
- Refactored reticle.py to views.py
- Fixed bug where Viewport Docs was being treated as viewport.
- Moved Reticle button to bottom right of viewport to not overlap axes decorator.

### Removed
- All mutli-viewport logic.

## [1.0.0] - 2022-05-25
### Added
- Initial add of the Sample Viewport Reticle extension.