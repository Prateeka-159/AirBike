import cv2
import mediapipe as mp
import numpy as np

mp_hands = mp.solutions.hands
mp_pose = mp.solutions.pose
mp_draw = mp.solutions.drawing_utils

hands = mp_hands.Hands(max_num_hands=2, min_detection_confidence=0.7)
pose = mp_pose.Pose(min_detection_confidence=0.7)

cap = cv2.VideoCapture(0)

# HAND CLOSED / OPEN DETECTION 
def is_fist(hand_landmarks):
    tips = [8, 12, 16, 20]      # fingertip landmarks
    folded = 0

    for tip in tips:
        tip_y = hand_landmarks.landmark[tip].y
        pip_y = hand_landmarks.landmark[tip - 2].y
        if tip_y > pip_y:
            folded += 1

    return folded >= 3

# MAIN LOOP
while True:
    ret, frame = cap.read()
    if not ret:
        break

    frame = cv2.flip(frame, 1)
    h, w, _ = frame.shape
    rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

    hand_results = hands.process(rgb)
    pose_results = pose.process(rgb)

    gas = False
    brake = False
    lane = "CENTER"

    # HAND DETECTION
    if hand_results.multi_hand_landmarks:
        for hand_landmarks, handedness in zip(
            hand_results.multi_hand_landmarks,
            hand_results.multi_handedness):

            label = handedness.classification[0].label
            fist = is_fist(hand_landmarks)

            if label == "Right" and fist:
                gas = True
            if label == "Left" and fist:
                brake = True

            mp_draw.draw_landmarks(frame, hand_landmarks, mp_hands.HAND_CONNECTIONS)

    # BODY LEAN DETECTION
    if pose_results.pose_landmarks:
        landmarks = pose_results.pose_landmarks.landmark

        left_shoulder = landmarks[11]
        right_shoulder = landmarks[12]

        shoulder_center_x = int((left_shoulder.x + right_shoulder.x) / 2 * w)
        frame_center_x = w // 2

        lean = shoulder_center_x - frame_center_x

        if lean > 40:
            lane = "RIGHT"
        elif lean < -40:
            lane = "LEFT"
        else:
            lane = "CENTER"

        mp_draw.draw_landmarks(frame, pose_results.pose_landmarks, mp_pose.POSE_CONNECTIONS)

    # DISPLAY INFO 
    cv2.putText(frame, f"GAS: {gas}", (10, 40),
                cv2.FONT_HERSHEY_SIMPLEX, 1, (0,255,0), 2)

    cv2.putText(frame, f"BRAKE: {brake}", (10, 80),
                cv2.FONT_HERSHEY_SIMPLEX, 1, (0,0,255), 2)

    cv2.putText(frame, f"LANE: {lane}", (10, 120),
                cv2.FONT_HERSHEY_SIMPLEX, 1, (255,0,0), 2)

    cv2.imshow("AirBike Controller", frame)

    if cv2.waitKey(1) & 0xFF == 27:
        break

cap.release()
cv2.destroyAllWindows()
