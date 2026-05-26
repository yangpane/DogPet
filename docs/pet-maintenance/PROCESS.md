# Process Notes

## Conversation Decisions

1. The project is based on `ayangweb/BongoCat` and is being repackaged as `DogPet`.
2. The product direction is a desktop pet that can use user-provided assets, such as a dog image sequence.
3. The first MVP should stay simple:
   - Use image frames, not video.
   - Do not implement dialogue yet.
   - Do not implement water or long-sitting reminders yet.
   - Do not keep Live2D as the main experience for MVP.
4. The MVP uses six fixed states:
   - `idle` as the base quiet/standing-by loop
   - `typing`
   - `click`
   - `mouse`
   - `sleep`
   - `random` as an occasional one-shot idle action
5. The public app now ships a complete built-in dog frame pack rather than requiring first-launch local assets.
6. The user provided dog sprite sheets for idle, typing, click, sleep, random, and drag states.
7. Runtime assets are cleaned transparent PNG sequences under `public/pet-preview`.
8. The state rules now treat visual priority and behavior tracking separately:
   - Pet click is the highest-priority one-shot visual state.
   - Global mouse clicks outside the pet count as mouse activity, not pet click.
   - Keyboard activity is remembered while click is playing, so click finishes into typing when appropriate.
   - Random is an interruptible idle insert action, not the base idle loop.
   - Random can only trigger from idle, has cooldown/probability gating, and does not trigger from sleep/typing/mouse/click.
   - Sleep starts after 5 minutes without keyboard or mouse activity.
9. The current typing experience uses a 12-frame, 4 x 3 source sheet:
   - Frames 1-3 are the typing intro animation, played slower than the loop so picking up the keyboard is visible.
   - Frames 4-9 are the typing loop while keyboard input continues.
   - Frames 10-12 are the typing outro animation after keyboard input stops.
   - Keyboard idle detection is tuned to 650 ms so the outro starts quickly after typing stops.
10. The current idle experience uses a single 1 x 1 sitting dog frame.
11. The idle frame is scaled to match the typing subject height, avoiding a large size jump between idle and typing.

## Implementation Summary

Added image-frame pet infrastructure:

- `src/pet-frame/states.ts`
- `src/pet-frame/machine.ts`
- `src/stores/petFrame.ts`

Updated main desktop rendering:

- `src/pages/main/index.vue`

Updated preferences:

- `src/pages/preference/index.vue`
- `src/pages/preference/components/pet-frame/index.vue`

Added browser/static preview helpers:

- `src/pages/browser-preview/index.vue`
- `public/preview.html`
- `public/pet-preview/`

Updated app/router browser guards:

- `src/App.vue`
- `src/router/index.ts`

Generated and bundled frame assets:

- `public/pet-preview/idle-hit`
- `public/pet-preview/typing-intro-hit`, `typing-loop-hit`, `typing-outro-hit`
- `public/pet-preview/drag-enter-hit`, `drag-loop-hit`, `drag-exit-hit`
- `public/pet-preview/click-hit`, `sleep-hit`, `random-hit`

## Current Runtime Status When Last Checked

- DogPet identity, release workflow, updater endpoint, and release documentation are configured.
- macOS local Tauri packaging has produced `DogPet.app`, `DogPet_1.1.0_aarch64.dmg`, and updater signature artifacts.
