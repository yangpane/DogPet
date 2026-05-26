# DogPet Release Checklist

DogPet is distributed with GitHub Releases and Tauri updater artifacts.

## GitHub Repository

Create a public repository:

```bash
gh repo create yangpane/DogPet --public --source=. --remote=origin --push
```

If the repository already exists, add or update the remote instead:

```bash
git remote set-url origin git@github.com:yangpane/DogPet.git
git push -u origin main
```

## Required Secrets

The updater key pair for this workspace was generated with:

```bash
pnpm tauri signer generate --ci --write-keys /private/tmp/dogpet-updater.key --force
```

Set this repository secret from the private key file contents:

- `TAURI_SIGNING_PRIVATE_KEY`: contents of `/private/tmp/dogpet-updater.key`

This key has no password, so `TAURI_SIGNING_PRIVATE_KEY_PASSWORD` may be omitted for v1. If you generate a password-protected key later, update both the secret and `src-tauri/tauri.conf.json` `plugins.updater.pubkey`.

## Optional Future Signing Secrets

These are reserved in the release workflow but not required for the unsigned v1 installer flow:

- macOS: `APPLE_CERTIFICATE`, `APPLE_CERTIFICATE_PASSWORD`, `APPLE_SIGNING_IDENTITY`, `APPLE_ID`, `APPLE_PASSWORD`, `APPLE_TEAM_ID`
- Windows: `WINDOWS_CERTIFICATE`, `WINDOWS_CERTIFICATE_PASSWORD`

## Release Flow

1. Update `package.json` and `src-tauri/Cargo.toml` versions together.
2. Commit all changes.
3. Create and push a tag:

```bash
git tag v1.1.0
git push origin v1.1.0
```

4. Wait for the `DogPet Release` workflow.
5. Inspect the draft release assets.
6. Publish the draft release manually.

Expected v1 assets:

- macOS Apple Silicon DMG
- macOS Intel DMG
- Windows x64 NSIS installer
- `latest.json` and updater signatures

## Install Caveats

DogPet v1 may be unsigned:

- macOS users may need to allow the app in System Settings -> Privacy & Security.
- Windows users may see SmartScreen and need to choose More info -> Run anyway.
