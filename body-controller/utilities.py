import cv2

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