import cv2
import mediapipe as mp
import math
import time

mp_hands = mp.solutions.hands
hands = mp_hands.Hands(max_num_hands=1, min_detection_confidence=0.7)
mp_draw = mp.solutions.drawing_utils

cap = cv2.VideoCapture(0)
cap.set(3, 1280)
cap.set(4, 720)

buttons = [["7", "8", "9", "/"],
           ["4", "5", "6", "*"],
           ["1", "2", "3", "-"],
           ["0", "C", "=", "+"]]

expression = ""
pinch_threshold = 40
last_click_time = 0

screen_width = int(cap.get(3))
screen_height = int(cap.get(4))
button_width = screen_width // 6
button_height = screen_height // 7

button_positions = []
for i in range(len(buttons)):
    for j in range(len(buttons[i])):
        x = button_width * j + button_width // 2
        y = button_height * i + button_height // 2
        button_positions.append((x, y, buttons[i][j]))

def draw_transparent_button(img, center_x, center_y, text, alpha=0.5):
    overlay = img.copy()
    color = (0, 0, 255) 
    cv2.rectangle(overlay, (center_x - button_width // 2, center_y - button_height // 2),
                  (center_x + button_width // 2, center_y + button_height // 2),
                  color, -1)
    img[:] = cv2.addWeighted(overlay, alpha, img, 1 - alpha, 0)
    cv2.putText(img, text, (center_x - button_width // 4, center_y + button_height // 6),
                cv2.FONT_HERSHEY_SIMPLEX, 2, (255, 255, 255), 5)

while True:
    ret, frame = cap.read()
    if not ret:
        break
    frame = cv2.flip(frame, 1)

    for pos in button_positions:
        x, y, text = pos
        draw_transparent_button(frame, x, y, text)

    cv2.rectangle(frame, (50, screen_height - 150), (screen_width - 50, screen_height - 50), (0, 0, 0), -1)
    cv2.putText(frame, expression, (60, screen_height - 80), cv2.FONT_HERSHEY_SIMPLEX, 2, (255, 255, 255), 5)

    rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    results = hands.process(rgb_frame)

    if results.multi_hand_landmarks:
        for hand_landmarks in results.multi_hand_landmarks:
            mp_draw.draw_landmarks(frame, hand_landmarks, mp_hands.HAND_CONNECTIONS)
            lm_list = [(int(lm.x * screen_width), int(lm.y * screen_height)) for lm in hand_landmarks.landmark]
            x1, y1 = lm_list[4]
            x2, y2 = lm_list[8]
            cv2.line(frame, (x1, y1), (x2, y2), (255, 0, 255), 5)
            distance = math.hypot(x2 - x1, y2 - y1)
            if distance < pinch_threshold:
                current_time = time.time()
                if current_time - last_click_time > 1:
                    pinch_point = ((x1 + x2) // 2, (y1 + y2) // 2)
                    cv2.circle(frame, pinch_point, 30, (0, 255, 0), -1)
                    for pos in button_positions:
                        x, y, text = pos
                        if (x - button_width // 2 < pinch_point[0] < x + button_width // 2 and
                            y - button_height // 2 < pinch_point[1] < y + button_height // 2):
                            if text == "C":
                                expression = ""
                            elif text == "=":
                                if expression != "":
                                    try:
                                        expression = str(eval(expression))
                                    except:
                                        expression = "Error"
                            else:
                                expression += text
                            last_click_time = current_time

    cv2.imshow("Gesture Calculator", frame)
    if cv2.waitKey(1) & 0xFF == 27:
        break

cap.release()
cv2.destroyAllWindows()
