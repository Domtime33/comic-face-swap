# app.py
import streamlit as st
import cv2
import numpy as np
from PIL import Image
import io

st.set_page_config(layout="centered", page_title="Comic Face Swap", page_icon="🦸")

st.title("🦸 Comic Face Swap Generator")
st.markdown("Upload a comic cover and your selfie. We'll blend your face into the comic!")

# Upload Comic Cover
comic_file = st.file_uploader("📘 Upload Comic Cover", type=["jpg", "jpeg", "png"], key="comic")
# Upload Face Photo
face_file = st.file_uploader("📸 Upload Your Selfie", type=["jpg", "jpeg", "png"], key="face")

def load_image(file):
    image = Image.open(file).convert("RGB")
    return np.array(image)

def detect_face(image_np):
    gray = cv2.cvtColor(image_np, cv2.COLOR_RGB2GRAY)
    face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + "haarcascade_frontalface_default.xml")
    faces = face_cascade.detectMultiScale(gray, 1.3, 5)
    return faces

def swap_face(comic_np, face_np):
    faces = detect_face(comic_np)
    if len(faces) == 0:
        return None

    (x, y, w, h) = faces[0]

    face_resized = cv2.resize(face_np, (w, h))
    comic_copy = comic_np.copy()
    comic_copy[y:y+h, x:x+w] = face_resized

    return comic_copy

if comic_file and face_file:
    comic_np = load_image(comic_file)
    face_np = load_image(face_file)

    st.image(comic_np, caption="Original Comic Cover", use_column_width=True)
    st.image(face_np, caption="Original Selfie", use_column_width=True)

    result = swap_face(comic_np, face_np)

    if result is not None:
        st.image(result, caption="🧬 Comic Face Swap Result", use_column_width=True)
        result_pil = Image.fromarray(result)
        buffered = io.BytesIO()
        result_pil.save(buffered, format="PNG")
        st.download_button("📥 Download Your Comic", buffered.getvalue(), "comic_face_swap.png")
    else:
        st.error("😕 Couldn't detect a face in the comic cover. Try another image.")
