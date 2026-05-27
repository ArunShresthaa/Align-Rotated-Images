import argparse
import sys
from pathlib import Path
import tkinter as tk
from tkinter import filedialog
import os

from PIL import Image

SUPPORTED_EXTENSIONS = {
    ".jpg",
    ".jpeg",
    ".png",
    ".bmp",
    ".gif",
    ".tif",
    ".tiff",
    ".webp",
}


def choose_folder() -> Path | None:
    root = tk.Tk()
    root.withdraw()
    selected = filedialog.askdirectory(title="Select folder to clear EXIF")
    root.destroy()
    if not selected:
        return None
    return Path(selected)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Clear EXIF data from all supported images in a folder without altering orientation or anything else."
    )
    parser.add_argument(
        "folder",
        nargs="?",
        help="Path to folder containing images. If omitted, a folder picker opens.",
    )
    return parser.parse_args()


def main():
    args = parse_args()
    folder = Path(args.folder).expanduser() if args.folder else None

    if folder is None:
        folder = choose_folder()

    if folder is None:
        print("No folder selected. Exiting.")
        sys.exit(0)

    if not folder.exists() or not folder.is_dir():
        print(f"Invalid folder: {folder}")
        sys.exit(1)

    image_paths = sorted(
        p for p in folder.iterdir()
        if p.is_file() and p.suffix.lower() in SUPPORTED_EXTENSIONS
    )

    if not image_paths:
        print(f"No supported images found in {folder}")
        sys.exit(0)

    processed = 0
    skipped = 0
    failed = 0

    print(
        f"Scanning {len(image_paths)} images for EXIF data in '{folder.name}'...")

    for i, path in enumerate(image_paths, 1):
        temp_path = path.with_suffix(path.suffix + ".tmp")
        try:
            with Image.open(path) as img:
                # Check for either the raw exif info block or the parsed getexif()
                has_exif = ("exif" in img.info) or bool(img.getexif())

                if not has_exif:
                    skipped += 1
                    continue

                save_kwargs = {
                    "format": img.format
                }
                if path.suffix.lower() in {".jpg", ".jpeg"}:
                    save_kwargs["quality"] = "keep"
                    save_kwargs["subsampling"] = "keep"

                # By default, PIL won't write EXIF unless explicitly passed 'exif' keyword arg
                img.save(temp_path, **save_kwargs)

            # Atomically replace the original with the EXIF-cleared version
            temp_path.replace(path)

            processed += 1
            print(f"[{i}/{len(image_paths)}] Cleared EXIF: {path.name}")

        except Exception as exc:
            # Clean up the temp file if it failed midway
            if temp_path.exists():
                temp_path.unlink()
            print(f"[{i}/{len(image_paths)}] Failed to process {path.name}: {exc}")
            failed += 1

    print("-" * 50)
    print("Summary:")
    print(f"Successfully cleared: {processed}")
    print(f"Skipped (No EXIF):    {skipped}")
    print(f"Failed:               {failed}")


if __name__ == "__main__":
    main()
