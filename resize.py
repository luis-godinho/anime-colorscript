import os
import sys
from PIL import Image, ImageSequence

TARGET_WIDTH = 250

IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png", ".webp", ".bmp", ".tiff", ".gif"}

resample_filter = Image.Resampling.LANCZOS


def resize_static_image(img, target_width):
    aspect_ratio = img.height / img.width
    new_height = int(target_width * aspect_ratio)
    return img.resize((target_width, new_height), resample_filter)


def resize_gif(im, output_path, target_width):
    """
    Resize an animated GIF while preserving frame durations, loop count and basic transparency.
    """
    frames = []
    durations = []
    # preserve loop count if present
    loop = im.info.get("loop", 0)
    transparency = im.info.get("transparency", None)

    for frame in ImageSequence.Iterator(im):
        # get each frame's duration (ms); fallback to 100ms if missing
        durations.append(frame.info.get("duration", 100))

        # Convert frame to RGBA so resizing keeps alpha correct, then resize
        frame_rgba = frame.convert("RGBA")
        resized_rgba = resize_static_image(frame_rgba, target_width)

        # Convert back to palette ("P") for GIF output (adaptive palette)
        paletted = resized_rgba.convert("P", palette=Image.Palette.ADAPTIVE)

        frames.append(paletted)

    # Ensure output dir exists
    os.makedirs(os.path.dirname(output_path), exist_ok=True)

    # Save: first frame + append the rest, preserve durations and loop.
    # transparency passed through if available.
    save_kwargs = {
        "save_all": True,
        "append_images": frames[1:],
        "duration": durations,
        "loop": loop,
        "optimize": False,
    }
    if transparency is not None:
        save_kwargs["transparency"] = transparency

    frames[0].save(output_path, format="GIF", **save_kwargs)


def resize_image(path, output_path):
    try:
        with Image.open(path) as img:
            ext = os.path.splitext(path)[1].lower()
            # Animated GIF branch
            if ext == ".gif" and getattr(img, "is_animated", False):
                resize_gif(img, output_path, TARGET_WIDTH)
            else:
                # static image (or non-animated gif) — resize and save normally
                # convert non-paletted images where appropriate to preserve quality
                if img.mode not in ("RGB", "RGBA", "L"):
                    img = img.convert("RGBA")
                resized = resize_static_image(img, TARGET_WIDTH)

                os.makedirs(os.path.dirname(output_path), exist_ok=True)
                # use same format as input if possible
                save_format = img.format if img.format else None
                if save_format:
                    resized.save(output_path, format=save_format)
                else:
                    resized.save(output_path)
            print(f"Resized: {output_path}")
    except Exception as e:
        print(f"Failed to process {path}: {e}")


def process_directory(root_dir):
    for root, _, files in os.walk(root_dir):
        for file in files:
            ext = os.path.splitext(file)[1].lower()
            if ext in IMAGE_EXTENSIONS:
                full_path = os.path.join(root, file)

                relative_path = os.path.relpath(full_path, root_dir)
                output_path = os.path.join("resized", relative_path)

                resize_image(full_path, output_path)


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python resize_images.py /path/to/directory")
    else:
        process_directory(sys.argv[1])
