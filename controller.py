import cv2
import mediapipe as mp

class CVController:
    def __init__(self):
        self.cap = cv2.VideoCapture(0)

        self.mp_hands = mp.solutions.hands
        self.mp_pose = mp.solutions.pose
        self.mp_draw = mp.solutions.drawing_utils

        self.hands = self.mp_hands.Hands(max_num_hands=2, min_detection_confidence=0.7)
        self.pose = self.mp_pose.Pose(min_detection_confidence=0.7)

        self.gas = False
        self.brake = False
        self.lane = "CENTER"

    def is_fist(self, hand_landmarks):
        tips = [8, 12, 16, 20]
        folded = 0

        for tip in tips:
            tip_y = hand_landmarks.landmark[tip].y
            pip_y = hand_landmarks.landmark[tip - 2].y
            if tip_y > pip_y:
                folded += 1

        return folded >= 3

    def update(self):
        ret, frame = self.cap.read()
        if not ret:
            return self.gas, self.brake, self.lane

        frame = cv2.flip(frame, 1)
        h, w, _ = frame.shape
        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

        hand_results = self.hands.process(rgb)
        pose_results = self.pose.process(rgb)

        self.gas = False
        self.brake = False
        self.lane = "CENTER"

        # HANDS → gas & brake
        if hand_results.multi_hand_landmarks:
            for hand_landmarks, handedness in zip(
                hand_results.multi_hand_landmarks,
                hand_results.multi_handedness):

                label = handedness.classification[0].label
                fist = self.is_fist(hand_landmarks)

                if label == "Right" and fist:
                    self.gas = True
                if label == "Left" and fist:
                    self.brake = True

        # POSE → lane change
        if pose_results.pose_landmarks:
            landmarks = pose_results.pose_landmarks.landmark
            left_shoulder = landmarks[11]
            right_shoulder = landmarks[12]

            shoulder_center_x = int((left_shoulder.x + right_shoulder.x) / 2 * w)
            frame_center_x = w // 2
            lean = shoulder_center_x - frame_center_x

            if lean > 40:
                self.lane = "RIGHT"
            elif lean < -40:
                self.lane = "LEFT"
            else:
                self.lane = "CENTER"

        return self.gas, self.brake, self.lane
