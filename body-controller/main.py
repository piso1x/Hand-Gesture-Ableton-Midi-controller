import cv2
import mido
import math
import mediapipe as mp
from tracker import Tracker
from mapper import map_range
from midi_controller import MidiController

#init webcam+tracker
cap = cv2.VideoCapture(0) 
if not cap.isOpened():
    print("Errore: impossibile aprire la webcam")
    exit()
tracker = Tracker() 
midi_controller = MidiController()
while True:
    res, frame = cap.read()
    if res:     
        landmarkPoints = tracker.process(frame)
        if landmarkPoints:
            #draw landmarks on the frame
            mp.solutions.drawing_utils.draw_landmarks(frame, landmarkPoints, mp.solutions.hands.HAND_CONNECTIONS)
            cv2.imshow("Webcam", frame)
            #extract coordinates
            thumb = landmarkPoints.landmark[4]
            index = landmarkPoints.landmark[8]
            distance = math.sqrt((thumb.x-index.x)**2 + (thumb.y-index.y)**2)
            #maps distance to 0-127 midi acceptable values
            midiValue = map_range(distance, 0.05, 0.25, 0, 127)
            print(midiValue)
            midi_controller.send_cc(1, midiValue) #sends midivalue to ableton
        if cv2.waitKey(1) & 0xFF == ord('q'): #while cicle stop if q is pressed
            break
cap.release()
midi_controller.close()