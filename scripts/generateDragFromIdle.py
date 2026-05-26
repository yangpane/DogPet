import argparse
import math
from pathlib import Path

from PIL import Image


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_SOURCE = ROOT / "public" / "pet-preview" / "idle-clean" / "001.png"
CANVAS = 512
SHEET_CELL = 256


def object_bbox(image: Image.Image):
    return image.getchannel("A").point(lambda value: 255 if value > 8 else 0).getbbox()


def transform_subject(subject: Image.Image, scale: float, angle: float) -> Image.Image:
    width, height = subject.size
    resized = subject.resize((round(width * scale), round(height * scale)), Image.Resampling.LANCZOS)

    return resized.rotate(angle, resample=Image.Resampling.BICUBIC, expand=True)


def compose_frame(subject: Image.Image, scale: float, angle: float, center_x: int, bottom_y: int) -> Image.Image:
    transformed = transform_subject(subject, scale, angle)
    frame = Image.new("RGBA", (CANVAS, CANVAS), (0, 0, 0, 0))
    x = round(center_x - transformed.width / 2)
    y = round(bottom_y - transformed.height)
    frame.alpha_composite(transformed, (x, y))

    return frame


def make_frames(source: Path):
    idle = Image.open(source).convert("RGBA")
    bbox = object_bbox(idle)
    if not bbox:
        raise ValueError(f"No visible subject found in {source}")

    subject = idle.crop(bbox)

    # Conservative by design: preserve the exact mother-frame dog art while
    # adding lift, sway, and return motion for the first drag experiment.
    specs = [
        # drag_enter
        (0.61, 0, 256, 460),
        (0.59, -3, 256, 430),
        (0.57, 2, 256, 396),
        # drag_loop
        (0.55, -7, 246, 374),
        (0.55, -3, 252, 364),
        (0.55, 4, 264, 368),
        (0.55, 7, 270, 378),
        (0.55, 2, 260, 386),
        (0.55, -5, 250, 378),
        # drag_exit
        (0.57, 3, 260, 404),
        (0.59, -2, 256, 434),
        (0.61, 0, 256, 460),
    ]

    return [compose_frame(subject, scale, angle, center_x, bottom_y) for scale, angle, center_x, bottom_y in specs]


def save_frames(frames: list[Image.Image], state: str, start: int = 1):
    targets = [
        ROOT / "pet-assets" / state,
        ROOT / "public" / "pet-preview" / state,
    ]

    for target in targets:
        target.mkdir(parents=True, exist_ok=True)
        for old_file in target.glob("*.png"):
            old_file.unlink()

        for offset, frame in enumerate(frames, start=start):
            frame.save(target / f"{offset:03}.png")


def save_preview(frames: list[Image.Image], target: Path, duration: int = 110):
    target.parent.mkdir(parents=True, exist_ok=True)
    frames[0].save(
        target,
        save_all=True,
        append_images=frames[1:],
        duration=duration,
        loop=0,
        disposal=2,
    )


def save_sheet(frames: list[Image.Image], target: Path):
    sheet = Image.new("RGBA", (SHEET_CELL * 4, SHEET_CELL * 3), (0, 0, 0, 0))

    for index, frame in enumerate(frames):
        col = index % 4
        row = math.floor(index / 4)
        thumbnail = frame.resize((SHEET_CELL, SHEET_CELL), Image.Resampling.LANCZOS)
        sheet.alpha_composite(thumbnail, (col * SHEET_CELL, row * SHEET_CELL))

    target.parent.mkdir(parents=True, exist_ok=True)
    sheet.save(target)


def save_contact_sheet(frames: list[Image.Image], target: Path):
    checker = Image.new("RGBA", (SHEET_CELL * 4, SHEET_CELL * 3), (245, 245, 245, 255))

    for y in range(0, checker.height, 32):
        for x in range(0, checker.width, 32):
            if (x // 32 + y // 32) % 2:
                checker.paste((228, 228, 228, 255), (x, y, x + 32, y + 32))

    for index, frame in enumerate(frames):
        col = index % 4
        row = math.floor(index / 4)
        thumbnail = frame.resize((SHEET_CELL, SHEET_CELL), Image.Resampling.LANCZOS)
        checker.alpha_composite(thumbnail, (col * SHEET_CELL, row * SHEET_CELL))

    target.parent.mkdir(parents=True, exist_ok=True)
    checker.convert("RGB").save(target)


def parse_args():
    parser = argparse.ArgumentParser(description="Generate a reference-locked drag sprite from the idle mother frame.")
    parser.add_argument("--source", default=str(DEFAULT_SOURCE))
    parser.add_argument("--sheet", default=str(ROOT / "pet-assets" / "drag-state-4x3.png"))

    return parser.parse_args()


def main():
    args = parse_args()
    frames = make_frames(Path(args.source).expanduser())

    save_sheet(frames, Path(args.sheet).expanduser())
    save_contact_sheet(frames, ROOT / "pet-assets" / "drag-state-4x3-contact.jpg")

    save_frames(frames[:3], "drag-enter-clean")
    save_frames(frames[3:9], "drag-loop-clean")
    save_frames(frames[9:], "drag-exit-clean")
    save_frames(frames, "drag-sequence-clean")

    save_preview(frames[:3], ROOT / "public" / "pet-preview" / "drag-enter-clean-preview.gif")
    save_preview(frames[3:9], ROOT / "public" / "pet-preview" / "drag-loop-clean-preview.gif")
    save_preview(frames[9:], ROOT / "public" / "pet-preview" / "drag-exit-clean-preview.gif")
    save_preview(frames, ROOT / "public" / "pet-preview" / "drag-sequence-clean-preview.gif")

    print("Wrote drag sprite sheet and 12 reference-locked frames")


if __name__ == "__main__":
    main()
