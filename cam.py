from flask import Flask, render_template, Response, request
import cv2
import numpy as np
import mediapipe as mp
from utils import face_points, read_landmarks, add_mask

app = Flask(__name__)

selected_products = set()
product_colors = {
    "LIP": [0, 0, 255], "EYELINER": [139, 0, 0],
    "EYESHADOW": [0, 100, 0], "FOUNDATION": [203, 192, 255],
    "BLUSH": [147, 20, 255], "HIGHLIGHTER": [255, 255, 255]
}
opacity_values = {
    "LIP": 0.6, "EYESHADOW": 0.4, "EYELINER": 0.5,
    "FOUNDATION": 0.3, "HIGHLIGHTER": 0.4, "BLUSH": 0.4
}

cap = cv2.VideoCapture(0)
mp_face_mesh = mp.solutions.face_mesh
face_mesh = mp_face_mesh.FaceMesh(refine_landmarks=True)

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/select", methods=["POST"])
def select():
    global selected_products, opacity_values, product_colors
    data = request.json
    selected_products = set(data.get("products", []))
    settings = data.get("settings", {})

    for product in settings:
        opacity_values[product] = float(settings[product]["opacity"])
        product_colors[product] = [
            int(settings[product]["b"]),
            int(settings[product]["g"]),
            int(settings[product]["r"]),
        ]
    return {"status": "updated"}

@app.route("/video_feed")
def video_feed():
    return Response(generate_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')

def generate_frames():
    while True:
        success, frame = cap.read()
        if not success:
            break

        frame = cv2.flip(frame, 1)
        display_frame = frame.copy()
        mask = np.zeros_like(frame)
        landmarks = read_landmarks(frame, face_mesh)

        if landmarks:
            for product in selected_products:
                if product == "LIP":
                    mask = add_mask(mask, landmarks, face_points["LIP_UPPER"], product_colors["LIP"], opacity_values["LIP"])
                    mask = add_mask(mask, landmarks, face_points["LIP_LOWER"], product_colors["LIP"], opacity_values["LIP"])
                elif product == "EYELINER":
                    mask = add_mask(mask, landmarks, face_points["EYELINER_LEFT"], product_colors["EYELINER"], opacity_values["EYELINER"])
                    mask = add_mask(mask, landmarks, face_points["EYELINER_RIGHT"], product_colors["EYELINER"], opacity_values["EYELINER"])
                elif product == "EYESHADOW":
                    mask = add_mask(mask, landmarks, face_points["EYESHADOW_LEFT"], product_colors["EYESHADOW"], opacity_values["EYESHADOW"])
                    mask = add_mask(mask, landmarks, face_points["EYESHADOW_RIGHT"], product_colors["EYESHADOW"], opacity_values["EYESHADOW"])
                elif product == "FOUNDATION":
                    mask = add_mask(mask, landmarks, face_points["FACE"], product_colors["FOUNDATION"], opacity_values["FOUNDATION"])
                elif product == "HIGHLIGHTER":
                    mask = add_mask(mask, landmarks, face_points["HIGHLIGHTER"], product_colors["HIGHLIGHTER"], opacity_values["HIGHLIGHTER"])
                elif product == "BLUSH":
                    for idx in [face_points["BLUSH_LEFT"][0], face_points["BLUSH_RIGHT"][0]]:
                        if idx in landmarks:
                            center = landmarks[idx]
                            cv2.circle(mask, center, 30, product_colors["BLUSH"], -1)
                    mask = cv2.addWeighted(mask, opacity_values["BLUSH"], np.zeros_like(mask), 1 - opacity_values["BLUSH"], 0)

        combined = cv2.addWeighted(display_frame, 1.0, mask, 0.4, 0)
        ret, buffer = cv2.imencode('.jpg', combined)
        frame = buffer.tobytes()

        yield (b'--frame\r\nContent-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')

if __name__ == "__main__":
    app.run(debug=True)
