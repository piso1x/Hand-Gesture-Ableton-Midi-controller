import cv2
import mido
import math
import mediapipe as mp
from tracker import Tracker
from mapper import map_range
from midi_controller import MidiController
from utilities import smoother, send_if_moved, convert_to_coordinates, draw_shadowed_label, store_coordinates, calculate_distance, distances_to_midi_values
import time

#init webcam+tracker
cap = cv2.VideoCapture(0) 
if not cap.isOpened():
    print("Errore: impossibile aprire la webcam")
    exit()
tracker = Tracker() 
midi_controller = MidiController()

last_midi_values = {1: -10, 2: -10, 3: -10, 4: -10}
last_left_midi_values = {5: -10, 6: -10, 7: -10, 8: -10}
active_cc = 0
smoothed_values = {1: 0, 2: 0, 3: 0, 4: 0}
smoothed_left_values = {1: 0, 2: 0, 3: 0, 4: 0}
alpha = 0.2

right_hand_coordinates = [] #stores coordinates of right hand fingertips and palm
right_distances = [] #stores distances between thumb and other fingers for pinch detection
right_distances_palm = [] #stores distances between palm and fingers for open hand detection
right_midi_values = [] #stores midi values for open hand detection

left_hand_coordinates = [] #stores coordinates of left hand fingertips and palm
left_distances = [] #stores distances between thumb and other fingers for pinch detection
left_distances_palm = [] #stores distances between palm and fingers for open hand detection
left_midi_values = [] #stores midi values for open hand detection

overlay_text = ""
overlay_until = 0.0

while True:
    res, frame = cap.read()
    if res:
        detections = tracker.process(frame)
        right_landmarks = None
        left_landmarks = None
        
        #draw landmarks and separate right and left hand
        for hand_landmarks, handedness in detections:
            label = handedness.classification[0].label
            mp.solutions.drawing_utils.draw_landmarks(frame, hand_landmarks, mp.solutions.hands.HAND_CONNECTIONS,
                mp.solutions.drawing_utils.DrawingSpec(color=(0,255,0), thickness=5, circle_radius=5),
                mp.solutions.drawing_utils.DrawingSpec(color=(255,0,0), thickness=2)
            )
            if label == "Right":
                right_landmarks = hand_landmarks
            elif label == "Left":
                left_landmarks = hand_landmarks

        #right hand processing
        if right_landmarks:
            store_coordinates(right_landmarks, right_hand_coordinates)
            calculate_distance(right_hand_coordinates, right_distances)
            calculate_distance(right_hand_coordinates, right_distances_palm)
            distances_to_midi_values(right_distances, smoothed_values, alpha, right_midi_values)

            draw_shadowed_label(frame, f"CC1: {right_midi_values[0]}", convert_to_coordinates(right_hand_coordinates[1], frame))
            draw_shadowed_label(frame, f"CC2: {right_midi_values[1]}", convert_to_coordinates(right_hand_coordinates[2], frame))
            draw_shadowed_label(frame, f"CC3: {right_midi_values[2]}", convert_to_coordinates(right_hand_coordinates[3], frame))
            draw_shadowed_label(frame, f"CC4: {right_midi_values[3]}", convert_to_coordinates(right_hand_coordinates[4], frame))

            send_if_moved(1, right_midi_values[0], last_midi_values, 5, midi_controller, active_cc)
            send_if_moved(2, right_midi_values[1], last_midi_values, 5, midi_controller, active_cc)
            send_if_moved(3, right_midi_values[2], last_midi_values, 5, midi_controller, active_cc)
            send_if_moved(4, right_midi_values[3], last_midi_values, 5, midi_controller, active_cc)
        
        #left hand processing
        if left_landmarks:
            store_coordinates(left_landmarks, left_hand_coordinates)
            calculate_distance(left_hand_coordinates, left_distances)
            calculate_distance(left_hand_coordinates, left_distances_palm)
            distances_to_midi_values(left_distances, smoothed_left_values, alpha, left_midi_values)

            draw_shadowed_label(frame, f"CC5: {left_midi_values[0]}", convert_to_coordinates(left_hand_coordinates[1], frame))
            draw_shadowed_label(frame, f"CC6: {left_midi_values[1]}", convert_to_coordinates(left_hand_coordinates[2], frame))
            draw_shadowed_label(frame, f"CC7: {left_midi_values[2]}", convert_to_coordinates(left_hand_coordinates[3], frame))
            draw_shadowed_label(frame, f"CC8: {left_midi_values[3]}", convert_to_coordinates(left_hand_coordinates[4], frame))

            send_if_moved(5, left_midi_values[0], last_left_midi_values, 5, midi_controller, active_cc)
            send_if_moved(6, left_midi_values[1], last_left_midi_values, 5, midi_controller, active_cc)
            send_if_moved(7, left_midi_values[2], last_left_midi_values, 5, midi_controller, active_cc)
            send_if_moved(8, left_midi_values[3], last_left_midi_values, 5, midi_controller, active_cc)

        # Keyboard input for mode switching -> easier for mapping different pinches
        key = cv2.waitKey(1) & 0xFF 
        match key:
            case value if value == ord('q'):
                break
            case value if value == ord('1'):
                active_cc = 1
                overlay_text = "---> MAP MODE (CC1) <---"
                overlay_until = time.perf_counter() + 3.0
                print("\n---> MAP MODE (CC1) <---")
            case value if value == ord('2'):
                active_cc = 2
                overlay_text = "---> MAP MODE (CC2) <---"
                overlay_until = time.perf_counter() + 3.0
                print("\n---> MAP MODE (CC2) <---")
            case value if value == ord('3'):
                active_cc = 3
                overlay_text = "---> MAP MODE (CC3) <---"
                overlay_until = time.perf_counter() + 3.0
                print("\n---> MAP MODE (CC3) <---")
            case value if value == ord('4'):
                active_cc = 4
                overlay_text = "---> MAP MODE (CC4) <---"
                overlay_until = time.perf_counter() + 3.0
                print("\n---> MAP MODE (CC4) <---")
            case value if value == ord('0'):
                active_cc = 0
                overlay_text = "---> PLAY MODE <---"
                overlay_until = time.perf_counter() + 3.0
                print("\n---> PLAY MODE <---")
            case value if value == ord('5'):
                active_cc = 5
                overlay_text = "---> MAP MODE (CC5) <---"
                overlay_until = time.perf_counter() + 3.0
                print("\n---> MAP MODE (CC5) <---")
            case value if value == ord('6'):
                active_cc = 6
                overlay_text = "---> MAP MODE (CC6) <---"
                overlay_until = time.perf_counter() + 3.0
                print("\n---> MAP MODE (CC6) <---")
            case value if value == ord('7'):
                active_cc = 7
                overlay_text = "---> MAP MODE (CC7) <---"
                overlay_until = time.perf_counter() + 3.0
                print("\n---> MAP MODE (CC7) <---")
            case value if value == ord('8'):
                active_cc = 8
                overlay_text = "---> MAP MODE (CC8) <---"
                overlay_until = time.perf_counter() + 3.0
                print("\n---> MAP MODE (CC8) <---")
            
        if time.perf_counter() < overlay_until:
            draw_shadowed_label(frame, overlay_text, (frame.shape[1]//2-30, 40))

        cv2.imshow("Webcam", frame)
cap.release()
midi_controller.close()