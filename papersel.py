#!/usr/bin/env python3
"""
papersel -- A minimalist wallpaper browser and setter for Omarchy/Hyprland.
Built with GTK4 + libadwaita. Wayland-native via hyprpaper IPC.
"""

# ─── Standard library imports ────────────────────────────────────────────────
import os           # File paths, environment variables
import sys          # Exit the app cleanly
import subprocess   # Run shell commands (hyprctl, swww)
import json         # Save/load app settings
from pathlib import Path  # Modern, safe path handling

# ─── GTK / Adwaita imports ───────────────────────────────────────────────────
import gi
gi.require_version("Gtk", "4.0")
gi.require_version("Adw", "1")
gi.require_version("Gdk", "4.0")
from gi.repository import Gtk, Adw, Gdk, GLib, Gio, GdkPixbuf

# ─── Constants ───────────────────────────────────────────────────────────────

# Supported image formats papersel will recognise
SUPPORTED_EXTENSIONS = {".jpg", ".jpeg", ".png", ".webp", ".gif", ".bmp"}

# Where Omarchy themes store their backgrounds
OMARCHY_BACKGROUNDS = Path.home() / ".config" / "omarchy" / "backgrounds"

# Where we store the user's settings between sessions
CONFIG_FILE = Path.home() / ".config" / "papersel" / "config.json"

# Default folder if nothing is configured yet
DEFAULT_WALLPAPER_DIR = Path.home() / "Pictures" / "wallpapers"

# Thumbnail size shown in the grid (pixels)
THUMB_SIZE = 200


# ─── Settings helper ─────────────────────────────────────────────────────────

def load_config() -> dict:
    """
    Read the saved config from disk.
    Returns an empty dict if the file doesn't exist yet -- that's fine,
    the app will use its defaults.
    """
    if CONFIG_FILE.exists():
        try:
            with open(CONFIG_FILE, "r") as f:
                return json.load(f)
        except (json.JSONDecodeError, OSError, IOError):
            return {}
    return {}


def save_config(data: dict) -> None:
    """
    Write the config dict to disk.
    We create the directory first if it doesn't exist.
    """
    try:
        CONFIG_FILE.parent.mkdir(parents=True, exist_ok=True)
        with open(CONFIG_FILE, "w") as f:
            json.dump(data, f, indent=2)
    except OSError:
        pass


# ─── Wallpaper setter ─────────────────────────────────────────────────────────

def set_wallpaper_hyprpaper(path: str) -> bool:
    """
    Set the wallpaper on Hyprland using hyprpaper IPC.

    How it works:
      1. We first 'preload' the image -- this tells hyprpaper to load it into memory.
      2. Then we tell hyprpaper to set it on ALL monitors (empty string = all).
      3. Finally we unload any previously preloaded image to free memory.

    Returns True if successful, False if something went wrong.
    """
    try:
        subprocess.run(
            ["hyprctl", "hyprpaper", "preload", path],
            check=True, capture_output=True, timeout=5
        )
        subprocess.run(
            ["hyprctl", "hyprpaper", "wallpaper", f",{path}"],
            check=True, capture_output=True, timeout=5
        )
        return True
    except (subprocess.CalledProcessError, FileNotFoundError, subprocess.TimeoutExpired, OSError):
        return False


def set_wallpaper_swww(path: str) -> bool:
    """
    Set the wallpaper using swww -- supports smooth animated transitions.
    Falls back automatically if hyprpaper is not available.
    """
    try:
        subprocess.run(
            ["swww", "img", path, "--transition-type", "fade"],
            check=True, capture_output=True, timeout=10
        )
        return True
    except (subprocess.CalledProcessError, FileNotFoundError, subprocess.TimeoutExpired, OSError):
        return False


def set_wallpaper(path: str) -> tuple[bool, str]:
    """
    Try to set the wallpaper using the best available backend.
    Priority: hyprpaper → swww → failure.

    Returns (success: bool, backend_used: str).
    """
    if set_wallpaper_hyprpaper(path):
        return True, "hyprpaper"
    if set_wallpaper_swww(path):
        return True, "swww"
    return False, "none"


# ─── Thumbnail loader ─────────────────────────────────────────────────────────

