# import cv2
# import mediapipe as mp
# import numpy as np
# import random
# import pyttsx3
# # screen size: 1000x700
# WINDOW_WIDTH, WINDOW_HEIGHT = 1200, 900

# # Initialize mediapipe and text-to-speech
# mp_hands = mp.solutions.hands
# mp_drawing = mp.solutions.drawing_utils
# hands = mp_hands.Hands(max_num_hands=1)
# engine = pyttsx3.init()

# def speak(text):
#     engine.say(text)
#     engine.runAndWait()

# def is_inside(rect, point):
#     x, y, w, h = rect
#     return x < point[0] < x + w and y < point[1] < y + h

# # Attractive 3D block with shadow and gradient
# def draw_3d_box(img, center, number, color=(100, 200, 255), shadow=True, highlight=True):
#     x, y = center
#     # Shadow
#     if shadow:
#         overlay = img.copy()
#         cv2.rectangle(overlay, (x-45, y-35), (x+45, y+45), (50, 50, 50), -1)
#         alpha = 0.3
#         cv2.addWeighted(overlay, alpha, img, 1 - alpha, 0, img)
#     # Main box with gradient
#     for i in range(80):
#         c = (
#             int(color[0] + (255-color[0]) * i/80),
#             int(color[1] + (255-color[1]) * i/80),
#             int(color[2] + (255-color[2]) * i/80)
#         )
#         cv2.rectangle(img, (x-40+i, y-40+i), (x+40-i, y+40-i), c, 1)
#     # Border
#     cv2.rectangle(img, (x-40, y-40), (x+40, y+40), (0, 0, 0), 3)
#     # 3D top
#     pts = np.array([[x-40, y-40], [x-30, y-55], [x+30, y-55], [x+40, y-40]], np.int32)
#     cv2.fillPoly(img, [pts], (min(color[0]+40,255), min(color[1]+40,255), min(color[2]+40,255)))
#     cv2.polylines(img, [pts], isClosed=True, color=(0,0,0), thickness=2)
#     # Highlight
#     if highlight:
#         cv2.line(img, (x-40, y-40), (x-30, y-55), (255,255,255), 2)
#         cv2.line(img, (x+40, y-40), (x+30, y-55), (255,255,255), 2)
#     # Number
#     cv2.putText(img, str(number), (x-22, y+18), cv2.FONT_HERSHEY_DUPLEX, 1.7, (0,0,0), 4)
#     cv2.putText(img, str(number), (x-22, y+18), cv2.FONT_HERSHEY_DUPLEX, 1.7, (255,255,255), 2)

# def draw_button(img, text, pos, color=(200, 200, 200)):
#     x, y = pos
#     cv2.rectangle(img, (x, y), (x+120, y+60), color, -1)
#     cv2.rectangle(img, (x, y), (x+120, y+60), (0, 0, 0), 2)
#     cv2.putText(img, text, (x+10, y+40), cv2.FONT_HERSHEY_SIMPLEX, 1, (0,0,0), 2)
#     return (x, y, 120, 60)

# def generate_question():
#     random_values = random.sample(range(1, 21), 4)
#     return random_values, sorted(random_values)

# cap = cv2.VideoCapture(0)
# WINDOW_WIDTH, WINDOW_HEIGHT = 1000, 700

# question, correct_order = generate_question()
# selected = []
# dragging = False
# drag_index = None
# drag_offset = (0, 0)
# drag_value = None
# speak("Arrange the numbers in ascending order")

# start_positions = [(150 + i * 180, 120) for i in range(4)]
# place_positions = [(150 + i * 180, 350) for i in range(4)]

# while cap.isOpened():
#     ret, frame = cap.read()
#     if not ret:
#         break
#     frame = cv2.flip(frame, 1)
#     frame = cv2.resize(frame, (WINDOW_WIDTH, WINDOW_HEIGHT))
#     h, w, _ = frame.shape
#     rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
#     results = hands.process(rgb)
#     finger = None

#     cv2.putText(frame, "Arrange the numbers in ascending order!", (80, 60), cv2.FONT_HERSHEY_SIMPLEX, 1.2, (0,0,255), 3)

#     if results.multi_hand_landmarks:
#         for hand_landmarks in results.multi_hand_landmarks:
#             lm = hand_landmarks.landmark[8]
#             finger = int(lm.x * w), int(lm.y * h)
#             mp_drawing.draw_landmarks(frame, hand_landmarks, mp_hands.HAND_CONNECTIONS)

#     # Draw current number blocks (not selected)
#     for i, val in enumerate(question):
#         if val not in selected or (dragging and drag_index == i):
#             draw_3d_box(frame, start_positions[i], val)

#     # Draw user selected blocks
#     for i, val in enumerate(selected):
#         draw_3d_box(frame, place_positions[i], val, (100, 255, 100))

#     # Draw buttons
#     del_btn = draw_button(frame, "DEL", (50, 600))
#     sub_btn = draw_button(frame, "SUBMIT", (200, 600), (180, 255, 180))
#     next_btn = draw_button(frame, "NEXT", (400, 600), (180, 180, 255))
#     quit_btn = draw_button(frame, "QUIT", (600,600), (255, 180, 180))

