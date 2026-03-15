# 🖐️ Virtual Cursor using Hand Gestures

A **Python-based Virtual Cursor system** that allows users to control their computer mouse using **hand gestures through a webcam**.
This project uses **Computer Vision and Hand Tracking** to detect hand landmarks and convert gestures into mouse actions in real time.

The system eliminates the need for a physical mouse and enables **touchless human-computer interaction**.

---

# 🚀 Features

* Real-time **hand tracking**
* **Cursor movement** using hand motion
* **Left Click**
* **Right Click**
* **Double Click**
* **Drag and Drop**
* **Scroll Control**
* **Zoom In / Zoom Out**
* **Copy & Paste gestures**
* **Screenshot capture**
* **Adjustable cursor sensitivity**
* **Toggle system ON/OFF with keyboard shortcut**

---

# 🧠 Technologies Used

* **Python**
* **OpenCV (cv2)** – Webcam video processing
* **MediaPipe** – Hand landmark detection
* **PyAutoGUI** – Mouse and keyboard control
* **NumPy** – Numerical computations
* **Keyboard** – Hotkey detection
* **Threading** – Real-time performance
* **Logging** – Event tracking
* **Deque (collections)** – Gesture smoothing

---

# ⚙️ How It Works

1. The webcam captures video frames.
2. OpenCV processes the video stream.
3. MediaPipe detects **21 hand landmarks**.
4. Finger positions and distances are analyzed.
5. Specific **hand gestures trigger mouse actions**.
6. PyAutoGUI performs the corresponding system operations.

---

# 🖐️ Supported Gestures

| Gesture        | Action       |
| -------------- | ------------ |
| Move Hand      | Move Cursor  |
| Pinch Index    | Left Click   |
| Thumb Alone    | Right Click  |
| Double Pinch   | Double Click |
| Fist Hold      | Drag         |
| Two Fingers    | Scroll       |
| Open Palm      | Screenshot   |
| Thumb Up       | Copy         |
| Thumb Down     | Paste        |
| Pinch + Spread | Zoom         |

---

# 🖥️ Requirements

Install the required Python libraries:

```bash
pip install opencv-python mediapipe pyautogui numpy keyboard
```

---

# ▶️ How to Run

1. Clone the repository

```bash
git clone https://github.com/yourusername/hand-gesture-virtual-cursor.git
```

2. Navigate to the project folder

```bash
cd hand-gesture-virtual-cursor
```

3. Run the program

```bash
python hand_cursor.py
```

---

# ⌨️ Controls

| Key              | Function              |
| ---------------- | --------------------- |
| CTRL + SHIFT + H | Toggle Virtual Cursor |
| CTRL + SHIFT + S | Increase Sensitivity  |
| CTRL + SHIFT + F | Decrease Sensitivity  |
| Q                | Quit Application      |

---

# 🎯 Applications

* Touchless computer interaction
* Accessibility tools
* Smart interfaces
* Computer vision research
* Gesture-based control systems

---

# 📌 Future Improvements

* Multi-hand gesture support
* Gesture customization
* GUI control panel
* Mobile camera integration
* AI gesture learning

---

# 👨‍💻 Author

Developed by **Druva Kumar V**

---

# ⭐ Support

If you like this project, please **star the repository** ⭐ to support the work.
