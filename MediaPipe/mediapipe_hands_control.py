import cv2
import mediapipe as mp
import serial
import math
import time

# Initialize MediaPipe Hands and Serial Communication
mp_hands = mp.solutions.hands
hands = mp_hands.Hands(min_detection_confidence=0.7, min_tracking_confidence=0.7)
mp_drawing = mp.solutions.drawing_utils

try:
    arduino = serial.Serial(port='COM3', baudrate=9600, timeout=1)  # Increased timeout
    print("Connected to Arduino")
except serial.SerialException as e:
    print(f"Error: Could not connect to Arduino on COM3 - {e}")
    exit()

cap = cv2.VideoCapture(0) # Open webcam
if not cap.isOpened():
    print("Error: Cannot access the webcam.")
    exit()

# Initial Values
brightness = 128
base_motor_angle = 90  
head_motor_angle = 90  
arm_motor_angle = 90 
smooth_step = 5  

# Threshold Settings
light_low_threshold = 0.05
light_high_threshold = 0.30
fist_left_threshold = 0.2
fist_right_threshold = 0.8
head_up_threshold = 0.3
head_down_threshold = 0.8
arm_up_threshold = 0.3
arm_down_threshold = 0.8

previous_command = ""  # Track the last command

while cap.isOpened():
    success, frame = cap.read()
    if not success:
        print("Error: Cannot read from webcam.")
        break

    #selfie view
    frame = cv2.flip(frame, 1)
    frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    results = hands.process(frame_rgb)

    # Check if any gesture is detected
    active_control = None  # Track which control is active
    if results.multi_hand_landmarks:
        for hand_landmarks in results.multi_hand_landmarks:
            # Draw hand landmarks on the image
            mp_drawing.draw_landmarks(frame, hand_landmarks, mp_hands.HAND_CONNECTIONS)

            # 1. Light Dimming (Thumb and Pinky Spread with Thresholds)
            thumb_tip = hand_landmarks.landmark[4]
            pinky_tip = hand_landmarks.landmark[20]
            spread_distance = math.sqrt((thumb_tip.x - pinky_tip.x)**2 + (thumb_tip.y - pinky_tip.y)**2)

            if spread_distance < light_low_threshold:
                brightness = max(0, brightness - 6)
                active_control = "light"

            elif spread_distance > light_high_threshold:
                brightness = min(255, brightness + 6)
                active_control = "light"

            # 2. Base Motor Control (Fist in Left/Right Regions)
            fingers_curled = []
            for i in [8, 12, 16, 20]:  # Index, Middle, Ring, Pinky tips
                tip_y = hand_landmarks.landmark[i].y
                base_y = hand_landmarks.landmark[i - 2].y
                fingers_curled.append(tip_y > base_y)

            if all(fingers_curled):  # Fist detected
                wrist_x = hand_landmarks.landmark[0].x  # X-coordinate of the wrist

                if wrist_x < fist_left_threshold:
                    base_motor_angle = max(0, base_motor_angle - smooth_step)
                    active_control = "base"

                elif wrist_x > fist_right_threshold:
                    base_motor_angle = min(180, base_motor_angle + smooth_step)
                    active_control = "base"

            # 3. Head Motor Control (Open Palm Orientation)
            wrist_y = hand_landmarks.landmark[0].y  #y-coordinate of the wrist
            palm_center_y = hand_landmarks.landmark[9].y  #y-coordinate of the palm center

            if wrist_y < head_up_threshold:  # Wrist higher than palm center
                head_motor_angle = max(0, head_motor_angle - smooth_step)
                active_control = "head" 

            elif wrist_y > head_down_threshold:  # Wrist lower than palm center
                head_motor_angle = min(180, head_motor_angle + smooth_step)
                active_control = "head"

            # 4. Arm Motor Control (Fist Gesture in Position)
            if all(fingers_curled): 
                if wrist_y < arm_up_threshold:
                    arm_motor_angle = max(0, arm_motor_angle - smooth_step)
                    active_control = "arm"

                elif wrist_y > arm_down_threshold:
                    arm_motor_angle = min(180, arm_motor_angle + smooth_step)
                    active_control = "arm"

            # Send the active command only
            if active_control:
                try:
                    # Only send the relevant command
                    if active_control == "light":
                        combined_command = f"L{brightness}\n"
                    elif active_control == "base":
                        combined_command = f"B{base_motor_angle}\n"
                    elif active_control == "head":
                        combined_command = f"H{head_motor_angle}\n"
                    elif active_control == "arm":
                        combined_command = f"A{arm_motor_angle}\n"

                    if combined_command != previous_command:
                        arduino.write(combined_command.encode())
                        print(f"Sent Command: {combined_command.strip()}")
                        previous_command = combined_command
                    time.sleep(0.005)  # Reduced delay for faster updates
                except Exception as e:
                    print(f"Error sending command: {e}")

    # Display the image
    cv2.imshow("MediaPipe Hands", frame)
    if cv2.waitKey(1) & 0xFF == ord('q'):  # Press 'q' to quit
        break

cap.release()
cv2.destroyAllWindows()
arduino.close()