#     # Drag and drop logic
#     if finger:
#         fx, fy = finger

#         if not dragging:
#             # Start dragging if finger is on a block
#             for i, (x, y) in enumerate(start_positions):
#                 if is_inside((x-40, y-40, 80, 80), finger):
#                     if question[i] not in selected and len(selected) < 4:
#                         dragging = True
#                         drag_index = i
#                         drag_value = question[i]
#                         drag_offset = (fx - x, fy - y)
#                         break
#         else:
#             # If dragging, show block at finger
#             draw_3d_box(frame, (fx - drag_offset[0], fy - drag_offset[1]), drag_value, (255, 200, 100), shadow=False, highlight=True)
#             # Drop block if finger is over place_positions
#             for i, (px, py) in enumerate(place_positions):
#                 if is_inside((px-40, py-40, 80, 80), finger):
#                     if drag_value not in selected and len(selected) < 4:
#                         selected.append(drag_value)
#                         speak(f"Added {drag_value}")
#                         dragging = False
#                         drag_index = None
#                         drag_value = None
#                         break
#             # Cancel drag if finger is over DEL
#             if is_inside(del_btn, finger):
#                 dragging = False
#                 drag_index = None
#                 drag_value = None
#                 speak("Cancelled")
#         # Button actions (only if not dragging)
#         if not dragging:
#             # Delete last
#             if is_inside(del_btn, finger) and selected:
#                 removed = selected.pop()
#                 speak(f"Removed {removed}")
#             # Submit check
#             if is_inside(sub_btn, finger):
#                 if selected == correct_order:
#                     speak("Congratulations, answer is correct!")
#                 else:
#                     speak("Try again")
#             # Next question
#             if is_inside(next_btn, finger):
#                 question, correct_order = generate_question()
#                 selected = []
#                 speak("Next. Arrange the numbers in ascending order")
#             # Quit button
#             if is_inside(quit_btn, finger):
#                 speak("Exiting the game")
#                 break

#     else:
#         # If finger not detected, stop dragging
#         dragging = False
#         drag_index = None
#         drag_value = None

#     cv2.imshow("Ascending Order Puzzle", frame)
#     if cv2.waitKey(1) & 0xFF == 27:  # ESC to quit
#         break

# cap.release()
# cv2.destroyAllWindows()
import cv2
import mediapipe as mp
import numpy as np
import random
import pyttsx3

# screen size: 1200x900
WINDOW_WIDTH, WINDOW_HEIGHT = 1200, 900

# Initialize mediapipe and text-to-speech
mp_hands = mp.solutions.hands
mp_drawing = mp.solutions.drawing_utils
hands = mp_hands.Hands(max_num_hands=1)
engine = pyttsx3.init()

def speak(text):
    engine.say(text)
    engine.runAndWait()

def is_inside(rect, point):
    x, y, w, h = rect
    return x < point[0] < x + w and y < point[1] < y + h

# Attractive 3D block with shadow and gradient and filled border
def draw_3d_box(img, center, number, color=(100, 200, 255), shadow=True, highlight=True):
    x, y = center
    border_thickness = 8  # Thickness of the border

    # Shadow
    if shadow:
        overlay = img.copy()
        cv2.rectangle(overlay, (x-45, y-35), (x+45, y+45), (50, 50, 50), -1)
        alpha = 0.3
        cv2.addWeighted(overlay, alpha, img, 1 - alpha, 0, img)

    # Draw filled border (as a thick rectangle behind the main box)
    border_color = (0, 0, 0)  # Black border, change as needed
    cv2.rectangle(img, (x-40-border_thickness, y-40-border_thickness), (x+40+border_thickness, y+40+border_thickness), border_color, -1)

    # Main box with gradient
    for i in range(80):
        c = (
            int(color[1] + (255-color[1]) * i/80),
            int(color[2] + (255-color[2]) * i/80),
            int(color[2] + (255-color[2]) * i/80)
        )
        cv2.rectangle(img, (x-40+i, y-40+i), (x+40-i, y+40-i), c, 1)

    # Main box outline (optional, for extra sharpness)
    cv2.rectangle(img, (x-40, y-40), (x+40, y+40), border_color, 2)

    # 3D top
    pts = np.array([[x-40, y-40], [x-30, y-55], [x+30, y-55], [x+40, y-40]], np.int32)
    cv2.fillPoly(img, [pts], (min(color[0]+40,255), min(color[1]+40,255), min(color[2]+40,255)))
    cv2.polylines(img, [pts], isClosed=True, color=border_color, thickness=2)

    # Highlight
    if highlight:
        cv2.line(img, (x-40, y-40), (x-30, y-55), (255,255,255), 2)
        cv2.line(img, (x+40, y-40), (x+30, y-55), (255,255,255), 2)

    # Number
    cv2.putText(img, str(number), (x-22, y+18), cv2.FONT_HERSHEY_DUPLEX, 1.7, (0,0,0), 4)
    cv2.putText(img, str(number), (x-22, y+18), cv2.FONT_HERSHEY_DUPLEX, 1.7, (255,255,255), 2)