def load_thumbnail(image_path: str) -> GdkPixbuf.Pixbuf | None:
    """
    Load an image file and scale it down to a square thumbnail.
    Returns None if the file can't be read (broken/unsupported image).
    """
    try:
        pixbuf = GdkPixbuf.Pixbuf.new_from_file_at_scale(
            image_path,
            width=THUMB_SIZE,
            height=THUMB_SIZE,
            preserve_aspect_ratio=True
        )
        return pixbuf
    except GLib.Error:
        return None


# ─── Wallpaper tile widget ────────────────────────────────────────────────────

class WallpaperTile(Gtk.Box):
    """
    A single card in the grid. Shows a thumbnail + the filename below it.
    Clicking it triggers the on_click callback with the full file path.
    """

    def __init__(self, image_path: str, on_click):
        super().__init__(orientation=Gtk.Orientation.VERTICAL, spacing=6)
        self.image_path = image_path
        self.on_click = on_click
        self.set_margin_start(4)
        self.set_margin_end(4)
        self.set_margin_top(4)
        self.set_margin_bottom(4)

        # ── Thumbnail image ──────────────────────────────────────────────────
        pixbuf = load_thumbnail(image_path)
        if pixbuf:
            image = Gtk.Image.new_from_pixbuf(pixbuf)
        else:
            # Show a placeholder icon if the image failed to load
            image = Gtk.Image.new_from_icon_name("image-missing")
        image.set_size_request(THUMB_SIZE, THUMB_SIZE)
        image.add_css_class("thumbnail")
        self.append(image)

        # ── Filename label ───────────────────────────────────────────────────
        label = Gtk.Label(label=Path(image_path).name)
        label.set_max_width_chars(20)   # Truncate long names
        label.set_ellipsize(3)          # Add "…" at the end if too long
        label.add_css_class("caption")
        self.append(label)

        # ── Make the whole tile clickable ────────────────────────────────────
        gesture = Gtk.GestureClick.new()
        gesture.connect("released", self._on_released)
        self.image_path = image_path
        self.add_controller(gesture)

        # Visual hover effect -- highlight on mouse-over
        motion = Gtk.EventControllerMotion.new()
        motion.connect("enter", lambda *_: self.add_css_class("tile-hover"))
        motion.connect("leave", lambda *_: self.remove_css_class("tile-hover"))
        self.add_controller(motion)

        self.add_css_class("wallpaper-tile")

    def _on_released(self, gesture, n, x, y):
        """Handle click events on the tile."""
        self.on_click(self.image_path)


# ─── Main application window ──────────────────────────────────────────────────

