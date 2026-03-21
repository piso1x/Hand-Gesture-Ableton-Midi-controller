import cv2
import math
import mediapipe as mp
from tracker import Tracker
from mapper import map_range

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
    
def store_coordinates(landmarkPoints, right_hand_coordinates):
    thumb = landmarkPoints.landmark[4]
    index = landmarkPoints.landmark[8]
    middle = landmarkPoints.landmark[12]
    ring = landmarkPoints.landmark[16]
    pinky = landmarkPoints.landmark[20]
    palm = landmarkPoints.landmark[0]

    right_hand_coordinates.clear()
    right_hand_coordinates.extend([thumb, index, middle, ring, pinky, palm])
    
def calculate_distance(right_hand_coordinates, right_distances):
    distance_thumb_index = math.sqrt((right_hand_coordinates[0].x-right_hand_coordinates[1].x)**2 + (right_hand_coordinates[0].y-right_hand_coordinates[1].y)**2)
    distance_thumb_middle = math.sqrt((right_hand_coordinates[0].x-right_hand_coordinates[2].x)**2 + (right_hand_coordinates[0].y-right_hand_coordinates[2].y)**2)
    distance_thumb_ring = math.sqrt((right_hand_coordinates[0].x-right_hand_coordinates[3].x)**2 + (right_hand_coordinates[0].y-right_hand_coordinates[3].y)**2)
    distance_thumb_pinky = math.sqrt((right_hand_coordinates[0].x-right_hand_coordinates[4].x)**2 + (right_hand_coordinates[0].y-right_hand_coordinates[4].y)**2)

    right_distances.clear()
    right_distances.extend([distance_thumb_index, distance_thumb_middle, distance_thumb_ring, distance_thumb_pinky])
    
def distances_to_midi_values(right_distances, smoothed_values, alpha, right_midi_values):
    midiValue_thumb_index = smoother(1, map_range(right_distances[0], 0.05, 0.25, 0, 127), alpha, smoothed_values)
    midiValue_thumb_middle = smoother(2, map_range(right_distances[1], 0.05, 0.25, 0, 127), alpha, smoothed_values)
    midiValue_thumb_ring = smoother(3, map_range(right_distances[2], 0.05, 0.25, 0, 127), alpha, smoothed_values)
    midiValue_thumb_pinky = smoother(4, map_range(right_distances[3], 0.05, 0.25, 0, 127), alpha, smoothed_values)

    right_midi_values.clear()
    right_midi_values.extend([midiValue_thumb_index, midiValue_thumb_middle, midiValue_thumb_ring, midiValue_thumb_pinky])