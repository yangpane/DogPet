import argparse
import math
from collections import deque
from pathlib import Path

from PIL import Image, ImageFilter


ROOT = Path(__file__).resolve().parents[1]
CANVAS = 512
TARGET_SUBJECT_HEIGHT = 320
DRAG_BOTTOMS = [
    460,
    445,
    430,
    430,
    426,
    428,
    432,
    430,
    426,
    430,
    445,
    460,
]


def is_background(pixel):
    r, g, b = pixel[:3]
    high = max(r, g, b)
    low = min(r, g, b)

    return high >= 188 and low >= 176 and high - low <= 52


def edge_background_mask(image):
    width, height = image.size
    source = image.convert("RGB")
    seen = bytearray(width * height)
    mask = bytearray(width * height)
    queue = deque()

    def push(x, y):
        if x < 0 or y < 0 or x >= width or y >= height:
            return

        idx = y * width + x
        if seen[idx]:
            return

        seen[idx] = 1
        if is_background(source.getpixel((x, y))):
            mask[idx] = 1
            queue.append((x, y))

    for x in range(width):
        push(x, 0)
        push(x, height - 1)

    for y in range(height):
        push(0, y)
        push(width - 1, y)

    while queue:
        x, y = queue.popleft()
        push(x + 1, y)
        push(x - 1, y)
        push(x, y + 1)
        push(x, y - 1)

    return Image.frombytes("L", (width, height), bytes(0 if value else 255 for value in mask))


def crop_sprite_sheet(source, cols, rows):
    sheet = Image.open(source).convert("RGBA")
    width, height = sheet.size
    frames = []

    for row in range(rows):
        for col in range(cols):
            left = round(width * col / cols)
            right = round(width * (col + 1) / cols)
            top = round(height * row / rows)
            bottom = round(height * (row + 1) / rows)
            frames.append(sheet.crop((left, top, right, bottom)))

    return frames


def remove_background(frame):
    alpha = edge_background_mask(frame)
    alpha = alpha.filter(ImageFilter.MaxFilter(3))
    alpha = alpha.filter(ImageFilter.GaussianBlur(0.65))

    clean = frame.copy()
    clean.putalpha(alpha)

    return clean


def object_bbox(frame):
    return frame.getchannel("A").point(lambda value: 255 if value > 8 else 0).getbbox()


def normalize_frame(frame, index):
    frame = frame.resize((CANVAS, CANVAS), Image.Resampling.LANCZOS)
    bbox = object_bbox(frame)
    if not bbox:
        return frame

    left, top, right, bottom = bbox
    subject = frame.crop(bbox)
    width = right - left
    height = bottom - top
    scale = min(1, TARGET_SUBJECT_HEIGHT / height)
    next_size = (round(width * scale), round(height * scale))
    subject = subject.resize(next_size, Image.Resampling.LANCZOS)

    source_center_x = (left + right) / 2
    center_x = round(CANVAS / 2 + (source_center_x - CANVAS / 2) * 0.35)
    target_bottom = DRAG_BOTTOMS[index]

    canvas = Image.new("RGBA", (CANVAS, CANVAS), (0, 0, 0, 0))
    canvas.alpha_composite(subject, (round(center_x - next_size[0] / 2), target_bottom - next_size[1]))

    return canvas


def write_frames(frames, state, root=ROOT):
    targets = [
        root / "pet-assets" / state,
        root / "public" / "pet-preview" / state,
    ]

    for target in targets:
        target.mkdir(parents=True, exist_ok=True)
        for old_file in target.glob("*.png"):
            old_file.unlink()

        for index, frame in enumerate(frames, start=1):
            frame.save(target / f"{index:03}.png")


def write_preview_gif(frames, target, duration=110):
    if not frames:
        return

    target.parent.mkdir(parents=True, exist_ok=True)
    frames[0].save(
        target,
        save_all=True,
        append_images=frames[1:],
        duration=duration,
        loop=0,
        disposal=2,
    )


def write_sheet(frames, target):
    sheet = Image.new("RGBA", (CANVAS * 4, CANVAS * 3), (0, 0, 0, 0))

    for index, frame in enumerate(frames):
        col = index % 4
        row = math.floor(index / 4)
        sheet.alpha_composite(frame, (col * CANVAS, row * CANVAS))

    target.parent.mkdir(parents=True, exist_ok=True)
    sheet.save(target)


def write_contact_sheet(frames, target):
    cell = 256
    checker = Image.new("RGBA", (cell * 4, cell * 3), (245, 245, 245, 255))

    for y in range(0, checker.height, 32):
        for x in range(0, checker.width, 32):
            if (x // 32 + y // 32) % 2:
                checker.paste((228, 228, 228, 255), (x, y, x + 32, y + 32))

    for index, frame in enumerate(frames):
        col = index % 4
        row = math.floor(index / 4)
        thumbnail = frame.resize((cell, cell), Image.Resampling.LANCZOS)
        checker.alpha_composite(thumbnail, (col * cell, row * cell))

    target.parent.mkdir(parents=True, exist_ok=True)
    checker.convert("RGB").save(target)


def sync_pet_folder(files, pet_assets: Path | None):
    if not pet_assets:
        return

    segments = {
        "drag-enter-clean": files[:3],
        "drag-loop-clean": files[3:9],
        "drag-exit-clean": files[9:],
    }

    for state, frames in segments.items():
        target = pet_assets / state
        target.mkdir(parents=True, exist_ok=True)
        for old_file in target.glob("*.png"):
            old_file.unlink()
        for index, frame in enumerate(frames, start=1):
            frame.save(target / f"{index:03}.png")


def parse_args():
    parser = argparse.ArgumentParser(description="Process the 4x3 drag sprite while preserving per-cell motion layout.")
    parser.add_argument("--source", required=True)
    parser.add_argument("--pet-assets-dir")

    return parser.parse_args()


def main():
    args = parse_args()
    source = Path(args.source).expanduser()
    frames = [
        normalize_frame(remove_background(frame), index)
        for index, frame in enumerate(crop_sprite_sheet(source, 4, 3))
    ]

    write_frames(frames[:3], "drag-enter-clean")
    write_frames(frames[3:9], "drag-loop-clean")
    write_frames(frames[9:], "drag-exit-clean")
    write_frames(frames, "drag-sequence-clean")
    write_sheet(frames, ROOT / "pet-assets" / "drag-state-4x3.png")
    write_contact_sheet(frames, ROOT / "pet-assets" / "drag-state-4x3-contact.jpg")

    write_preview_gif(frames[:3], ROOT / "public" / "pet-preview" / "drag-enter-clean-preview.gif")
    write_preview_gif(frames[3:9], ROOT / "public" / "pet-preview" / "drag-loop-clean-preview.gif")
    write_preview_gif(frames[9:], ROOT / "public" / "pet-preview" / "drag-exit-clean-preview.gif")
    write_preview_gif(frames, ROOT / "public" / "pet-preview" / "drag-sequence-clean-preview.gif")

    pet_assets = Path(args.pet_assets_dir).expanduser() if args.pet_assets_dir else None
    sync_pet_folder(frames, pet_assets)

    if pet_assets:
        write_preview_gif(frames[:3], pet_assets / "drag-enter-clean-preview.gif")
        write_preview_gif(frames[3:9], pet_assets / "drag-loop-clean-preview.gif")
        write_preview_gif(frames[9:], pet_assets / "drag-exit-clean-preview.gif")
        write_preview_gif(frames, pet_assets / "drag-sequence-clean-preview.gif")

    print("Wrote drag enter/loop/exit frames from updated 4x3 sprite")


if __name__ == "__main__":
    main()
