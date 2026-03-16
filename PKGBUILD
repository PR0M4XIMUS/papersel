# Maintainer: Your Name <your@email.com>

# ── Package metadata ──────────────────────────────────────────────────────────
pkgname=papersel                          # The AUR package name (must be unique)
pkgver=1.0.0                              # Version — bump this on every release
pkgrel=1                                  # Release number for this pkgver (reset to 1 on version bump)
pkgdesc="Minimalist wallpaper browser and setter for Omarchy / Hyprland"
arch=('any')                              # 'any' = pure Python, no compiled binaries
url="https://github.com/YOURUSERNAME/papersel"
license=('MIT')

# ── Runtime dependencies ──────────────────────────────────────────────────────
# These packages must be installed for papersel to RUN.
depends=(
    'python'            # The Python interpreter
    'python-gobject'    # Python bindings for GTK/GLib (gi.repository)
    'gtk4'              # The GTK4 widget toolkit
    'libadwaita'        # Adwaita widgets (Adw.ApplicationWindow, Adw.Toast, etc.)
)

# ── Optional dependencies ─────────────────────────────────────────────────────
# Users can install these for extra features. Not required to run.
optdepends=(
    'hyprpaper: set wallpapers on Hyprland (recommended)'
    'swww: animated wallpaper transitions (fallback backend)'
)

# ── Source files ──────────────────────────────────────────────────────────────
# For a git-hosted package you would use a tarball URL from GitHub releases:
#   source=("https://github.com/YOURUSERNAME/$pkgname/archive/v$pkgver.tar.gz")
#   sha256sums=('PASTE_SHA256_HERE')
#
# For local testing during development, use the files directly:
source=(
    "papersel.py"
    "papersel.desktop"
    "LICENSE"
)
# Run `makepkg -g` to auto-generate these checksums after placing source files
sha256sums=(
    'SKIP'
    'SKIP'
    'SKIP'
)

# ── Build step ────────────────────────────────────────────────────────────────
# Pure Python needs no compilation, so build() is empty.
build() {
    : # nothing to compile
}

# ── Install step ─────────────────────────────────────────────────────────────
# This runs as root inside a fake root environment (fakeroot).
# $pkgdir is the staging directory — it mimics the real filesystem.
package() {
    # Install the main Python script to /usr/bin/papersel
    # We create the directory first, then copy the script
    install -Dm755 "$srcdir/papersel.py" "$pkgdir/usr/bin/papersel"

    # Install the .desktop file so papersel appears in app launchers (Walker, etc.)
    install -Dm644 "$srcdir/papersel.desktop" \
        "$pkgdir/usr/share/applications/papersel.desktop"

    # Install the license — AUR policy requires this
    install -Dm644 "$srcdir/LICENSE" \
        "$pkgdir/usr/share/licenses/$pkgname/LICENSE"
}
