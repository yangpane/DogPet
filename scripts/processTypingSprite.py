import argparse
from collections import deque
from pathlib import Path

from PIL import Image, ImageFilter


ROOT = Path(__file__).resolve().parents[1]
CANVAS = 512
DEFAULT_GROUND_Y = 460
DEFAULT_PADDING_X = 42


def is_background(pixel):
    r, g, b = pixel[:3]
    high = max(r, g, b)
    low = min(r, g, b)

    return high >= 188 and low >= 176 and high - low <= 48


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
    alpha = alpha.filter(ImageFilter.GaussianBlur(0.7))

    clean = frame.copy()
    clean.putalpha(alpha)

    return clean


def object_bbox(frame):
    alpha = frame.getchannel("A")

    return alpha.point(lambda value: 255 if value > 24 else 0).getbbox()


def align_frame(frame, ground_y, padding_x, max_subject_height):
    bbox = object_bbox(frame)
    if not bbox:
        return Image.new("RGBA", (CANVAS, CANVAS), (0, 0, 0, 0))

    left, top, right, bottom = bbox
    subject = frame.crop(bbox)
    width = right - left
    height = bottom - top

    scale_limits = [
        (CANVAS - padding_x * 2) / width,
        ground_y / height,
        1.0,
    ]

    if max_subject_height:
        scale_limits.append(max_subject_height / height)

    scale = min(scale_limits)
    next_size = (round(width * scale), round(height * scale))
    subject = subject.resize(next_size, Image.Resampling.LANCZOS)

    canvas = Image.new("RGBA", (CANVAS, CANVAS), (0, 0, 0, 0))
    x = round((CANVAS - next_size[0]) / 2)
    y = ground_y - next_size[1]
    canvas.alpha_composite(subject, (x, y))

    return canvas


def write_preview_gif(frames, target):
    if not frames:
        return

    preview = [frame.copy() for frame in frames]
    preview[0].save(
        target,
        save_all=True,
        append_images=preview[1:],
        duration=100,
        loop=0,
        disposal=2,
    )


def parse_args():
    parser = argparse.ArgumentParser(description="Cut a pet sprite sheet into transparent, aligned PNG frames.")
    parser.add_argument("--source", required=True)
    parser.add_argument("--state", default="typing-clean")
    parser.add_argument("--cols", type=int, default=4)
    parser.add_argument("--rows", type=int, default=2)
    parser.add_argument("--ground-y", type=int, default=DEFAULT_GROUND_Y)
    parser.add_argument("--padding-x", type=int, default=DEFAULT_PADDING_X)
    parser.add_argument("--max-subject-height", type=int)
    parser.add_argument("--canvas", type=int, default=CANVAS)
    return parser.parse_args()


def main():
    args = parse_args()
    global CANVAS
    CANVAS = args.canvas

    source = Path(args.source).expanduser()
    if not source.exists():
        raise FileNotFoundError(f"Sprite sheet does not exist: {source}")

    frames = [
        align_frame(remove_background(frame), args.ground_y, args.padding_x, args.max_subject_height)
        for frame in crop_sprite_sheet(source, args.cols, args.rows)
    ]

    target_dirs = [
        ROOT / "pet-assets" / args.state,
        ROOT / "public" / "pet-preview" / args.state,
    ]

    for target_dir in target_dirs:
        target_dir.mkdir(parents=True, exist_ok=True)

        for index, frame in enumerate(frames, start=1):
            frame.save(target_dir / f"{index:03}.png")

    write_preview_gif(frames, ROOT / "public" / "pet-preview" / f"{args.state}-preview.gif")

    print(f"Wrote {len(frames)} cleaned frames for {args.state}")


if __name__ == "__main__":
    main()
