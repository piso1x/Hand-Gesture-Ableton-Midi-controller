import cv2 #input webcam
import mediapipe as mp #hand tracking

class Tracker: 
    def __init__(self): 
        self.mp_hands = mp.solutions.hands.Hands( #init model
                max_num_hands=1,
                min_detection_confidence=0.7,
                min_tracking_confidence=0.5
            )
    def process(self, frame):
        if frame is None: #webcam check
            return None
        else:
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB) #color format conversion
            res = self.mp_hands.process(frame) 
            if res.multi_hand_landmarks: #hand detected
                return res.multi_hand_landmarks[0] #return hand landmarks
            else:
                return None #no hand detected