import cv2 
import mediapipe as mp 

#tracker class that uses mediapipe to detect hand landmarks and return them as coordinates
class Tracker: 
    def __init__(self): 
        self.mp_hands = mp.solutions.hands.Hands( 
                max_num_hands=1,
                min_detection_confidence=0.7,
                min_tracking_confidence=0.5
            )
    def process(self, frame):
        if frame is None: 
            return None
        else:
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB) 
            res = self.mp_hands.process(frame) 
            if res.multi_hand_landmarks: 
                return res.multi_hand_landmarks[0] 
            else:
                return None 