# camera.py
import cv2
import numpy as np
import mediapipe as mp
from utils import face_points, read_landmarks, add_mask

# Facial features to enhance
face_elements = [
    "LIP_LOWER",
    "LIP_UPPER",
    "EYEBROW_LEFT",
    "EYEBROW_RIGHT",
    "EYELINER_LEFT",
    "EYELINER_RIGHT",
    "EYESHADOW_LEFT",
    "EYESHADOW_RIGHT",
]

# Colors for each feature
colors_map = {
    "LIP_UPPER": [0, 0, 255],        # Red lips
    "LIP_LOWER": [0, 0, 255],
    "EYELINER_LEFT": [139, 0, 0],    # Dark blue eyeliner
    "EYELINER_RIGHT": [139, 0, 0],
    "EYESHADOW_LEFT": [0, 100, 0],   # Dark green shadow
    "EYESHADOW_RIGHT": [0, 100, 0],
    "EYEBROW_LEFT": [19, 69, 139],   # Dark brown brows
    "EYEBROW_RIGHT": [19, 69, 139],
}

# Prepare data for rendering
face_connections = [face_points[part] for part in face_elements]
colors = [colors_map[part] for part in face_elements]

# Initialize webcam
cap = cv2.VideoCapture(0)

# Setup MediaPipe face mesh
with mp.solutions.face_mesh.FaceMesh(static_image_mode=False, refine_landmarks=True, max_num_faces=1) as face_mesh:
    while cap.isOpened():
        success, frame = cap.read()
        if not success:
            print("Camera not accessible.")
            break

        frame = cv2.flip(frame, 1)
        mask = np.zeros_like(frame)

        landmarks = read_landmarks(frame, face_mesh)
        if landmarks:
            mask = add_mask(mask, landmarks, face_connections, colors)
            output = cv2.addWeighted(frame, 1.0, mask, 0.4, 1.0)
        else:
            output = frame

        cv2.imshow("Virtual Makeup Try-On", output)

        if cv2.waitKey(5) & 0xFF == ord('q'):
            break

cap.release()
cv2.destroyAllWindows()
