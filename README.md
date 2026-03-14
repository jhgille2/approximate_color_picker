# Approximate Color Guesser

Approximate Color Guesser is a desktop app for artists and designers with color vision differences.

It monitors a user-selected region of your screen (for example, a color swatch, palette, or preview in any digital art or color application) and describes the sampled color in plain language (e.g. `muted blue`, `bright yellow`, `very dark red`).

## Why this helps

Many digital art and color applications do not expose a simple external API for the active color. This tool works visually by sampling pixels from your screen, so it can be used with any software where the color preview is visible.

## Features

- Click-and-drag region selector (overlay)
- Live color sampling from any region of your screen
- Multiple sampling modes:
  - `Center pixel`
  - `Average region`
  - `Most saturated pixel`
- Approximate color naming in English, Spanish, French, or German
- Live RGB + HEX values

## Setup & Running (All OS)

### Windows
1. Open terminal in the project folder.
2. Create and activate a virtual environment:
  ```powershell
  python -m venv .venv
  .\.venv\Scripts\Activate.ps1
  ```
3. Install dependencies:
  ```powershell
  pip install -r requirements.txt
  ```
4. Run:
  ```powershell
  python app.py
  ```

### macOS
1. Open Terminal in the project folder.
2. Create and activate a virtual environment:
  ```bash
  python3 -m venv .venv
  source .venv/bin/activate
  ```
3. Install dependencies:
  ```bash
  pip install -r requirements.txt
  ```
4. Run:
  ```bash
  python app.py
  ```

### Linux
1. Open Terminal in the project folder.
2. Create and activate a virtual environment:
  ```bash
  python3 -m venv .venv
  source .venv/bin/activate
  ```
3. Install dependencies:
  ```bash
  pip install -r requirements.txt
  ```
4. Run:
  ```bash
  python app.py
  ```

**Note:** On Linux, you may need to install Tkinter and Pillow system dependencies:
```bash
sudo apt-get install python3-tk python3-pil python3-pil.imagetk
```

If you ever see `ImportError: cannot import name '_imaging' from 'PIL'`, repair Pillow in the venv:
```bash
pip uninstall -y pillow
pip install --no-cache-dir -r requirements.txt
```

## How to use with any digital art or color application

1. Open your digital art or color application and keep the color preview, swatch, or palette visible.
2. In this app, click **Select Region**.
3. Drag a rectangle over the part of your screen that best represents your current selected color (usually the color preview swatch, palette, or color wheel).
4. Choose a sampling mode:
  - `Center pixel` works best for a small swatch.
  - `Average region` is useful for noisy/anti-aliased UI.
  - `Most saturated pixel` may help when the region includes gradients.
5. Select your preferred language for color descriptions.
6. Click **Start Monitoring**.

## Notes

- For best results, select a small region around the color preview or swatch.
- If your UI theme adds borders/shadows, reduce region size to avoid those pixels.
- This is an approximation, not a color-calibrated scientific measurement.
