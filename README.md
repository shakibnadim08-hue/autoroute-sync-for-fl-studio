# AutoRoute Sync for FL Studio

> **Original project created by Shakib Nadim.**

AutoRoute Sync for FL Studio is a lightweight Channel Rack and Mixer organization utility for FL Studio. It removes repetitive manual routing and color-matching steps when adding samples, instruments, and plugins to a project.

This is an independent third-party project. It is not affiliated with, endorsed by, or sponsored by Image-Line Software.

## What it does

When a new Channel Rack channel is created, the script automatically:

- assigns the channel a vivid, distinct color;
- finds a safe unused Mixer insert;
- routes the channel to that Mixer insert;
- copies the channel name to the Mixer insert; and
- copies the channel color to the Mixer insert.

The same behavior applies when a sample or instrument is dragged into the Playlist because FL Studio creates a Channel Rack channel for that content.

The script also watches automatically managed Mixer inserts. When a managed source channel is deleted, the script confirms that the insert is no longer being used, removes the effects loaded in that managed insert, and restores the insert’s previous name and color.

Automatic colors exclude red so they are not confused with FL Studio’s selection and attention states.

## How it works

FL Studio hosts the script through its MIDI Controller Scripting system. The script does not need a physical MIDI keyboard or controller. A free software-only virtual MIDI port is used so FL Studio can load the script.

After loading, the script monitors Channel Rack changes. For each new channel, it reads the channel’s name, color, and current Mixer routing, selects an available insert, and writes the matching routing and metadata. Before changing an insert, it remembers the insert’s previous name and color. When the managed channel disappears, the script waits for the deletion state to settle, verifies that no other channel is using that insert, removes the occupied effects from the owned Mixer insert using a verified track-and-slot focus sequence, and restores the saved appearance.

The script does not add effects, process audio, change plugin settings, create buses, or edit automation clips.

## Installation

See [INSTALLATION.md](INSTALLATION.md) for the complete Windows and macOS setup instructions. The setup uses a free virtual MIDI port, so physical MIDI hardware is not required.

## Requirements

- FL Studio with MIDI Controller Scripting support.
- Windows with [loopMIDI](https://www.tobias-erichsen.de/software/loopmidi.html), or macOS with the built-in IAC Driver.
- The included `device_AutoRouteSync.py` script.

## Usage

After installation, keep the virtual MIDI port active while FL Studio is running. Add a sample or instrument to the Channel Rack or Playlist and the script will organize its channel and Mixer insert automatically.

The script respects existing channel routing and avoids Mixer inserts that contain effects or existing inter-insert routing. Existing project channels are not retroactively changed when the script starts or a project is loaded.

## License and attribution

AutoRoute Sync for FL Studio is free to download, modify, and redistribute for non-commercial purposes under the included [LICENSE](LICENSE). Sale, paywall distribution, monetized redistribution, and use in a paid product or paid service are not permitted without written permission from Shakib Nadim.

Every redistributed copy must prominently display the following notice near the beginning of its README, repository page, download page, or first visible presentation area:

> **Original project created by Shakib Nadim.**

A modified project may use a custom name, but its name must begin with the exact original project name:

> **AutoRoute Sync for FL Studio — [Custom Name]**

The original project name may not be removed, hidden, replaced, or used only in a deeply nested credit file. Modified projects must clearly identify the modifier and must not be presented as unrelated software.

## Trademark notice

FL Studio is a trademark of Image-Line Software. AutoRoute Sync for FL Studio is an independent third-party utility and does not include Image-Line software, logos, or proprietary assets.

## Project files

| File | Description |
|---|---|
| `device_AutoRouteSync.py` | FL Studio MIDI Controller Script. |
| `INSTALLATION.md` | Setup instructions for Windows and macOS. |
| `LICENSE` | Project license and redistribution conditions. |
| `NOTICE.md` | Required attribution and modified-project notice. |
