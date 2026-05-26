from pathlib import Path

from PIL import Image


ROOT = Path(__file__).resolve().parents[1]
SOURCE_ROOT = ROOT / "public" / "pet-preview"
PADDING = 12
TARGET_SIZE = (320, 374)
TARGET_SUBJECT_HEIGHT = 320
TARGET_SUBJECT_WIDTH = 296
TARGET_GROUND_Y = 362

STATE_DIRS = [
    "idle-clean",
    "typing-intro-clean",
    "typing-loop-clean",
    "typing-outro-clean",
    "click-clean",
    "drag-enter-clean",
    "drag-loop-clean",
    "drag-exit-clean",
    "sleep-clean",
    "random-clean",
]


def object_bbox(image):
    return image.getchannel("A").point(lambda value: 255 if value > 8 else 0).getbbox()


def union_bbox(frames):
    boxes = [object_bbox(frame) for frame in frames]
    boxes = [box for box in boxes if box]
    if not boxes:
        return None

    left = min(box[0] for box in boxes)
    top = min(box[1] for box in boxes)
    right = max(box[2] for box in boxes)
    bottom = max(box[3] for box in boxes)
    width, height = frames[0].size

    return (
        max(0, left - PADDING),
        max(0, top - PADDING),
        min(width, right + PADDING),
        min(height, bottom + PADDING),
    )


def resize_to_fit(subject):
    width, height = subject.size
    scale = min(TARGET_SUBJECT_WIDTH / width, TARGET_SUBJECT_HEIGHT / height, 1)

    return subject.resize((round(width * scale), round(height * scale)), Image.Resampling.LANCZOS)


def state_ground_y(state_dir, source_bbox):
    if state_dir.startswith("drag-"):
        source_bottom = source_bbox[3]

        return TARGET_GROUND_Y - round(max(0, 460 - source_bottom) * 0.8)

    return TARGET_GROUND_Y


def normalize_frame(frame, state_dir):
    bbox = object_bbox(frame)
    if not bbox:
        return Image.new("RGBA", TARGET_SIZE, (0, 0, 0, 0))

    subject = resize_to_fit(frame.crop(bbox))
    target = Image.new("RGBA", TARGET_SIZE, (0, 0, 0, 0))
    x = round((TARGET_SIZE[0] - subject.width) / 2)
    y = state_ground_y(state_dir, bbox) - subject.height
    y = max(0, min(TARGET_SIZE[1] - subject.height, y))
    target.alpha_composite(subject, (x, y))

    return target


def write_preview_gif(frames, target):
    if not frames:
        return

    frames[0].save(
        target,
        save_all=True,
        append_images=frames[1:],
        duration=110,
        loop=0,
        disposal=2,
    )


def crop_state(state_dir):
    source_dir = SOURCE_ROOT / state_dir
    sources = sorted(source_dir.glob("*.png"))
    if not sources:
        return

    frames = [normalize_frame(Image.open(source).convert("RGBA"), state_dir) for source in sources]

    target_name = state_dir.replace("-clean", "-hit")
    targets = [
        SOURCE_ROOT / target_name,
        ROOT / "pet-assets" / target_name,
    ]

    for target_dir in targets:
        target_dir.mkdir(parents=True, exist_ok=True)
        for old_file in target_dir.glob("*.png"):
            old_file.unlink()

        for index, frame in enumerate(frames, start=1):
            frame.save(target_dir / f"{index:03}.png")

    write_preview_gif(frames, SOURCE_ROOT / f"{target_name}-preview.gif")
    write_preview_gif(frames, ROOT / "pet-assets" / f"{target_name}-preview.gif")

    print(f"{state_dir} -> {target_name}: size={frames[0].size}")


def main():
    for state_dir in STATE_DIRS:
        crop_state(state_dir)


if __name__ == "__main__":
    main()
