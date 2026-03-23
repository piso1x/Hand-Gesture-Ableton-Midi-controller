import cv2
import math
import mediapipe as mp
from tracker import Tracker
from mapper import map_range
import time

#smooths the midi values to avoid sudden jumps and create a more natural control experience
def smoother(cc_num, current_val, alpha, smoothed_values):
    smoothed_values[cc_num] = alpha * current_val + (1 - alpha) * smoothed_values[cc_num] 
    return int(round(smoothed_values[cc_num]))

#sends midi message only if the value has changed more than a certain threshold to avoid sending too many messages and saturating the midi receiver
def send_if_moved(cc_num, current_val, last_midi_values, threshold, midi_controller, active_cc):
    if active_cc == 0 or active_cc == cc_num:
        if abs(current_val - last_midi_values[cc_num]) > threshold:
            midi_controller.send_cc(cc_num, current_val)
            last_midi_values[cc_num] = current_val
            
#convert normalized landmark coordinates to pixel coordinates based on frame dimensions to draw labels on the frame         
def convert_to_coordinates(landmark, frame):
    height, width = frame.shape[:2]
    return (int(landmark.x * width), int(landmark.y * height))

#draws a label with a shadow for better visibility
def draw_shadowed_label(frame, text, anchor):
    font = cv2.FONT_HERSHEY_SIMPLEX
    font_scale = 1
    thickness = 2
    padding = 8
    shadow_offset = 3

    text_width, text_height = cv2.getTextSize(text, font, font_scale, thickness)[0]
    x, y = anchor

    top_left = (x - padding, y - text_height - padding)
    bottom_right = (x + text_width + padding, y + padding)

    shadow_top_left = (top_left[0] + shadow_offset, top_left[1] + shadow_offset)
    shadow_bottom_right = (bottom_right[0] + shadow_offset, bottom_right[1] + shadow_offset)

    cv2.rectangle(frame, shadow_top_left, shadow_bottom_right, (40, 40, 40), -1)
    cv2.rectangle(frame, top_left, bottom_right, (0, 0, 0), -1)
    cv2.putText(frame, text, (x, y), font, font_scale, (255, 255, 255), thickness)
    
def store_coordinates(landmark_points, right_hand_coordinates):
    thumb = landmark_points.landmark[4]
    index = landmark_points.landmark[8]
    middle = landmark_points.landmark[12]
    ring = landmark_points.landmark[16]
    pinky = landmark_points.landmark[20]
    palm = landmark_points.landmark[0]

    right_hand_coordinates.clear()
    right_hand_coordinates.extend([thumb, index, middle, ring, pinky, palm])
    
def calculate_distance(right_hand_coordinates, right_distances):
    right_distances.clear()
    thumb = right_hand_coordinates[0]
    for finger in right_hand_coordinates[1:5]:
        distance = math.sqrt((thumb.x - finger.x) ** 2 + (thumb.y - finger.y) ** 2)
        right_distances.append(distance)
    
def distances_to_midi_values(right_distances, smoothed_values, alpha, right_midi_values):
    right_midi_values.clear()
    for cc_num, distance in enumerate(right_distances, start=1):
        midi_value = smoother(cc_num, map_range(distance, 0.05, 0.25, 0, 127), alpha, smoothed_values)
        right_midi_values.append(midi_value)
    
def draw_labels(frame, right_midi_values, hand_coordinates, cc_start=1):
    for cc_num, (midi_value, coordinate) in enumerate(zip(right_midi_values, hand_coordinates[1:]), start=cc_start):
        draw_shadowed_label(frame, f"CC{cc_num}: {midi_value}", convert_to_coordinates(coordinate, frame))
    
def send_midi_messages(midi_values, last_midi_values, threshold, midi_controller, active_cc, cc_start):    
    for cc_num, midi_value in enumerate(midi_values, start=cc_start):
        send_if_moved(cc_num, midi_value, last_midi_values, threshold, midi_controller, active_cc)

def handle_mode_key(key, active_cc, overlay_text, overlay_until, overlay_duration=3.0):
    match key:
        case value if value == ord('q'):
            return active_cc, overlay_text, overlay_until, True
        case value if value == ord('0'):
            active_cc = 0
            overlay_text = "---> PLAY MODE <---"
            overlay_until = time.perf_counter() + overlay_duration
            print("\n---> PLAY MODE <---")
        case value if value in (ord('1'), ord('2'), ord('3'), ord('4'), ord('5'), ord('6'), ord('7'), ord('8')):
            active_cc = int(chr(value))
            overlay_text = f"---> MAP MODE (CC{active_cc}) <---"
            overlay_until = time.perf_counter() + overlay_duration
            print(f"\n{overlay_text}")
    return active_cc, overlay_text, overlay_until, False