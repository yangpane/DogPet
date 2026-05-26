# Pet Asset Spec

## MVP Package Shape

```json
{
  "name": "My Pet",
  "version": 1,
  "states": {
    "idle": { "id": "idle", "frames": [], "fps": 8, "loop": true },
    "typing": { "id": "typing", "frames": [], "fps": 10, "loop": true },
    "click": { "id": "click", "frames": [], "fps": 12, "loop": false },
    "mouse": { "id": "mouse", "frames": [], "fps": 10, "loop": true },
    "sleep": { "id": "sleep", "frames": [], "fps": 6, "loop": true },
    "random": { "id": "random", "frames": [], "fps": 10, "loop": false }
  }
}
```

## Accepted Frame Formats

- `.png`
- `.jpg`
- `.jpeg`
- `.webp`

## Naming

Frames should be named in playback order:

```text
001.png
002.png
003.png
...
```

The app sorts uploaded frames by file name.

## Recommended Frame Guidelines

- Use the same canvas size for every frame in the same state.
- Keep the pet centered in the same approximate position.
- Recommended first test size: square frames around `444 x 444` or `512 x 512`.
- Transparent PNG is the preferred runtime format.
- For sprite sheets, keep every cell the same size and lay frames left-to-right, top-to-bottom.
- Current cleanup output uses a `512 x 512` transparent canvas and keeps the pet's bottom aligned to the same baseline to avoid animation jitter.

## Current Typing Asset

The provided sprite sheet was cropped, background-cleaned, and aligned into 8 square frames:

```text
pet-assets/typing-clean/001.png
pet-assets/typing-clean/002.png
pet-assets/typing-clean/003.png
pet-assets/typing-clean/004.png
pet-assets/typing-clean/005.png
pet-assets/typing-clean/006.png
pet-assets/typing-clean/007.png
pet-assets/typing-clean/008.png
```

## Sprite Cleanup Command

```bash
python3 scripts/processTypingSprite.py \
  --source ~/Desktop/Pet/assets/original/小狗打字.png \
  --state typing-clean \
  --cols 4 \
  --rows 2
```

For the idle sheet, save the source image as:

```text
~/Desktop/Pet/assets/original/小狗待机.png
```

Then run the same cleanup script with `--state idle-clean --cols 3 --rows 2`.

## Current Idle Asset

The provided idle sprite sheet was cropped, background-cleaned, and aligned into 6 square frames:

```text
pet-assets/idle-clean/001.png
pet-assets/idle-clean/002.png
pet-assets/idle-clean/003.png
pet-assets/idle-clean/004.png
pet-assets/idle-clean/005.png
pet-assets/idle-clean/006.png
```

Cleanup command:

```bash
python3 scripts/processTypingSprite.py \
  --source ~/Desktop/Pet/assets/original/小狗待机.png \
  --state idle-clean \
  --cols 3 \
  --rows 2 \
  --ground-y 462 \
  --padding-x 54
```

## Current Full Demo Asset Set

All six states now use cleaned transparent PNG frame sequences:

```text
pet-assets/idle-clean/001.png   ... 001.png  # 1 x 1, fps 8, loop
pet-assets/typing-intro-clean/001.png ... 003.png  # 4 x 3 frames 1-3, typing enter
pet-assets/typing-loop-clean/001.png  ... 006.png  # 4 x 3 frames 4-9, fps 10, loop while typing
pet-assets/typing-outro-clean/001.png ... 003.png  # 4 x 3 frames 10-12, typing exit
pet-assets/typing-clean/001.png ... 008.png  # 4 x 2, previous comparison set
pet-assets/typing-pixel-clean/001.png ... 008.png  # 4 x 2, comparison set, currently not active
pet-assets/click-clean/001.png  ... 004.png  # 2 x 2, fps 12, one-shot
pet-assets/mouse-clean/001.png  ... 006.png  # 3 x 2, fps 10, loop
pet-assets/sleep-clean/001.png  ... 006.png  # 3 x 2, fps 6, loop
pet-assets/random-clean/001.png ... 009.png  # 3 x 3, fps 10, one-shot idle insert
```

Source files live in:

```text
~/Desktop/Pet/assets/original/
```

Cleaned copies are mirrored to:

```text
~/Desktop/Pet/assets/
```
