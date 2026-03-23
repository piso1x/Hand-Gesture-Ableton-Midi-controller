import cv2
import mido
import math
import mediapipe as mp
from tracker import Tracker
from mapper import map_range
from midi_controller import MidiController
from utilities import smoother, send_if_moved, convert_to_coordinates, draw_shadowed_label, store_coordinates, calculate_distance, distances_to_midi_values, draw_labels, send_midi_messages, handle_mode_key
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
alpha = 0.1

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
MIRROR_VIEW = True

while True:
    res, frame = cap.read()
    if res:
        #starts processing the frame and extracting hand landmarks
        if MIRROR_VIEW:
            frame = cv2.flip(frame, 1)
        detections = tracker.process(frame)
        right_landmarks = None
        left_landmarks = None
        
        #draw landmarks and separate right and left hand
        for hand_landmarks, handedness in detections:
            label = handedness.classification[0].label
            if not MIRROR_VIEW:
                label = "Left" if label == "Right" else "Right"
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
            #calculate_distance(right_hand_coordinates, right_distances_palm)
            distances_to_midi_values(right_distances, smoothed_values, alpha, right_midi_values)

            draw_labels(frame, right_midi_values, right_hand_coordinates, cc_start=1)

            send_midi_messages(right_midi_values, last_midi_values, 5, midi_controller, active_cc, 1)
        
        #left hand processing
        if left_landmarks:
            store_coordinates(left_landmarks, left_hand_coordinates)
            calculate_distance(left_hand_coordinates, left_distances)
            #calculate_distance(left_hand_coordinates, left_distances_palm)
            distances_to_midi_values(left_distances, smoothed_values, alpha, left_midi_values)

            draw_labels(frame, left_midi_values, left_hand_coordinates, cc_start=5)

            send_midi_messages(left_midi_values, last_left_midi_values, 5, midi_controller, active_cc, 5)

        # Keyboard input for mode switching -> easier for mapping different pinches
        key = cv2.waitKey(1) & 0xFF 
        active_cc, overlay_text, overlay_until, should_quit = handle_mode_key(key, active_cc, overlay_text, overlay_until)
        if should_quit:
            break
        
        # Draw overlay text if needed
        if time.perf_counter() < overlay_until:
            draw_shadowed_label(frame, overlay_text, (frame.shape[1]//2-30, 40))

        cv2.imshow("Webcam", frame)
cap.release()
midi_controller.close()