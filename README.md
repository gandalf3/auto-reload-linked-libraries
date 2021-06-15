# Auto Reload Linked Libraries

A simple Blender addon which auto-reloads linked library .blend files when it detects that they have been modified.

## Installation

1. Download the latest `.zip` from [the releases page](https://github.com/gandalf3/auto-reload-linked-libraries/releases).
2. In Blender's User Preferences > Addons, click *Install*.
3. Navigate to the downloaded zip and select it.
4. Enable the addon.

## Usage

This addon doesn't have a UI. Once it's enabled, linked libraries should just refresh automatically.

## Dependencies

Uses [`watchdog`](https://github.com/gorakhargosh/watchdog/) to watch for file changes. This is automatically included in the release zip, so you only need to worry about this if you wish to run the unpackaged source code.
A script `make_zip.sh` is included which generates such a bundled `.zip` archive, though it isn't terribly robust.
