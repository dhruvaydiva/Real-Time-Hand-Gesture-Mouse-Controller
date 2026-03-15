"""
Virtual Cursor Controller - Windows Edition (Full Gesture Suite)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

GESTURE MAP:
  ☝️  Index finger up + move        → Move cursor
  👌  Index + thumb PINCH           → Left Click
  🤙  Thumb finger alone           → Right Click
  ✌️  Quick double pinch            → Double Click
  ✊  FIST (close hand, hold)       → Drag & Drop (hold = drag, open = drop)
  ✌️  Two fingers up + swipe UP     → Scroll Up
  ✌️  Two fingers up + swipe DOWN   → Scroll Down
  ✌️  Two fingers up + swipe LEFT   → Scroll Left
  ✌️  Two fingers up + swipe RIGHT  → Scroll Right
  🖐️  Open palm (hold 1.5s)         → Screenshot
  👍  Thumbs Up                     → Copy  (Ctrl+C)
  👎  Thumbs Down                   → Paste (Ctrl+V)
  🤏  Pinch + move hands apart      → Zoom In  (Ctrl++)
  🤏  Pinch + move hands together   → Zoom Out (Ctrl+-)

HOTKEYS:
  Ctrl+Shift+H  → Toggle ON / OFF
  Ctrl+Shift+S  → Sensitivity UP   (+0.1)
  Ctrl+Shift+F  → Sensitivity DOWN (-0.1)

SYSTEM TRAY:
  Right-click tray icon → Toggle / Quit

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
"""

import cv2
import mediapipe as mp
import pyautogui
import numpy as np
import keyboard
import time
import sys
import logging
import threading
import subprocess
from collections import deque

# ── Try importing tray icon library ──────────────────────────────────────────
try:
    import pystray
    from pystray import MenuItem as TrayItem
    from PIL import Image, ImageDraw
    TRAY_AVAILABLE = True
except ImportError:
    TRAY_AVAILABLE = False
    print("[INFO] pystray/Pillow not installed — system tray disabled.")
    print("[INFO] Run:  pip install pystray pillow  to enable tray icon.")

# ─── Configuration ────────────────────────────────────────────────────────────
TOGGLE_HOTKEY       = "ctrl+shift+h"
SENS_UP_HOTKEY      = "ctrl+shift+s"
SENS_DOWN_HOTKEY    = "ctrl+shift+f"
CAMERA_INDEX        = 0
SMOOTHING_FRAMES    = 5
CLICK_THRESHOLD     = 0.045
CLICK_COOLDOWN      = 0.35
DOUBLE_CLICK_GAP    = 0.35     # max seconds between two pinches = double click
SCROLL_THRESHOLD    = 0.04     # min swipe distance to trigger scroll
SCROLL_COOLDOWN     = 0.12
ZOOM_THRESHOLD      = 0.06     # min spread/pinch distance change to trigger zoom
SCREENSHOT_HOLD     = 1.5      # seconds to hold open palm for screenshot
DRAG_THRESHOLD      = 0.5      # seconds holding fist before drag starts
MOVEMENT_SPEED      = 1.0
SHOW_WEBCAM_WINDOW  = True
OSD_DURATION        = 1.8      # seconds on-screen gesture label stays visible
# ─────────────────────────────────────────────────────────────────────────────

pyautogui.FAILSAFE = False
pyautogui.PAUSE    = 0

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s  %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)]
)
log = logging.getLogger(__name__)


# ══════════════════════════════════════════════════════════════════════════════
#  Helpers
# ══════════════════════════════════════════════════════════════════════════════

class SmoothCursor:
    def __init__(self, size=5):
        self.qx = deque(maxlen=size)
        self.qy = deque(maxlen=size)

    def update(self, x, y):
        self.qx.append(x)
        self.qy.append(y)
        return int(np.mean(self.qx)), int(np.mean(self.qy))