class PaperSelWindow(Adw.ApplicationWindow):
    """
    The main window. Contains:
     - A top header bar with folder picker and title
     - A scrollable grid of wallpaper thumbnails
     - A bottom bar showing the selected wallpaper and a Set button
    """

    def __init__(self, app):
        super().__init__(application=app)
        self.set_title("papersel")
        self.set_default_size(960, 680)

        # Load user config; get the last-used folder (or our default)
        self.config = load_config()
        self.wallpaper_dir = Path(
            self.config.get("wallpaper_dir", str(DEFAULT_WALLPAPER_DIR))
        )
        self.selected_path: str | None = None  # Currently highlighted wallpaper

        self._build_ui()
        self._apply_css()

        # Load wallpapers after the window is shown (feels snappier)
        GLib.idle_add(self._scan_wallpapers)

    # ── UI construction ──────────────────────────────────────────────────────

    def _build_ui(self):
        """Assemble all the widgets into the window layout."""

        # Outer vertical box -- everything stacks top to bottom
        root = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        self.set_content(root)

        # ── Header bar ───────────────────────────────────────────────────────
        header = Adw.HeaderBar()
        header.add_css_class("flat")

        # "Open Folder" button on the left side of the header
        open_btn = Gtk.Button(icon_name="folder-open-symbolic")
        open_btn.set_tooltip_text("Choose wallpaper folder")
        open_btn.connect("clicked", self._on_open_folder)
        header.pack_start(open_btn)

        # Title widget -- shows app name + current folder path
        title_widget = Adw.WindowTitle(
            title="papersel",
            subtitle=str(self.wallpaper_dir)
        )
        self.title_widget = title_widget  # Keep a reference to update later
        header.set_title_widget(title_widget)

        root.append(header)

        # ── Scrollable wallpaper grid ─────────────────────────────────────────
        self.scroll = Gtk.ScrolledWindow()
        self.scroll.set_vexpand(True)          # Fill all available height
        self.scroll.set_policy(              # Show scrollbar only when needed
            Gtk.PolicyType.NEVER,
            Gtk.PolicyType.AUTOMATIC
        )

        # FlowBox: automatically wraps tiles into rows as the window resizes
        self.grid = Gtk.FlowBox()
        self.grid.set_valign(Gtk.Align.START)
        self.grid.set_max_children_per_line(30)  # Allow many columns
        self.grid.set_min_children_per_line(2)
        self.grid.set_column_spacing(8)
        self.grid.set_row_spacing(8)
        self.grid.set_margin_start(16)
        self.grid.set_margin_end(16)
        self.grid.set_margin_top(16)
        self.grid.set_margin_bottom(16)
        self.grid.set_selection_mode(Gtk.SelectionMode.NONE)  # We handle selection

        self.scroll.set_child(self.grid)

        # Wrap the scroll area in a clamp so it doesn't stretch too wide
        clamp = Adw.Clamp()
        clamp.set_maximum_size(1600)
        clamp.set_child(self.scroll)
        root.append(clamp)

        # ── Empty state (shown when folder has no images) ─────────────────────
        self.empty_status = Adw.StatusPage(
            title="No wallpapers found",
            description="Choose a folder that contains image files.",
            icon_name="image-missing"
        )
        self.empty_status.set_visible(False)
        root.append(self.empty_status)

        # ── Bottom action bar ─────────────────────────────────────────────────
        action_bar = Gtk.ActionBar()
        action_bar.add_css_class("action-bar")

        # Label showing which wallpaper is selected
        self.selected_label = Gtk.Label(label="No wallpaper selected")
        self.selected_label.set_ellipsize(3)
        self.selected_label.set_hexpand(True)
        self.selected_label.set_halign(Gtk.Align.START)
        self.selected_label.add_css_class("caption")
        action_bar.pack_start(self.selected_label)

        # "Set Wallpaper" button -- the main action
        self.set_btn = Gtk.Button(label="Set Wallpaper")
        self.set_btn.add_css_class("suggested-action")  # Highlighted/accent colour
        self.set_btn.set_sensitive(False)               # Disabled until something is selected
        self.set_btn.connect("clicked", self._on_set_wallpaper)
        action_bar.pack_end(self.set_btn)

        root.append(action_bar)

    # ── CSS styling ──────────────────────────────────────────────────────────

    def _apply_css(self):
        """
        Inject custom CSS to make the app look clean and minimal.
        We use Adwaita's CSS variables so dark/light mode is automatic.
        """
        css = b"""
        /* Wallpaper tile -- the card around each thumbnail */
        .wallpaper-tile {
            border-radius: 12px;
            padding: 8px;
            background-color: alpha(@card_bg_color, 0.5);
            transition: background-color 120ms ease,
                        transform 120ms ease;
        }

        /* Hover effect -- subtle lift */
        .wallpaper-tile.tile-hover {
            background-color: @card_bg_color;
            transform: translateY(-2px);
        }

        /* Selected tile -- accent ring */
        .wallpaper-tile.selected {
            outline: 2px solid @accent_color;
            outline-offset: 2px;
        }

        /* Make thumbnails rounded */
        .thumbnail {
            border-radius: 8px;
        }

        /* Small grey caption text */
        .caption {
            font-size: 0.75rem;
            color: alpha(@window_fg_color, 0.6);
        }
        """
        provider = Gtk.CssProvider()
        provider.load_from_data(css)
        Gtk.StyleContext.add_provider_for_display(
            Gdk.Display.get_default(),
            provider,
            Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION
        )

    # ── Folder scanning ──────────────────────────────────────────────────────

    def _scan_wallpapers(self) -> bool:
        """
        Find all image files in the selected folder and populate the grid.
        Returns False so GLib.idle_add doesn't call this repeatedly.
        """
        while child := self.grid.get_first_child():
            self.grid.remove(child)

        self.selected_path = None
        self.set_btn.set_sensitive(False)
        self.selected_label.set_text("No wallpaper selected")

        try:
            images = sorted([
                str(p) for p in self.wallpaper_dir.iterdir()
                if p.suffix.lower() in SUPPORTED_EXTENSIONS
            ]) if self.wallpaper_dir.exists() else []
        except (OSError, PermissionError):
            images = []

        if not images:
            # Show the empty state placeholder instead of a blank grid
            self.scroll.set_visible(False)
            self.empty_status.set_visible(True)
            return False

        self.scroll.set_visible(True)
        self.empty_status.set_visible(False)

        # Add a tile for each image
        for img_path in images:
            tile = WallpaperTile(img_path, self._on_tile_clicked)
            self.grid.append(tile)

        return False  # Tell GLib.idle_add we're done

    # ── User actions ─────────────────────────────────────────────────────────

    def _on_tile_clicked(self, path: str):
        """
        Called when the user clicks a wallpaper tile.
        Marks it as selected and enables the Set button.
        """
        # Remove 'selected' style from the previously chosen tile
        child = self.grid.get_first_child()
        while child:
            # FlowBoxChild wraps our tile, so we need to get the inner widget
            inner = child.get_child()
            if inner:
                inner.remove_css_class("selected")
            child = child.get_next_sibling()

        # Find the tile that matches our path and mark it selected
        child = self.grid.get_first_child()
        while child:
            inner = child.get_child()
            if inner and hasattr(inner, "image_path") and inner.image_path == path:
                inner.add_css_class("selected")
                break
            child = child.get_next_sibling()

        # Update state
        self.selected_path = path
        self.selected_label.set_text(Path(path).name)
        self.set_btn.set_sensitive(True)

    def _on_set_wallpaper(self, _btn):
        """
        Called when the user presses 'Set Wallpaper'.
        Tries hyprpaper first, then swww, and shows a toast with the result.
        """
        if not self.selected_path:
            return

        success, backend = set_wallpaper(self.selected_path)

        # Show a small notification toast at the bottom of the window
        toast = Adw.Toast()
        if success:
            toast.set_title(f"Wallpaper set via {backend} ✓")
            # Save this as the last-used wallpaper in config
            self.config["last_wallpaper"] = self.selected_path
            save_config(self.config)
        else:
            toast.set_title("Could not set wallpaper -- is hyprpaper or swww running?")
            toast.set_timeout(4)

        # ToastOverlay must wrap our content to display toasts
        # We find it by walking up the widget tree
        self._show_toast(toast)

    def _show_toast(self, toast: Adw.Toast):
        """
        Display a toast notification. We wrap the window content in a
        ToastOverlay on first use so we don't need to restructure the UI.
        """
        # If we already have an overlay, use it
        if hasattr(self, "_toast_overlay"):
            self._toast_overlay.add_toast(toast)
            return

        # First time: wrap existing content in a ToastOverlay
        content = self.get_content()
        self.set_content(None)
        overlay = Adw.ToastOverlay()
        overlay.set_child(content)
        self.set_content(overlay)
        self._toast_overlay = overlay
        overlay.add_toast(toast)

    def _on_open_folder(self, _btn):
        """
        Open a folder-chooser dialog and update the wallpaper directory.
        Uses the modern GTK4 FileDialog API.
        """
        dialog = Gtk.FileDialog()
        dialog.set_title("Choose wallpaper folder")

        # Pre-open the dialog at the current wallpaper directory
        if self.wallpaper_dir.exists():
            initial = Gio.File.new_for_path(str(self.wallpaper_dir))
            dialog.set_initial_folder(initial)

        # select_folder is async -- the callback fires when the user is done
        dialog.select_folder(self, None, self._on_folder_chosen)

    def _on_folder_chosen(self, dialog, result):
        """Callback for the folder dialog. Updates dir and reloads images."""
        try:
            folder = dialog.select_folder_finish(result)
            if folder:
                self.wallpaper_dir = Path(folder.get_path())
                self.title_widget.set_subtitle(str(self.wallpaper_dir))
                self.config["wallpaper_dir"] = str(self.wallpaper_dir)
                save_config(self.config)
                self._scan_wallpapers()
        except (GLib.Error, TypeError):
            pass  # User cancelled -- do nothing


# ─── Application entry point ──────────────────────────────────────────────────

class PaperSelApp(Adw.Application):
    """
    The top-level application object. GTK requires one of these.
    It manages the app lifecycle (startup, shutdown, single-instance).
    """

    def __init__(self):
        super().__init__(
            application_id="io.github.papersel",   # Reverse-DNS style app ID
            flags=Gio.ApplicationFlags.FLAGS_NONE
        )
        self.connect("activate", self.on_activate)

    def on_activate(self, app):
        """Called when the app starts. We create and show the main window."""
        win = PaperSelWindow(app)
        win.present()


def main():
    app = PaperSelApp()
    return app.run(sys.argv)


if __name__ == "__main__":
    sys.exit(main())
