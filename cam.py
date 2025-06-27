import cv2
import numpy as np
from utils import face_points, read_landmarks, add_mask
import mediapipe as mp

selected_products = set()

# Default opacity and color values
opacity_values = {
    "LIP": 0.6, "EYESHADOW": 0.4, "EYELINER": 0.5,
    "FOUNDATION": 0.3, "HIGHLIGHTER": 0.4, "BLUSH": 0.4
}
product_colors = {
    "LIP": [0, 0, 255], "EYELINER": [139, 0, 0],
    "EYESHADOW": [0, 100, 0], "FOUNDATION": [203, 192, 255],
    "BLUSH": [147, 20, 255], "HIGHLIGHTER": [255, 255, 255]
}

# Product button layout
products = [
    ("LIP", (10, 30)), ("EYELINER", (10, 70)),
    ("EYESHADOW", (10, 110)), ("FOUNDATION", (10, 150)),
    ("BLUSH", (10, 190)), ("HIGHLIGHTER", (10, 230))
]

# Handle mouse clicks on product buttons
def handle_click(event, x, y, flags, param):
    if event == cv2.EVENT_LBUTTONDOWN:
        for name, (bx, by) in products:
            if bx <= x <= bx + 120 and by - 20 <= y <= by:
                if name in selected_products:
                    selected_products.remove(name)
                else:
                    selected_products.add(name)

# Create sliders in separate window
def setup_sliders():
    cv2.namedWindow("Makeup Controls", cv2.WINDOW_NORMAL)
    for name in opacity_values:
        cv2.createTrackbar(f"{name}_opacity", "Makeup Controls", int(opacity_values[name] * 100), 100, lambda x: None)
        for ch in ["R", "G", "B"]:
            default_val = product_colors[name][{"B": 0, "G": 1, "R": 2}[ch]]
            cv2.createTrackbar(f"{name}_{ch}", "Makeup Controls", default_val, 255, lambda x: None)

# Update opacity and colors from sliders
def update_values():
    for name in opacity_values:
        opacity_values[name] = cv2.getTrackbarPos(f"{name}_opacity", "Makeup Controls") / 100.0
        b = cv2.getTrackbarPos(f"{name}_B", "Makeup Controls")
        g = cv2.getTrackbarPos(f"{name}_G", "Makeup Controls")
        r = cv2.getTrackbarPos(f"{name}_R", "Makeup Controls")
        product_colors[name] = [b, g, r]

# Setup camera and MediaPipe
cap = cv2.VideoCapture(0)
mp_face_mesh = mp.solutions.face_mesh
face_mesh = mp_face_mesh.FaceMesh(refine_landmarks=True)

cv2.namedWindow("Virtual Makeup Preview")
cv2.setMouseCallback("Virtual Makeup Preview", handle_click)
setup_sliders()

while True:
    ret, frame = cap.read()
    if not ret:
        print("Camera failed to open.")
        break

    frame = cv2.flip(frame, 1)
    display_frame = frame.copy()
    mask = np.zeros_like(frame)
    landmarks = read_landmarks(frame, face_mesh)
    update_values()

    if landmarks:
        if "LIP" in selected_products:
            mask = add_mask(mask, landmarks, face_points["LIP_UPPER"], product_colors["LIP"], opacity_values["LIP"])
            mask = add_mask(mask, landmarks, face_points["LIP_LOWER"], product_colors["LIP"], opacity_values["LIP"])
        if "EYELINER" in selected_products:
            mask = add_mask(mask, landmarks, face_points["EYELINER_LEFT"], product_colors["EYELINER"], opacity_values["EYELINER"])
            mask = add_mask(mask, landmarks, face_points["EYELINER_RIGHT"], product_colors["EYELINER"], opacity_values["EYELINER"])
        if "EYESHADOW" in selected_products:
            mask = add_mask(mask, landmarks, face_points["EYESHADOW_LEFT"], product_colors["EYESHADOW"], opacity_values["EYESHADOW"])
            mask = add_mask(mask, landmarks, face_points["EYESHADOW_RIGHT"], product_colors["EYESHADOW"], opacity_values["EYESHADOW"])
        if "FOUNDATION" in selected_products:
            mask = add_mask(mask, landmarks, face_points["FACE"], product_colors["FOUNDATION"], opacity_values["FOUNDATION"])
        if "HIGHLIGHTER" in selected_products:
            mask = add_mask(mask, landmarks, face_points["HIGHLIGHTER"], product_colors["HIGHLIGHTER"], opacity_values["HIGHLIGHTER"])
        if "BLUSH" in selected_products:
            for idx in [face_points["BLUSH_LEFT"][0], face_points["BLUSH_RIGHT"][0]]:
                if idx in landmarks:
                    center = landmarks[idx]
                    cv2.circle(mask, center, 30, product_colors["BLUSH"], -1)
            mask = cv2.addWeighted(mask, opacity_values["BLUSH"], np.zeros_like(mask), 1 - opacity_values["BLUSH"], 0)

    # Draw buttons on preview
    for name, (bx, by) in products:
        is_selected = name in selected_products
        color = tuple(int(c) for c in product_colors[name])
        cv2.rectangle(display_frame, (bx, by - 20), (bx + 120, by), color, -1 if is_selected else 2)
        cv2.putText(display_frame, name, (bx + 5, by - 5), cv2.FONT_HERSHEY_SIMPLEX, 0.5,
                    (255, 255, 255) if is_selected else color, 1)

    combined = cv2.addWeighted(display_frame, 1.0, mask, 0.4, 0)
    cv2.imshow("Virtual Makeup Preview", combined)

    if cv2.waitKey(1) & 0xFF == ord("q"):
        break

cap.release()
cv2.destroyAllWindows()
