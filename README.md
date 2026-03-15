# Virtual Cursor Controller — Windows Edition

Control your laptop cursor entirely with **hand gestures** via your webcam.

---

## File Structure

```
virtual_cursor/
  hand_cursor.py          <- Main Python script
  requirements.txt        <- Python packages list
  install.bat             <- Double-click to install packages
  start.bat               <- Double-click to run manually
  startup_silent.vbs      <- Drop into Startup folder for auto-start at login
  README.md               <- This file
  .vscode/
    launch.json           <- VS Code Run config (press F5)
```

---

## Step 1 — Install

Double-click **`install.bat`**

Or run manually in terminal:
```
pip install -r requirements.txt
```

---

## Step 2 — Run in VS Code

1. Open the `virtual_cursor` folder in VS Code
2. Press **F5**
3. Select **"Run Virtual Cursor"**

Or double-click **`start.bat`** to run without VS Code.

---

## Step 3 — Auto-Start on Windows Login

1. Press **Win + R**, type `shell:startup`, press **Enter**
2. Copy **`startup_silent.vbs`** into that folder
3. Done — Virtual Cursor will silently start every time you log in

**To disable auto-start:**
- Go back to `shell:startup` and delete `startup_silent.vbs`

---

## Gestures

| Gesture | Action |
|---|---|
| Index finger up | Move cursor |
| Thumb + index pinch | Left click |
| Thumb + middle pinch | Right click |
| Fist or open palm | Freeze cursor |
| **Ctrl + Shift + H** | Toggle ON / OFF |

> Keep your hand 30–60 cm from the webcam for best results.

---

## Configuration

Open `hand_cursor.py` and edit the top section:

| Setting | Default | What it does |
|---|---|---|
| `TOGGLE_HOTKEY` | `ctrl+shift+h` | Your toggle hotkey |
| `CAMERA_INDEX` | `0` | Webcam number (try 1 if 0 fails) |
| `SMOOTHING_FRAMES` | `5` | Cursor smoothness (3=fast, 8=smooth) |
| `CLICK_THRESHOLD` | `0.04` | How tight the pinch needs to be |
| `CLICK_COOLDOWN` | `0.4` | Min seconds between clicks |
| `MOVEMENT_SPEED` | `1.0` | Cursor speed multiplier |
| `SHOW_WEBCAM_WINDOW` | `True` | Show or hide webcam preview |

---

## How to Stop

| Method | How |
|---|---|
| Hotkey | Press `Ctrl + Shift + H` to pause/resume |
| Webcam window | Press `Q` or `Esc` |
| VS Code | Click the red square Stop button |
| Terminal | Press `Ctrl + C` |

---

## Troubleshooting

**Webcam not opening**
→ Change `CAMERA_INDEX = 1` or `= 2` in `hand_cursor.py`

**Cursor too fast / slow**
→ Adjust `MOVEMENT_SPEED` (0.5 = slower, 2.0 = faster)

**Accidental clicks**
→ Increase `CLICK_THRESHOLD` to `0.06`

**Hotkey not working**
→ Run VS Code or `start.bat` as Administrator

**startup_silent.vbs not launching at startup**
→ Make sure Python is added to Windows PATH
→ Or change `pythonExe` in the .vbs file to the full Python path
