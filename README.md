# Hand Gesture Ableton MIDI Controller

A real-time hand-gesture MIDI controller built with OpenCV + MediaPipe + Mido.

The app tracks up to two hands from webcam video, converts finger distances into MIDI CC values, and sends those values to a virtual MIDI output port that can be mapped in Ableton Live (or any DAW that supports MIDI CC).

## Features

- Real-time hand tracking (up to 2 hands)
- Gesture-to-MIDI conversion (0–127 CC range)
- Smoothing to reduce jitter
- Threshold/noise gate to avoid flooding MIDI messages
- Keyboard-driven map/play modes
- On-screen CC labels and mode overlays
- Virtual MIDI output port for DAW integration

## Project Structure

- `main.py`: main app loop (camera capture, tracking, gesture processing, UI overlay, mode handling)
- `tracker.py`: MediaPipe hand tracking wrapper
- `mapper.py`: generic range mapper (`map_range`)
- `midi_controller.py`: virtual MIDI output class (Mido backend)
- `utilities.py`: helper functions for smoothing, distance computation, drawing, MIDI send logic, key handling

## Requirements

- Python 3.10+ (required because the code uses `match/case`)
- macOS (or Windows/Linux with equivalent MIDI setup)
- Webcam
- Ableton Live (or any DAW that receives MIDI CC)

Python packages:

- `opencv-python`
- `mediapipe`
- `mido`
- `python-rtmidi`

## Installation

From the `body-controller` folder:

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install --upgrade pip
pip install opencv-python mediapipe mido python-rtmidi
```

## Run

```bash
source .venv/bin/activate
python main.py
```

When running, the app creates a virtual MIDI port named:

- `Python Hand Gestures`

## Ableton Setup (macOS)

### 1) Enable a MIDI bridge (IAC Driver)

1. Open **Audio MIDI Setup**.
2. Go to **Window → Show MIDI Studio**.
3. Double-click **IAC Driver**.
4. Enable **Device is online**.

### 2) Route MIDI in Ableton

1. Open **Ableton Live → Preferences → Link/Tempo/MIDI**.
2. In **MIDI Ports**, enable **Track** and **Remote** for the input receiving your virtual port/IAC route.
3. Arm a MIDI track and map CC controls as needed.

> Depending on your MIDI routing setup, you may route from the app’s virtual port to IAC, or directly consume the virtual port if your DAW exposes it.

## Controls

Keyboard controls while the OpenCV window is active:

- `q`: quit
- `0`: Play Mode (all mapped CC pass through)
- `1`–`8`: Map Mode for a specific CC channel

A mode banner is displayed on screen for ~3 seconds after switching mode.

## How It Works

1. **Capture frame** from webcam (`cv2.VideoCapture`).
2. **Track hands** with MediaPipe (`tracker.py`).
3. **Split detections** by handedness (Right / Left).
4. **Extract key landmarks**: thumb, index, middle, ring, pinky, palm.
5. **Compute distances** between thumb and other fingers.
6. **Map distances → MIDI** using `map_range(..., 0.05..0.25 -> 0..127)`.
7. **Smooth values** via exponential smoothing:
   - `smoothed = alpha * current + (1 - alpha) * previous`
8. **Noise gate**: send MIDI only if value changed more than threshold.
9. **Render overlays** (CC labels + current mode) and show frame.

## Important Parameters

In `main.py`:

- `alpha = 0.2`: smoothing factor
- threshold in `send_midi_messages(..., 5, ...)`: min CC delta before sending
- overlay duration in `handle_mode_key(..., overlay_duration=3.0)`

In `tracker.py`:

- `max_num_hands=2`
- `min_detection_confidence=0.7`
- `min_tracking_confidence=0.5`

## Current Gesture Mapping Logic

- Distances used: thumb-index, thumb-middle, thumb-ring, thumb-pinky
- Each distance produces one CC value (4 values per hand pipeline)
- Values are clamped to 0–127

## Troubleshooting

### No webcam / black window

- Confirm camera permissions for terminal/IDE.
- Check that no other app is locking the webcam.

### No MIDI received in Ableton

- Verify virtual port appears in DAW.
- Confirm MIDI preferences have the correct input enabled.
- Ensure track is armed and mapped.

### Jittery or unstable CC values

- Increase smoothing (`alpha` lower/higher depending desired response).
- Increase noise gate threshold.
- Improve lighting and keep hand in stable tracking area.

### Left/Right hand seems swapped

- Webcam mirroring can make handedness appear inverted visually.
- If needed, swap routing logic for Right/Left assignment in `main.py`.

### `KeyError` on MIDI dictionaries

- Ensure CC keys used in send/smoothing functions match dictionary keys.
- Keep right/left CC index conventions consistent across `main.py` and `utilities.py`.

## Development Notes

- Keep `main.py` focused on orchestration.
- Put reusable logic in `utilities.py` (already done for mode handling).
- If adding new gestures, extend the distance extraction + mapping pipeline first, then expose as additional CC channels.

## License

This project is licensed under the MIT License.
