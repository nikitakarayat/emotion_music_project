import cv2
import numpy as np
from tensorflow.keras.models import load_model
from tensorflow.keras.preprocessing.image import img_to_array

# Load your pre-trained emotion detection model here
model = load_model("models/emotion_model.h5")

# Emotion labels must match the model's output classes
EMOTIONS = ["angry", "disgust", "fear", "happy", "sad", "surprise", "neutral"]

face_detector = cv2.CascadeClassifier(cv2.data.haarcascades + "haarcascade_frontalface_default.xml")

def predict_emotion(frame):
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    faces = face_detector.detectMultiScale(gray, scaleFactor=1.3, minNeighbors=5)

    if len(faces) == 0:
        return None

    # Take the first face detected
    (x, y, w, h) = faces[0]
    roi_gray = gray[y:y+h, x:x+w]
    roi_gray = cv2.resize(roi_gray, (48, 48))
    roi = roi_gray.astype("float") / 255.0
    roi = img_to_array(roi)
    roi = np.expand_dims(roi, axis=0)

    preds = model.predict(roi)[0]
    emotion_probability = np.max(preds)
    emotion_label = EMOTIONS[preds.argmax()]

    return emotion_label