class OSDLabel:
    """On-Screen Display — shows gesture name on the webcam window."""
    def __init__(self):
        self.text      = ""
        self.expire_at = 0
        self.color     = (0, 255, 180)

    def show(self, text, color=(0, 255, 180)):
        self.text      = text
        self.color     = color
        self.expire_at = time.time() + OSD_DURATION

    def draw(self, frame):
        if time.time() < self.expire_at and self.text:
            fh, fw = frame.shape[:2]
            cv2.putText(frame, self.text,
                        (fw // 2 - len(self.text) * 9, fh // 2 + 10),
                        cv2.FONT_HERSHEY_DUPLEX, 1.0, (0, 0, 0), 4)
            cv2.putText(frame, self.text,
                        (fw // 2 - len(self.text) * 9, fh // 2 + 10),
                        cv2.FONT_HERSHEY_DUPLEX, 1.0, self.color, 2)


# ══════════════════════════════════════════════════════════════════════════════
#  Main Controller
# ══════════════════════════════════════════════════════════════════════════════

class VirtualCursor:
    def __init__(self):
        self.screen_w, self.screen_h = pyautogui.size()
        self.enabled        = True
        self.running        = False
        self.sensitivity    = MOVEMENT_SPEED
        self.smoother       = SmoothCursor(SMOOTHING_FRAMES)
        self.osd            = OSDLabel()

        # Click state
        self.last_click         = 0
        self.last_pinch_time    = 0
        self.was_left_pinch     = False
        self.was_right_pinch    = False
        self.pinch_count        = 0

        # Drag state
        self.fist_start_time    = 0
        self.is_dragging        = False
        self.was_fist           = False

        # Scroll state
        self.last_scroll        = 0
        self.prev_index_y       = None
        self.prev_index_x       = None

        # Screenshot state
        self.palm_start_time    = 0
        self.was_open_palm      = False
        self.screenshot_taken   = False

        # Zoom state
        self.prev_pinch_dist    = None
        self.last_zoom          = 0

        # Thumb gesture cooldown
        self.last_thumb_action  = 0

        # MediaPipe
        self.mp_hands  = mp.solutions.hands
        self.mp_draw   = mp.solutions.drawing_utils
        self.mp_styles = mp.solutions.drawing_styles
        self.detector  = self.mp_hands.Hands(
            static_image_mode=False,
            max_num_hands=1,
            min_detection_confidence=0.75,
            min_tracking_confidence=0.75,
        )

        # Hotkeys
        keyboard.add_hotkey(TOGGLE_HOTKEY,   self._toggle)
        keyboard.add_hotkey(SENS_UP_HOTKEY,  self._sens_up)
        keyboard.add_hotkey(SENS_DOWN_HOTKEY,self._sens_down)
        log.info(f"Hotkeys: {TOGGLE_HOTKEY.upper()} toggle | "
                 f"{SENS_UP_HOTKEY.upper()} sens+ | {SENS_DOWN_HOTKEY.upper()} sens-")

    # ── Hotkey callbacks ──────────────────────────────────────────────────────
    def _toggle(self):
        self.enabled = not self.enabled
        state = "ENABLED" if self.enabled else "DISABLED"
        log.info(f"Virtual Cursor {state}")
        self.osd.show(f"Cursor {state}", (0,255,100) if self.enabled else (80,80,255))

    def _sens_up(self):
        self.sensitivity = min(3.0, round(self.sensitivity + 0.1, 1))
        log.info(f"Sensitivity: {self.sensitivity}")
        self.osd.show(f"Sensitivity: {self.sensitivity:.1f}", (255, 220, 0))

    def _sens_down(self):
        self.sensitivity = max(0.3, round(self.sensitivity - 0.1, 1))
        log.info(f"Sensitivity: {self.sensitivity}")
        self.osd.show(f"Sensitivity: {self.sensitivity:.1f}", (255, 220, 0))

    # ── Landmark helpers ──────────────────────────────────────────────────────
    def _lm(self, results, idx):
        lm = results.multi_hand_landmarks[0].landmark
        return lm[idx].x, lm[idx].y

    def _dist(self, a, b):
        return np.hypot(a[0]-b[0], a[1]-b[1])

    def _fingers_up(self, results):
        """[thumb, index, middle, ring, pinky] True/False"""
        lm    = results.multi_hand_landmarks[0].landmark
        tips  = [4,  8,  12, 16, 20]
        bases = [3,  6,  10, 14, 18]
        up = [lm[tips[0]].x < lm[bases[0]].x]
        for i in range(1, 5):
            up.append(lm[tips[i]].y < lm[bases[i]].y)
        return up

    def _is_fist(self, fingers):
        return not any(fingers[1:])   # all four fingers down

    def _is_open_palm(self, fingers):
        return all(fingers[1:])       # all four fingers up

    def _is_thumbs_up(self, results, fingers):
        """Thumb up, all other fingers down."""
        if fingers[0] and not any(fingers[1:]):
            lm = results.multi_hand_landmarks[0].landmark
            return lm[4].y < lm[3].y   # thumb tip above base
        return False

    def _is_thumbs_down(self, results, fingers):
        """Thumb down, all other fingers down."""
        if not any(fingers[1:]):
            lm = results.multi_hand_landmarks[0].landmark
            return lm[4].y > lm[3].y   # thumb tip below base
        return False

    # ── Main run loop ─────────────────────────────────────────────────────────
    def run(self):
        cap = cv2.VideoCapture(CAMERA_INDEX, cv2.CAP_MSMF)
        if not cap.isOpened():
            cap = cv2.VideoCapture(CAMERA_INDEX)
        if not cap.isOpened():
            log.error("Cannot open webcam! Try changing CAMERA_INDEX.")
            return

        cap.set(cv2.CAP_PROP_FRAME_WIDTH,  640)
        cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
        cap.set(cv2.CAP_PROP_FPS,          30)
        time.sleep(1)
        for _ in range(5): cap.read()   # flush startup frames

        self.running = True
        log.info(f"Virtual Cursor RUNNING  |  Screen: {self.screen_w}x{self.screen_h}")
        log.info(f"Toggle: {TOGGLE_HOTKEY.upper()}  |  Sensitivity: Ctrl+Shift+S/F  |  Q=Quit")

        while self.running:
            ret, frame = cap.read()
            if not ret:
                time.sleep(0.03)
                continue

            frame   = cv2.flip(frame, 1)
            fh, fw  = frame.shape[:2]
            rgb     = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            results = self.detector.process(rgb)

            # ── Status bar ────────────────────────────────────────────────
            bar_color = (20, 110, 20) if self.enabled else (110, 20, 20)
            cv2.rectangle(frame, (0, 0), (fw, 40), bar_color, -1)
            status = "ACTIVE" if self.enabled else "PAUSED"
            cv2.putText(frame,
                f"{status}  |  {TOGGLE_HOTKEY.upper()} = Toggle  |  "
                f"Sensitivity: {self.sensitivity:.1f}  |  Q = Quit",
                (8, 27), cv2.FONT_HERSHEY_SIMPLEX, 0.50, (255,255,255), 1)

            # ── Gesture panel (right side) ────────────────────────────────
            panel_x = fw - 195
            cv2.rectangle(frame, (panel_x, 42), (fw, fh), (15,15,15), -1)
            gestures_info = [
                ("GESTURES", (180,180,180)),
                ("", None),
                ("Move hand    Cursor", (200,200,200)),
                ("Pinch idx    L-Click", (200,200,200)),
                ("Thumb alone  R-Click", (200,200,200)),
                ("2x Pinch     DblClick", (200,200,200)),
                ("Fist hold    Drag", (200,200,200)),
                ("2 fingers^  Scroll", (200,200,200)),
                ("Open palm    Shot", (200,200,200)),
                ("Thumb up     Copy", (200,200,200)),
                ("Thumb dn     Paste", (200,200,200)),
                ("Pinch+-      Zoom", (200,200,200)),
                ("", None),
                (f"Sens+: Ctrl+Shift+S", (160,160,100)),
                (f"Sens-:  Ctrl+Shift+F", (160,160,100)),
            ]
            for i, (txt, color) in enumerate(gestures_info):
                if txt and color:
                    cv2.putText(frame, txt, (panel_x + 6, 62 + i * 18),
                                cv2.FONT_HERSHEY_SIMPLEX, 0.38, color, 1)

            # ── Camera feed area ──────────────────────────────────────────
            cam_w = fw - 195

            if results.multi_hand_landmarks:
                self.mp_draw.draw_landmarks(
                    frame,
                    results.multi_hand_landmarks[0],
                    self.mp_hands.HAND_CONNECTIONS,
                    self.mp_styles.get_default_hand_landmarks_style(),
                    self.mp_styles.get_default_hand_connections_style(),
                )

                if self.enabled:
                    self._process_gestures(results, frame, fh, fw)

            else:
                self.prev_index_y    = None
                self.prev_index_x    = None
                self.prev_pinch_dist = None
                if self.is_dragging:
                    pyautogui.mouseUp()
                    self.is_dragging = False
                cv2.putText(frame, "No hand", (10, fh - 12),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.55, (100,100,220), 2)

            # ── OSD overlay ───────────────────────────────────────────────
            self.osd.draw(frame)

            if SHOW_WEBCAM_WINDOW:
                cv2.imshow("Virtual Cursor", frame)
                if cv2.waitKey(1) & 0xFF in (ord('q'), ord('Q'), 27):
                    break

        if self.is_dragging:
            pyautogui.mouseUp()
        cap.release()
        cv2.destroyAllWindows()
        self.running = False
        log.info("Virtual Cursor stopped.")

    # ══════════════════════════════════════════════════════════════════════════
    #  Gesture Processing
    # ══════════════════════════════════════════════════════════════════════════
    def _process_gestures(self, results, frame, fh, fw):
        fingers    = self._fingers_up(results)
        index_tip  = self._lm(results, 8)
        thumb_tip  = self._lm(results, 4)
        middle_tip = self._lm(results, 12)
        now        = time.time()

        # ── 1. CURSOR MOVEMENT (index finger up, not pinching) ────────────
        left_dist  = self._dist(index_tip, thumb_tip)
        is_pinching = left_dist < CLICK_THRESHOLD

        if fingers[1] and not self._is_fist(fingers):
            margin = 0.18
            nx = np.clip((index_tip[0] - margin) / (1 - 2 * margin), 0, 1)
            ny = np.clip((index_tip[1] - margin) / (1 - 2 * margin), 0, 1)
            tx = int(min(nx * self.screen_w  * self.sensitivity, self.screen_w  - 1))
            ty = int(min(ny * self.screen_h * self.sensitivity, self.screen_h - 1))
            sx, sy = self.smoother.update(tx, ty)
            if not self.is_dragging:
                pyautogui.moveTo(sx, sy)
            else:
                pyautogui.dragTo(sx, sy, button='left')

        # ── 2. LEFT CLICK (index + thumb pinch) ───────────────────────────
        if is_pinching and not self.was_left_pinch:
            if now - self.last_click > CLICK_COOLDOWN:
                # Check for double click
                if now - self.last_pinch_time < DOUBLE_CLICK_GAP:
                    pyautogui.doubleClick()
                    self.osd.show("Double Click", (255, 200, 0))
                    log.info("Double Click")
                    self.last_pinch_time = 0
                else:
                    pyautogui.click()
                    self.osd.show("Left Click", (0, 255, 200))
                    log.info("Left Click")
                    self.last_pinch_time = now
                self.last_click = now
        self.was_left_pinch = is_pinching

        # ── 3. RIGHT CLICK (thumb finger only — all other fingers down) ──────
        # Thumb up alone = right click (distinct from thumbs-up which needs
        # the thumb tip clearly above its base AND a 1s cooldown)
        is_thumb_only = (fingers[0] and not fingers[1] and not fingers[2]
                         and not fingers[3] and not fingers[4])
        if is_thumb_only and not self.was_right_pinch:
            if now - self.last_click > CLICK_COOLDOWN:
                pyautogui.rightClick()
                self.osd.show("Right Click", (255, 100, 100))
                log.info("Right Click")
                self.last_click = now
        self.was_right_pinch = is_thumb_only

        # ── 4. SCROLL (two fingers up + swipe) ────────────────────────────
        if fingers[1] and fingers[2] and not fingers[3] and not fingers[4]:
            cur_y = index_tip[1]
            cur_x = index_tip[0]

            if self.prev_index_y is not None and now - self.last_scroll > SCROLL_COOLDOWN:
                dy = self.prev_index_y - cur_y   # positive = moving up
                dx = cur_x - self.prev_index_x   # positive = moving right

                if abs(dy) > abs(dx):            # vertical scroll
                    if dy > SCROLL_THRESHOLD:
                        pyautogui.scroll(3)
                        self.osd.show("Scroll Up", (100, 220, 255))
                        self.last_scroll = now
                    elif dy < -SCROLL_THRESHOLD:
                        pyautogui.scroll(-3)
                        self.osd.show("Scroll Down", (100, 180, 255))
                        self.last_scroll = now
                else:                            # horizontal scroll
                    if dx > SCROLL_THRESHOLD:
                        pyautogui.hscroll(3)
                        self.osd.show("Scroll Right", (150, 200, 255))
                        self.last_scroll = now
                    elif dx < -SCROLL_THRESHOLD:
                        pyautogui.hscroll(-3)
                        self.osd.show("Scroll Left", (150, 200, 255))
                        self.last_scroll = now

            self.prev_index_y = cur_y
            self.prev_index_x = cur_x
        else:
            self.prev_index_y = None
            self.prev_index_x = None

        # ── 5. DRAG & DROP (fist) ─────────────────────────────────────────
        is_fist = self._is_fist(fingers)
        if is_fist:
            if not self.was_fist:
                self.fist_start_time = now
            elif now - self.fist_start_time > DRAG_THRESHOLD and not self.is_dragging:
                pyautogui.mouseDown(button='left')
                self.is_dragging = True
                self.osd.show("Dragging...", (255, 165, 0))
                log.info("Drag started")
        else:
            if self.is_dragging:
                pyautogui.mouseUp(button='left')
                self.is_dragging = False
                self.osd.show("Dropped", (255, 200, 100))
                log.info("Drop")
        self.was_fist = is_fist

        # ── 6. SCREENSHOT (open palm hold 1.5s) ───────────────────────────
        is_open = self._is_open_palm(fingers)
        if is_open:
            if not self.was_open_palm:
                self.palm_start_time   = now
                self.screenshot_taken  = False
            elif (not self.screenshot_taken and
                  now - self.palm_start_time > SCREENSHOT_HOLD):
                screenshot_path = f"screenshot_{int(now)}.png"
                img = pyautogui.screenshot()
                img.save(screenshot_path)
                self.screenshot_taken = True
                self.osd.show("Screenshot Saved!", (50, 255, 50))
                log.info(f"Screenshot saved: {screenshot_path}")
        self.was_open_palm = is_open

        # ── 7. COPY (thumbs up) ───────────────────────────────────────────
        if self._is_thumbs_up(results, fingers):
            if now - self.last_thumb_action > 1.0:
                pyautogui.hotkey('ctrl', 'c')
                self.osd.show("Copied!", (100, 255, 100))
                log.info("Copy (Ctrl+C)")
                self.last_thumb_action = now

        # ── 8. PASTE (thumbs down) ────────────────────────────────────────
        if self._is_thumbs_down(results, fingers):
            if now - self.last_thumb_action > 1.0:
                pyautogui.hotkey('ctrl', 'v')
                self.osd.show("Pasted!", (100, 200, 255))
                log.info("Paste (Ctrl+V)")
                self.last_thumb_action = now

        # ── 9. ZOOM IN / OUT (pinch spread/close with index+thumb) ────────
        if fingers[0] and fingers[1] and not fingers[2] and not fingers[3] and not fingers[4]:
            cur_dist = self._dist(index_tip, thumb_tip)
            if self.prev_pinch_dist is not None and now - self.last_zoom > 0.2:
                delta = cur_dist - self.prev_pinch_dist
                if delta > ZOOM_THRESHOLD:
                    pyautogui.hotkey('ctrl', '+')
                    self.osd.show("Zoom In", (255, 255, 100))
                    log.info("Zoom In")
                    self.last_zoom = now
                elif delta < -ZOOM_THRESHOLD:
                    pyautogui.hotkey('ctrl', '-')
                    self.osd.show("Zoom Out", (200, 255, 200))
                    log.info("Zoom Out")
                    self.last_zoom = now
            self.prev_pinch_dist = cur_dist
        else:
            self.prev_pinch_dist = None

        # ── Fingertip dot ─────────────────────────────────────────────────
        ix = int(index_tip[0] * fw)
        iy = int(index_tip[1] * fh)
        dot_col = (0, 255, 255) if is_pinching else (255, 255, 0)
        cv2.circle(frame, (ix, iy), 10, dot_col, -1)

        # ── Drag indicator ────────────────────────────────────────────────
        if self.is_dragging:
            cv2.rectangle(frame, (2, 42), (180, 68), (0, 100, 200), -1)
            cv2.putText(frame, "DRAGGING - Open fist to drop",
                        (6, 61), cv2.FONT_HERSHEY_SIMPLEX, 0.42, (255,255,255), 1)


# ══════════════════════════════════════════════════════════════════════════════
#  System Tray
# ══════════════════════════════════════════════════════════════════════════════

def _make_tray_icon(color=(0, 200, 100)):
    """Create a small coloured circle image for the tray."""
    img  = Image.new("RGBA", (64, 64), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    draw.ellipse([8, 8, 56, 56], fill=color + (255,))
    draw.ellipse([20, 20, 44, 44], fill=(255, 255, 255, 200))
    return img


def start_tray(controller):
    if not TRAY_AVAILABLE:
        return

    def on_toggle(icon, item):
        controller._toggle()
        icon.icon = _make_tray_icon((0,200,100) if controller.enabled else (200,60,60))
        icon.title = f"Virtual Cursor  ({'ON' if controller.enabled else 'OFF'})"

    def on_quit(icon, item):
        controller.running = False
        icon.stop()

    icon = pystray.Icon(
        "VirtualCursor",
        _make_tray_icon(),
        "Virtual Cursor (ON)",
        menu=pystray.Menu(
            TrayItem("Toggle ON / OFF", on_toggle, default=True),
            TrayItem("Quit",            on_quit),
        )
    )
    threading.Thread(target=icon.run, daemon=True).start()
    log.info("System tray icon started.")
    return icon


# ══════════════════════════════════════════════════════════════════════════════
#  Entry Point
# ══════════════════════════════════════════════════════════════════════════════

def main():
    print("=" * 60)
    print("   VIRTUAL CURSOR  —  Full Gesture Suite  (Windows)")
    print("=" * 60)
    print()
    print("  GESTURE            ACTION")
    print("  ─────────────────────────────────────────────")
    print("  Index finger up  → Move cursor")
    print("  Pinch idx+thumb  → Left Click")
    print("  Quick 2x pinch   → Double Click")
    print("  Thumb finger alone   → Right Click")
    print("  Fist (hold)      → Drag & Drop")
    print("  2 fingers swipe  → Scroll Up/Down/Left/Right")
    print("  Open palm 1.5s   → Screenshot")
    print("  Thumbs Up        → Copy  (Ctrl+C)")
    print("  Thumbs Down      → Paste (Ctrl+V)")
    print("  Pinch spread     → Zoom In  (Ctrl++)")
    print("  Pinch close      → Zoom Out (Ctrl+-)")
    print()
    print("  HOTKEYS")
    print("  ─────────────────────────────────────────────")
    print(f"  {TOGGLE_HOTKEY.upper():<22} Toggle ON / OFF")
    print(f"  {SENS_UP_HOTKEY.upper():<22} Sensitivity UP (+0.1)")
    print(f"  {SENS_DOWN_HOTKEY.upper():<22} Sensitivity DOWN (-0.1)")
    print("=" * 60)
    print()

    vc = VirtualCursor()
    start_tray(vc)

    try:
        vc.run()
    except KeyboardInterrupt:
        log.info("Stopped by user.")
    finally:
        vc.running = False


if __name__ == "__main__":
    main()