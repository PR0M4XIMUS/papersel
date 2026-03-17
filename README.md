# papersel

A minimalist wallpaper browser and setter for **Omarchy / Hyprland** on Arch Linux.

Built with **GTK4 + libadwaita** — feels native, follows your system dark/light theme automatically.

![papersel screenshot](screenshot.png)

---

## Features

- Browse wallpapers in any folder as a visual thumbnail grid
- Automatically loads from `~/.config/omarchy/backgrounds/` or any folder you choose
- Set wallpaper system-wide via **hyprpaper** (recommended) or **swww** (fallback)
- Remembers your last folder between sessions
- Minimal UI inspired by Material You / Android 12+ design language
- Zero background processes — only runs when you open it

---

## Dependencies

| Package | Why |
|---|---|
| `python` | Runtime |
| `python-gobject` | GTK bindings |
| `gtk4` | UI toolkit |
| `libadwaita` | Modern Adwaita widgets |
| `hyprpaper` *(optional)* | Set wallpapers on Hyprland |
| `swww` *(optional)* | Animated wallpaper transitions |

---

## Installation

### From AUR (recommended)

Once published:

```bash
yay -S papersel
# or
paru -S papersel
```

### Manual build from source

```bash
git clone https://github.com/YOURUSERNAME/papersel
cd papersel
makepkg -si
```

---

## Usage

Launch from your app menu, or run:

```bash
papersel
```

1. On first launch, click the **folder icon** in the header to choose your wallpapers directory.
2. Click any thumbnail to select it.
3. Press **Set Wallpaper** to apply it via hyprpaper.

### Omarchy tip

Your Omarchy theme backgrounds live at:

```
~/.config/omarchy/backgrounds/<theme-name>/
```

Point papersel at that folder to manage them visually.

---

## How wallpaper setting works

papersel uses **hyprpaper IPC** via `hyprctl`:

```bash
hyprctl hyprpaper preload /path/to/image.jpg
hyprctl hyprpaper wallpaper ",/path/to/image.jpg"
```

If hyprpaper isn't running, it falls back to `swww img`.

---

## Development

```bash
# Run directly without installing
python papersel.py
```

---

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

---

## License

MIT — see [LICENSE](LICENSE).
