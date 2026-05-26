# DogPet Maintenance Pack

This folder records the DogPet MVP work so the project can be resumed without digging through chat history.

## Source Project

- Product repo: `DogPet`
- Original upstream: `ayangweb/BongoCat`
- Local maintenance folder: `~/Desktop/Pet`

## Current Product Direction

Build a custom image-frame desktop pet. The MVP replaces the original Live2D-first experience with a frame animation renderer. Users provide pet images for fixed states, and the desktop pet switches states based on keyboard, mouse, idle, wake, drag, and random events.

The current app ships with a built-in dog frame pack, so first launch no longer depends on local desktop assets.

## Fixed MVP States

- `idle`: no operation
- `typing`: keyboard input
- `click`: mouse click one-shot animation
- `mouse`: drag loop slot for the current MVP
- `sleep`: long inactivity
- `random`: occasional idle action

## Included Assets

- `public/pet-preview/idle-hit/001.png`: built-in idle frame
- `public/pet-preview/typing-intro-hit/001.png` to `003.png`: typing enter
- `public/pet-preview/typing-loop-hit/001.png` to `006.png`: typing loop
- `public/pet-preview/typing-outro-hit/001.png` to `003.png`: typing exit
- `public/pet-preview/drag-enter-hit/001.png` to `003.png`: drag enter
- `public/pet-preview/drag-loop-hit/001.png` to `006.png`: drag loop
- `public/pet-preview/drag-exit-hit/001.png` to `003.png`: drag exit
- `public/pet-preview/click-hit`, `sleep-hit`, and `random-hit`: remaining bundled frame states

## Quick Run

From the source project:

```bash
corepack pnpm tauri dev
```

If the desktop app is already running, the debug process is usually:

```text
target/debug/dogpet
```

The frontend dev server usually runs at:

```text
http://127.0.0.1:1420
```

## Verification Commands

```bash
corepack pnpm exec tsc --noEmit
corepack pnpm build:vite
TAURI_SIGNING_PRIVATE_KEY="$(cat /private/tmp/dogpet-updater.key)" TAURI_SIGNING_PRIVATE_KEY_PASSWORD="" corepack pnpm tauri build
```
