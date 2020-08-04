# Auto Reload Linked Libraries

A simple Blender addon which auto-reloads linked library .blend files when it detects that they have been modified.

## Installation

1. Download the latest `.zip` release.
2. In Blender's User Preferences > Addons, click *Install from file*.
3. Navigate to the downloaded zip, select it.
4. Enable the addon.

## Usage

This addon doesn't have a UI. Once it's enabled, linked libraries should just refresh automatically.

## Dependencies

Uses `watchdog` to watch for file changes. This is automatically included in the release zip, so you only need to worry about this if you wish to run the unpackaged source code.
