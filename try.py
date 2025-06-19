import cv2
import mediapipe as mp
import numpy as np
import random

# Mediapipe setup
mp_hands = mp.solutions.hands
hands = mp_hands.Hands(max_num_hands=1)
mp_drawing = mp.solutions.drawing_utils

# 3D Box boundary coordinates (simulated)
box_front = np.array([[400, 150], [500, 150], [500, 250], [400, 250]])
box_back = np.array([[420, 130], [520, 130], [520, 230], [420, 230]])

def draw_3d_box(img):
    cv2.polylines(img, [box_front], True, (255, 0, 0), 2)
    cv2.polylines(img, [box_back], True, (255, 0, 0), 2)
    for i in range(4):
        cv2.line(img, tuple(box_front[i]), tuple(box_back[i]), (255, 0, 0), 2)

def inside_box(x, y):
    return 400 <= x <= 500 and 150 <= y <= 250

def generate_question():
    # Randomly generate a simple addition or subtraction question
    op = random.choice(['+', '-'])
    a = random.randint(2, 10)
    b = random.randint(1, a if op == '-' else 10)
    answer = a + b if op == '+' else a - b
    question = f"{a} {op} {b} = ?"
    # Generate options (one correct, two random wrong)
    options = [answer]
    while len(options) < 3:
        wrong = answer + random.choice([-2, -1, 1, 2, 3])
        if wrong != answer and wrong > 0 and wrong not in options:
            options.append(wrong)
    random.shuffle(options)
    return question, options, answer

# Initial 2D block positions
def reset_blocks():
    return [(100 + i * 50, 400) for i in range(4)], [], [False] * 4

initial_blocks, moved_blocks, picked = reset_blocks()
question, options, answer = generate_question()
option_pos = [(100, 100), (250, 100), (100, 180)]

# Start camera
cap = cv2.VideoCapture(0)
solved = False

while True:
    ret, img = cap.read()
    if not ret:
        break
    img = cv2.flip(img, 1)
    h, w, _ = img.shape
    img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    results = hands.process(img_rgb)

    # Draw 2D question
    cv2.putText(img, question, (30, 50), cv2.FONT_HERSHEY_SIMPLEX, 1.2, (0, 0, 0), 2)
    for val, pos in zip(options, option_pos):
        cv2.circle(img, pos, 25, (255, 255, 255), -1)
        cv2.putText(img, str(val), (pos[0] - 10, pos[1] + 10), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 0), 2)

    draw_3d_box(img)

    # Draw remaining 2D blocks
    for i, (x, y) in enumerate(initial_blocks):
        if not picked[i]:
            cv2.rectangle(img, (x, y), (x + 30, y + 30), (0, 0, 255), -1)

    # Draw moved blocks in 3D box
    for (x, y) in moved_blocks:
        cv2.rectangle(img, (x, y), (x + 30, y + 30), (0, 255, 0), -1)

    if results.multi_hand_landmarks:
        for handLms in results.multi_hand_landmarks:
            ix = int(handLms.landmark[8].x * w)
            iy = int(handLms.landmark[8].y * h)
            cv2.circle(img, (ix, iy), 10, (0, 0, 255), -1)

            # Check if finger touched any 2D block
            for i, (bx, by) in enumerate(initial_blocks):
                if not picked[i] and bx < ix < bx + 30 and by < iy < by + 30:
                    picked[i] = True

            # If finger in 3D box and carrying a picked block
            if inside_box(ix, iy):
                for i in range(len(picked)):
                    if picked[i]:
                        moved_blocks.append((ix - 15, iy - 15))
                        picked[i] = False

            mp_drawing.draw_landmarks(img, handLms, mp_hands.HAND_CONNECTIONS)

    # Check for correct answer (number of moved blocks == correct answer)
    if len(moved_blocks) == answer:
        solved = True
        idx = options.index(answer)
        cv2.circle(img, option_pos[idx], 30, (0, 255, 0), 5)
        cv2.putText(img, "Correct! Press 'n' for next.", (180, 300), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 128, 0), 3)
    else:
        solved = False

    cv2.putText(img, "Press 'n' for next question", (10, 470), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (100, 100, 100), 2)
    cv2.imshow("Gesture Math Box", img)
    key = cv2.waitKey(1) & 0xFF
    if key == 27:  # ESC to quit
        break
    if key == ord('n'):
        # Next question: reset everything
        initial_blocks, moved_blocks, picked = reset_blocks()
        question, options, answer = generate_question()
        solved = False

cap.release()
cv2.destroyAllWindows()