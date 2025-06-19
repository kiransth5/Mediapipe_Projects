import cv2
import mediapipe as mp
import numpy as np
import random

# Set desired window size
WINDOW_WIDTH, WINDOW_HEIGHT = 1020, 920

# Mediapipe setup
mp_hands = mp.solutions.hands
hands = mp_hands.Hands(max_num_hands=1)
mp_drawing = mp.solutions.drawing_utils

# 3D Box boundary coordinates (simulated)
box_front = np.array([[600, 250], [800, 250], [800, 450], [600, 450]])
box_back = np.array([[630, 220], [830, 220], [830, 420], [630, 420]])

def draw_3d_box(img):
    cv2.polylines(img, [box_front], True, (255, 0, 0), 2)
    cv2.polylines(img, [box_back], True, (255, 0, 0), 2)
    for i in range(4):
        cv2.line(img, tuple(box_front[i]), tuple(box_back[i]), (255, 0, 0), 2)


def inside_box(x, y):
    return 600 <= x <= 800 and 250 <= y <= 450

def generate_question():
    op = random.choice(['+', '-','*', '/'])
    a = random.randint(2, 10)
    b = random.randint(1, a if op == '-' else 10)
    if op == '+':
        answer = a + b
    elif op == '-':
        answer = a - b
    elif op == '*': 
        answer = a * b
    else:
        answer = a // b
           
    
    
    
    question = f"{a} {op} {b} = ?"
    options = [answer]
    while len(options) < 3:
        wrong = answer + random.choice([-2, -1, 1, 2, 3])
        if wrong != answer and wrong > 0 and wrong not in options:
            options.append(wrong)
    random.shuffle(options)
    return question, options, answer

def reset_blocks():
    return [(150 + i * 70, 600) for i in range(4)], [], [False] * 4

initial_blocks, moved_blocks, picked = reset_blocks()
question, options, answer = generate_question()
option_pos = [(150, 150), (350, 150), (150, 250)]

# Next button coordinates (bigger and on the right)
btn_x1, btn_y1, btn_x2, btn_y2 = 750, 600, 900, 670

cap = cv2.VideoCapture(0)
cap.set(cv2.CAP_PROP_FRAME_WIDTH, WINDOW_WIDTH)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, WINDOW_HEIGHT)
solved = False
next_gesture_active = False

cv2.namedWindow("Gesture Math Box", cv2.WINDOW_NORMAL)
cv2.resizeWindow("Gesture Math Box", WINDOW_WIDTH, WINDOW_HEIGHT)

while True:
    ret, img = cap.read()
    if not ret:
        break
    img = cv2.flip(img, 1)
    img = cv2.resize(img, (WINDOW_WIDTH, WINDOW_HEIGHT))
    h, w, _ = img.shape
    img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    results = hands.process(img_rgb)

    # Draw 2D question and options
    cv2.putText(img, question, (30, 80), cv2.FONT_HERSHEY_SIMPLEX, 2, (0, 0, 0), 3)
    for val, pos in zip(options, option_pos):
        cv2.circle(img, pos, 40, (255, 255, 255), -1)
        cv2.putText(img, str(val), (pos[0] - 20, pos[1] + 20), cv2.FONT_HERSHEY_SIMPLEX, 2, (0, 0, 0), 3)

    draw_3d_box(img)

    # Draw remaining 2D blocks
    for i, (x, y) in enumerate(initial_blocks):
        if not picked[i]:
            cv2.rectangle(img, (x, y), (x + 50, y + 50), (0, 0, 255), -1)

    # Draw moved blocks in 3D box
    for (x, y) in moved_blocks:
        cv2.rectangle(img, (x, y), (x + 50, y + 50), (0, 255, 0), -1)

    next_gesture_active = False

    if results.multi_hand_landmarks:
        for handLms in results.multi_hand_landmarks:
            ix = int(handLms.landmark[8].x * w)
            iy = int(handLms.landmark[8].y * h)
            cv2.circle(img, (ix, iy), 15, (0, 0, 255), -1)

            # Check if finger touched any 2D block
            for i, (bx, by) in enumerate(initial_blocks):
                if not picked[i] and bx < ix < bx + 50 and by < iy < by + 50:
                    picked[i] = True

            # If finger in 3D box and carrying a picked block
            if inside_box(ix, iy):
                for i in range(len(picked)):
                    if picked[i]:
                        moved_blocks.append((ix - 25, iy - 25))
                        picked[i] = False

            # Check if finger is inside the Next button
            if btn_x1 <= ix <= btn_x2 and btn_y1 <= iy <= btn_y2:
                next_gesture_active = True
                cv2.rectangle(img, (btn_x1, btn_y1), (btn_x2, btn_y2), (0, 255, 0), 5)
            mp_drawing.draw_landmarks(img, handLms, mp_hands.HAND_CONNECTIONS)

    # Check for correct answer (number of moved blocks == correct answer)
    if len(moved_blocks) == answer:
        solved = True
        idx = options.index(answer)
        cv2.circle(img, option_pos[idx], 45, (0, 255, 0), 7)
        cv2.putText(img, "Correct! Use hand to click Next.", (200, 500), cv2.FONT_HERSHEY_SIMPLEX, 1.5, (0, 128, 0), 3)
    else:
        solved = False

    # Draw the Next button
    cv2.rectangle(img, (btn_x1, btn_y1), (btn_x2, btn_y2), (0, 128, 255), -1)
    cv2.putText(img, "Next", (btn_x1 + 30, btn_y1 + 50), cv2.FONT_HERSHEY_SIMPLEX, 2, (255, 255, 255), 4)

    cv2.imshow("Gesture Math Box", img)
    key = cv2.waitKey(1) & 0xFF
    if key == 27:  # ESC to quit
        break
    if next_gesture_active:
        initial_blocks, moved_blocks, picked = reset_blocks()
        question, options, answer = generate_question()
        solved = False
        # Wait a bit to avoid multiple triggers
        cv2.waitKey(500)

cap.release()
cv2.destroyAllWindows()