# DogPet

DogPet is a cross-platform desktop pet built with Tauri and Vue. It uses image-frame animations so users can bring their own pet artwork into a transparent, always-on-top desktop companion.

## Download

Download the latest installer from [GitHub Releases](https://github.com/yangpane/DogPet/releases).

- macOS Apple Silicon: download the `aarch64.dmg` asset.
- macOS Intel: download the `x64.dmg` asset.
- Windows 10/11 64-bit: download the `x64-setup.exe` or NSIS installer asset.

DogPet v1 is distributed through GitHub Releases. The app can check for updates from the DogPet release updater manifest.

## Features

- Transparent desktop pet window for macOS and Windows.
- Built-in default dog frame pack, so first launch does not require extra assets.
- Image-frame state machine for idle, typing, dragging, click, sleep, and random actions.
- User-uploaded image frame packs for custom pets.
- Keyboard and mouse activity detection for responsive pet behavior.

## Installation Notes

DogPet v1 reserves signing and notarization configuration but may be distributed unsigned during early testing.

- macOS may show an unidentified developer warning. Open System Settings -> Privacy & Security and allow DogPet if needed.
- Windows may show Microsoft Defender SmartScreen. Choose "More info" and "Run anyway" only if you downloaded DogPet from the official release page.
- On macOS, DogPet needs Input Monitoring permission to react to global keyboard and mouse input.

## Development

```bash
pnpm install
pnpm dev
pnpm tauri dev
```

Build the desktop app locally:

```bash
pnpm build:vite
pnpm tauri build
```

## Release

Create a tag such as `v1.1.0` or run the `DogPet Release` GitHub Actions workflow manually. The workflow builds:

- macOS Apple Silicon DMG
- macOS Intel DMG
- Windows x64 NSIS installer
- Tauri updater artifacts

Required repository secrets for updater artifacts:

- `TAURI_SIGNING_PRIVATE_KEY`
- `TAURI_SIGNING_PRIVATE_KEY_PASSWORD`

Reserved optional secrets for future formal signing:

- macOS: `APPLE_CERTIFICATE`, `APPLE_CERTIFICATE_PASSWORD`, `APPLE_SIGNING_IDENTITY`, `APPLE_ID`, `APPLE_PASSWORD`, `APPLE_TEAM_ID`
- Windows: `WINDOWS_CERTIFICATE`, `WINDOWS_CERTIFICATE_PASSWORD`

## Privacy

DogPet runs locally. Uploaded pet assets are stored in the app data directory on the user's machine.
