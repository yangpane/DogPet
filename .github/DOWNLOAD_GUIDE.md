# DogPet Download Guide

## System Requirements

- macOS 12 or later.
- Windows 10 or later, 64-bit.

Linux packaging may remain available from the underlying Tauri configuration, but DogPet v1 focuses on macOS and Windows.

## macOS

- Apple Silicon: download the `DogPet_*_aarch64.dmg` asset from GitHub Releases.
- Intel: download the `DogPet_*_x64.dmg` asset from GitHub Releases.

If macOS blocks the app because it is not notarized yet:

1. Open System Settings.
2. Go to Privacy & Security.
3. Find the DogPet warning and choose Open Anyway.
4. Grant Input Monitoring permission when prompted so DogPet can react to keyboard and mouse activity.

## Windows

- 64-bit users should download the `DogPet_*_x64-setup.exe` or NSIS installer asset.

If Microsoft Defender SmartScreen appears, choose More info -> Run anyway only when the installer came from the official DogPet release page.

## Updates

DogPet checks for updates from:

```text
https://github.com/yangpane/DogPet/releases/latest/download/latest.json
```

Updater artifacts require the Tauri updater signing secrets configured in the GitHub repository.
