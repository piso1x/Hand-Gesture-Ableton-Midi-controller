
def smoother(cc_num, current_val, alpha, smoothed_values):
    smoothed_values[cc_num] = alpha * current_val + (1 - alpha) * smoothed_values[cc_num]
    return int(round(smoothed_values[cc_num]))

def send_if_moved(cc_num, current_val, last_midi_values, threshold, midi_controller, active_cc):
    if active_cc == 0 or active_cc == cc_num:
        if abs(current_val - last_midi_values[cc_num]) > threshold:
            midi_controller.send_cc(cc_num, current_val)
            last_midi_values[cc_num] = current_val
            
def convert_to_coordinates(landmark, frame):
    height, width = frame.shape[:2]
    return (int(landmark.x * width), int(landmark.y * height))