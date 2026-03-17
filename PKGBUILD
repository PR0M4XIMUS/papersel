# Maintainer: Your Name <your@email.com>

# ── Package metadata ──────────────────────────────────────────────────────────
pkgname=papersel
pkgver=1.0.0
pkgrel=1
pkgdesc="Minimalist wallpaper browser and setter for Omarchy / Hyprland"
arch=('any')
url="https://github.com/YOURUSERNAME/papersel"
license=('MIT')
makedepends=('git')

# ── Runtime dependencies ──────────────────────────────────────────────────────
depends=(
    'python'
    'python-gobject'
    'gtk4'
    'libadwaita'
)

# ── Optional dependencies ─────────────────────────────────────────────────────
optdepends=(
    'hyprpaper: set wallpapers on Hyprland (recommended)'
    'swww: animated wallpaper transitions (fallback backend)'
)

# ── Source files ──────────────────────────────────────────────────────────────
source=(
    "$pkgname-$pkgver::https://github.com/YOURUSERNAME/$pkgname/archive/refs/tags/v$pkgver.tar.gz"
)
sha256sums=('SKIP')

# ── Build step ────────────────────────────────────────────────────────────────
build() {
    :
}

# ── Install step ─────────────────────────────────────────────────────────────
package() {
    cd "$srcdir/$pkgname-$pkgver"

    install -Dm755 "papersel.py" "$pkgdir/usr/bin/papersel"
    install -Dm644 "papersel.desktop" "$pkgdir/usr/share/applications/papersel.desktop"
    install -Dm644 "LICENSE" "$pkgdir/usr/share/licenses/$pkgname/LICENSE"
    install -Dm644 "icons/hicolor/scalable/apps/papersel.svg" \
        "$pkgdir/usr/share/icons/hicolor/scalable/apps/papersel.svg"
}
