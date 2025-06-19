import cv2
import mediapipe as mp
import numpy as np

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

# Initial 2D block positions
initial_blocks = [(100 + i * 50, 400) for i in range(4)]
moved_blocks = []
picked = [False] * 4

# Start camera
cap = cv2.VideoCapture(0)

while True:
    ret, img = cap.read()
    if not ret:
        break
    img = cv2.flip(img, 1)
    h, w, _ = img.shape
    img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    results = hands.process(img_rgb)

    # Draw 2D question
    cv2.putText(img, "Add   2 + 2 = ?", (30, 50), cv2.FONT_HERSHEY_SIMPLEX, 1.2, (0, 0, 0), 2)
    options = [5, 4, 6]
    option_pos = [(100, 100), (250, 100), (100, 180)]

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

    # Check for correct answer
    if len(moved_blocks) == 4:
        cv2.circle(img, option_pos[1], 30, (0, 255, 0), 5)
        cv2.putText(img, "Correct!", (250, 300), cv2.FONT_HERSHEY_SIMPLEX, 1.5, (0, 128, 0), 3)

    cv2.imshow("Gesture Math Box", img)
    if cv2.waitKey(1) & 0xFF == 27:
        break

cap.release()
cv2.destroyAllWindows()