def draw_button(img, text, pos, color=(200, 200, 200)):
    x, y = pos
    cv2.rectangle(img, (x, y), (x+120, y+60), color, -1)
    cv2.rectangle(img, (x, y), (x+120, y+60), (0, 0, 0), 2)
    cv2.putText(img, text, (x+10, y+40), cv2.FONT_HERSHEY_SIMPLEX, 1, (0,0,0), 2)
    return (x, y, 120, 60)

def generate_question():
    random_values = random.sample(range(1, 21), 4)
    return random_values, sorted(random_values)

cap = cv2.VideoCapture(0)

question, correct_order = generate_question()
selected = []
dragging = False
drag_index = None
drag_offset = (0, 0)
drag_value = None
speak("Arrange the numbers in ascending order")

start_positions = [(150 + i * 180, 120) for i in range(4)]
place_positions = [(150 + i * 180, 350) for i in range(4)]

while cap.isOpened():
    ret, frame = cap.read()
    if not ret:
        break
    frame = cv2.flip(frame, 1)
    frame = cv2.resize(frame, (WINDOW_WIDTH, WINDOW_HEIGHT))
    h, w, _ = frame.shape
    rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    results = hands.process(rgb)
    finger = None

    # Instruction at the top
    cv2.putText(frame, "Arrange the numbers in ascending order!", (80, 60), cv2.FONT_HERSHEY_SIMPLEX, 1.2, (0,0,255), 3)

    if results.multi_hand_landmarks:
        for hand_landmarks in results.multi_hand_landmarks:
            lm = hand_landmarks.landmark[8]
            finger = int(lm.x * w), int(lm.y * h)
            mp_drawing.draw_landmarks(frame, hand_landmarks, mp_hands.HAND_CONNECTIONS)

    # Draw current number blocks (not selected)
    for i, val in enumerate(question):
        if val not in selected or (dragging and drag_index == i):
            draw_3d_box(frame, start_positions[i], val)

    # Draw user selected blocks
    for i, val in enumerate(selected):
        draw_3d_box(frame, place_positions[i], val, (100, 255, 100))

    # Draw buttons vertically
    button_x = 1000  # x position (right side of the window)
    button_y_start = 200  # starting y position
    button_gap = 100      # vertical gap between buttons

    del_btn = draw_button(frame, "DEL", (button_x, button_y_start))
    sub_btn = draw_button(frame, "SUBMIT", (button_x, button_y_start + button_gap), (180, 255, 180))
    next_btn = draw_button(frame, "NEXT", (button_x, button_y_start + 2 * button_gap), (180, 180, 255))
    quit_btn = draw_button(frame, "QUIT", (button_x, button_y_start + 3 * button_gap), (255, 180, 180))

    # Drag and drop logic
    if finger:
        fx, fy = finger

        if not dragging:
            # Start dragging if finger is on a block
            for i, (x, y) in enumerate(start_positions):
                if is_inside((x-40, y-40, 80, 80), finger):
                    if question[i] not in selected and len(selected) < 4:
                        dragging = True
                        drag_index = i
                        drag_value = question[i]
                        drag_offset = (fx - x, fy - y)
                        break
        else:
            # If dragging, show block at finger
            draw_3d_box(frame, (fx - drag_offset[0], fy - drag_offset[1]), drag_value, (255, 200, 100), shadow=False, highlight=True)
            # Drop block if finger is over place_positions
            for i, (px, py) in enumerate(place_positions):
                if is_inside((px-40, py-40, 80, 80), finger):
                    if drag_value not in selected and len(selected) < 4:
                        selected.append(drag_value)
                        speak(f"Added {drag_value}")
                        dragging = False
                        drag_index = None
                        drag_value = None
                        break
            # Cancel drag if finger is over DEL
            if is_inside(del_btn, finger):
                dragging = False
                drag_index = None
                drag_value = None
                speak("Cancelled")
        # Button actions (only if not dragging)
        if not dragging:
            # Delete last
            if is_inside(del_btn, finger) and selected:
                removed = selected.pop()
                speak(f"Removed {removed}")
            # Submit check
            if is_inside(sub_btn, finger):
                if selected == correct_order:
                    speak("Congratulations, answer is correct!")
                else:
                    speak("Try again")
            # Next question
            if is_inside(next_btn, finger):
                question, correct_order = generate_question()
                selected = []
                speak("Next. Arrange the numbers in ascending order")
            # Quit button
            if is_inside(quit_btn, finger):
                speak("Exiting the game")
                break

    else:
        # If finger not detected, stop dragging
        dragging = False
        drag_index = None
        drag_value = None

    cv2.imshow("Ascending Order Puzzle", frame)
    if cv2.waitKey(1) & 0xFF == 27:  # ESC to quit
        break

cap.release()
cv2.destroyAllWindows()