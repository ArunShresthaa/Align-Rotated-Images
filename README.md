# Image Upright Tool

A simple desktop app to help fix randomly rotated images in a folder.

## Features

- Loads all images from a selected folder
- Navigate images with:
  - `Up` key or `Up (Previous)` button
  - `Down` key or `Down (Next)` button
- Rotate and save current image with:
  - `Left` key (`-90` degrees)
  - `Right` key (`+90` degrees)

Supported image types: `.jpg`, `.jpeg`, `.png`, `.bmp`, `.gif`, `.tif`, `.tiff`, `.webp`

## Setup

```powershell
pip install -r requirements.txt
```

## Run

Open folder picker:

```powershell
python main.py
```

Or pass a folder path directly:

```powershell
python main.py "C:\path\to\your\images"
```

## Notes

- Rotations are saved immediately by overwriting the current image file.
- Keep a backup of important images if you want a non-destructive workflow.
