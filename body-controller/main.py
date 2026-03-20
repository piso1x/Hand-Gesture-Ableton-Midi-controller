import cv2
import mido
import math
import mediapipe as mp
from tracker import Tracker
from mapper import map_range
from midi_controller import MidiController
from utilities import smoother, send_if_moved, convert_to_coordinates

#init webcam+tracker
cap = cv2.VideoCapture(0) 
if not cap.isOpened():
    print("Errore: impossibile aprire la webcam")
    exit()
tracker = Tracker() 
midi_controller = MidiController()

last_midi_values = {1: -10, 2: -10, 3: -10, 4: -10}
active_cc = 0
smoothed_values = {1: 0, 2: 0, 3: 0, 4: 0}
alpha = 0.2

while True:
    res, frame = cap.read()
    if res:     
        landmarkPoints = tracker.process(frame)
        if landmarkPoints:

            #draw landmarks on the frame
            mp.solutions.drawing_utils.draw_landmarks(frame, landmarkPoints, mp.solutions.hands.HAND_CONNECTIONS)
            
            #extract coordinates
            thumb = landmarkPoints.landmark[4]
            index = landmarkPoints.landmark[8]
            middle = landmarkPoints.landmark[12]
            ring = landmarkPoints.landmark[16]
            pinky = landmarkPoints.landmark[20]
            palm = landmarkPoints.landmark[0]

            #calculating distances for pinces
            distance_thumb_index = math.sqrt((thumb.x-index.x)**2 + (thumb.y-index.y)**2)
            distance_thumb_middle = math.sqrt((thumb.x-middle.x)**2 + (thumb.y-middle.y)**2)
            distance_thumb_ring = math.sqrt((thumb.x-ring.x)**2 + (thumb.y-ring.y)**2)
            distance_thumb_pinky = math.sqrt((thumb.x-pinky.x)**2 + (thumb.y-pinky.y)**2)

            #calculating distances for full open hand
            distance_palm_index = math.sqrt((palm.x-index.x)**2 + (palm.y-index.y)**2)
            distance_palm_middle = math.sqrt((palm.x-middle.x)**2 + (palm.y-middle.y)**2)
            distance_palm_ring = math.sqrt((palm.x-ring.x)**2 + (palm.y-ring.y)**2)
            distance_palm_pinky = math.sqrt((palm.x-pinky.x)**2 + (palm.y-pinky.y)**2)
            distance_palm_thumb = math.sqrt((palm.x-thumb.x)**2 + (palm.y-thumb.y)**2)

            #maps distance to 0-127 midi acceptable values
            midiValue_thumb_index = smoother(1, map_range(distance_thumb_index, 0.05, 0.25, 0, 127), 0.2, smoothed_values)
            midiValue_thumb_middle = smoother(2, map_range(distance_thumb_middle, 0.05, 0.25, 0, 127), 0.2, smoothed_values)
            midiValue_thumb_ring = smoother(3, map_range(distance_thumb_ring, 0.05, 0.25, 0, 127), 0.2, smoothed_values)
            midiValue_thumb_pinky = smoother(4, map_range(distance_thumb_pinky, 0.05, 0.25, 0, 127), 0.2, smoothed_values)

            #draws midi values on the frame for debugging
            #crea oggetto punto  passagli punto
            cv2.putText(frame, f"CC1: {midiValue_thumb_index}", convert_to_coordinates(index, frame), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 0, 0), 2)
            cv2.putText(frame, f"CC2: {midiValue_thumb_middle}", convert_to_coordinates(middle, frame), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 0, 0), 2)
            cv2.putText(frame, f"CC3: {midiValue_thumb_ring}", convert_to_coordinates(ring, frame), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 0, 0), 2)
            cv2.putText(frame, f"CC4: {midiValue_thumb_pinky}", convert_to_coordinates(pinky, frame), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 0, 0), 2)
            
            cv2.imshow("Webcam", frame)
            
            # Noise gate fun
            send_if_moved(1, midiValue_thumb_index, last_midi_values, 5, midi_controller, active_cc)
            send_if_moved(2, midiValue_thumb_middle, last_midi_values, 5, midi_controller, active_cc)
            send_if_moved(3, midiValue_thumb_ring, last_midi_values, 5, midi_controller, active_cc)
            send_if_moved(4, midiValue_thumb_pinky, last_midi_values, 5, midi_controller, active_cc)

        # Keyboard input for mode switching -> easier for mapping different pinches
        
        key = cv2.waitKey(1) & 0xFF
        if key == ord('q'): 
            break
        elif key == ord('1'): 
            active_cc = 1; print("\n---> MAP MODE (CC1) <---")
        elif key == ord('2'): 
            active_cc = 2; print("\n---> MAP MODE (CC2) <---")
        elif key == ord('3'): 
            active_cc = 3; print("\n---> MAP MODE (CC3) <---")
        elif key == ord('4'): 
            active_cc = 4; print("\n---> MAP MODE (CC4) <---")
        elif key == ord('0'): 
            active_cc = 0; print("\n---> PLAY MODE <---")
cap.release()
midi_controller.close()