import argparse
import sys
from pathlib import Path
import tkinter as tk
from tkinter import filedialog, messagebox

from PIL import Image, ImageTk

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


class ImageUprightApp:
    def __init__(self, root: tk.Tk, folder: Path):
        self.root = root
        self.folder = folder
        self.image_paths = self._load_image_paths(folder)

        if not self.image_paths:
            messagebox.showerror(
                "No Images Found", f"No supported images found in:\n{folder}")
            self.root.destroy()
            return

        self.current_index = 0
        self.current_image = None
        self.current_photo = None

        self.root.title("Image Upright Tool")
        self.root.geometry("1200x800")
        self.root.minsize(700, 500)

        self._build_ui()
        self._bind_keys()
        self._show_current_image()

        # Try to ensure the Tk window and image label have keyboard focus.
        try:
            self.root.lift()
            # focus after a short delay so the window has time to appear
            self.root.after(150, lambda: (
                self.root.focus_force(), self.image_label.focus_set()))
        except Exception:
            pass

    @staticmethod
    def _load_image_paths(folder: Path):
        return sorted(
            [
                p
                for p in folder.iterdir()
                if p.is_file() and p.suffix.lower() in SUPPORTED_EXTENSIONS
            ]
        )

    def _build_ui(self):
        self.root.rowconfigure(1, weight=1)
        self.root.columnconfigure(0, weight=1)

        top_frame = tk.Frame(self.root)
        top_frame.grid(row=0, column=0, sticky="ew", padx=10, pady=10)
        top_frame.columnconfigure(1, weight=1)

        self.status_label = tk.Label(
            top_frame, text="", anchor="w", font=("Segoe UI", 10, "bold"))
        self.status_label.grid(row=0, column=0, sticky="w")

        self.help_label = tk.Label(
            top_frame,
            text="Left/Right: Previous/Next image | Up/Down: Rotate 180 and save | Bulk buttons: rotate landscape images",
            anchor="e",
            fg="#333333",
        )
        self.help_label.grid(row=0, column=1, sticky="e")

        image_container = tk.Frame(self.root, bg="#222222")
        image_container.grid(
            row=1, column=0, sticky="nsew", padx=10, pady=(0, 10))
        image_container.rowconfigure(0, weight=1)
        image_container.columnconfigure(0, weight=1)

        # Make the image label focusable so it can receive key events.
        self.image_label = tk.Label(image_container, bg="#222222", takefocus=1)
        self.image_label.grid(row=0, column=0, sticky="nsew")

        controls = tk.Frame(self.root)
        controls.grid(row=2, column=0, sticky="ew", padx=10, pady=(0, 10))

        self.prev_button = tk.Button(
            controls, text="Left (Previous)", command=self.show_previous)
        self.prev_button.pack(side="left", padx=5)

        self.next_button = tk.Button(
            controls, text="Right (Next)", command=self.show_next)
        self.next_button.pack(side="left", padx=5)

        self.rotate_left_button = tk.Button(
            controls, text="Rotate Left", command=lambda: self.rotate_current(-90))
        self.rotate_left_button.pack(side="left", padx=15)

        self.rotate_right_button = tk.Button(
            controls, text="Rotate Right", command=lambda: self.rotate_current(90))
        self.rotate_right_button.pack(side="left", padx=5)

        self.bulk_rotate_left_button = tk.Button(
            controls,
            text="Bulk Rotate -90",
            command=lambda: self.bulk_rotate_landscape(-90),
        )
        self.bulk_rotate_left_button.pack(side="left", padx=15)

        self.bulk_rotate_right_button = tk.Button(
            controls,
            text="Bulk Rotate +90",
            command=lambda: self.bulk_rotate_landscape(90),
        )
        self.bulk_rotate_right_button.pack(side="left", padx=5)

        self.quit_button = tk.Button(
            controls, text="Quit", command=self.root.quit)
        self.quit_button.pack(side="right", padx=5)

        # Refit image when window size changes.
        self.root.bind("<Configure>", self._on_resize)

    def _bind_keys(self):
        # Use a single key handler for diagnostics and reliability.
        self.root.bind_all("<Key>", self._on_key)

    def _on_key(self, event):
        if event.keysym == "Left":
            self.show_previous()
        elif event.keysym == "Right":
            self.show_next()
        elif event.keysym == "Up":
            self.rotate_current(180)
        elif event.keysym == "Down":
            self.rotate_current(180)

    def _on_resize(self, _event):
        if self.current_image is not None:
            self._display_image(self.current_image)

    def _show_current_image(self):
        path = self.image_paths[self.current_index]
        try:
            self.current_image = Image.open(path)
            self._display_image(self.current_image)
            # ensure the image label has focus so keyboard presses are handled
            try:
                self.image_label.focus_set()
            except Exception:
                pass
            self.status_label.config(
                text=f"{self.current_index + 1}/{len(self.image_paths)} - {path.name}"
            )
        except Exception as exc:
            messagebox.showerror(
                "Error", f"Could not open image:\n{path}\n\n{exc}")

    def _is_landscape(self, image: Image.Image) -> bool:
        return image.width > image.height

    def _display_image(self, image: Image.Image):
        # Keep aspect ratio while fitting image to the available canvas size.
        width = self.image_label.winfo_width()
        height = self.image_label.winfo_height()

        if width <= 1 or height <= 1:
            width = max(self.root.winfo_width() - 40, 200)
            height = max(self.root.winfo_height() - 180, 200)

        display = image.copy()
        display.thumbnail((width, height), Image.Resampling.LANCZOS)

        self.current_photo = ImageTk.PhotoImage(display)
        self.image_label.config(image=self.current_photo)

    def show_previous(self):
        if not self.image_paths:
            return
        self.current_index = (self.current_index - 1) % len(self.image_paths)
        self._show_current_image()

    def show_next(self):
        if not self.image_paths:
            return
        self.current_index = (self.current_index + 1) % len(self.image_paths)
        self._show_current_image()

    def rotate_current(self, degrees: int):
        if self.current_image is None:
            return

        path = self.image_paths[self.current_index]

        # Pillow rotate is counter-clockwise; expand keeps full image bounds.
        rotated = self.current_image.rotate(degrees, expand=True)

        try:
            rotated.save(path)
            self.current_image = rotated
            self._display_image(self.current_image)
            self.status_label.config(
                text=f"{self.current_index + 1}/{len(self.image_paths)} - {path.name} (saved)"
            )
        except Exception as exc:
            messagebox.showerror(
                "Save Error", f"Could not save image:\n{path}\n\n{exc}")

    def bulk_rotate_landscape(self, degrees: int):
        rotated_count = 0

        for path in self.image_paths:
            try:
                with Image.open(path) as image:
                    if not self._is_landscape(image):
                        continue

                    rotated = image.rotate(degrees, expand=True)
                    rotated.save(path)
                    rotated_count += 1
            except Exception as exc:
                messagebox.showerror(
                    "Bulk Rotate Error", f"Could not rotate image:\n{path}\n\n{exc}"
                )
                return

        self._show_current_image()
        self.status_label.config(
            text=(
                f"{self.current_index + 1}/{len(self.image_paths)} - "
                f"{self.image_paths[self.current_index].name} "
                f"(bulk rotated {rotated_count} images)"
            )
        )


def choose_folder() -> Path | None:
    selected = filedialog.askdirectory(title="Select image folder")
    if not selected:
        return None
    return Path(selected)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Browse images and rotate them upright with arrow keys."
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

    root = tk.Tk()

    if folder is None:
        folder = choose_folder()

    if folder is None:
        root.destroy()
        return

    if not folder.exists() or not folder.is_dir():
        messagebox.showerror(
            "Invalid Folder", f"Not a valid folder:\n{folder}")
        root.destroy()
        sys.exit(1)

    app = ImageUprightApp(root, folder)
    if app.image_paths:
        root.mainloop()


if __name__ == "__main__":
    main()
