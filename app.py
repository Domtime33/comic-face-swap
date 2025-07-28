# app.py
import streamlit as st
import os
import sqlite3
from datetime import datetime
from PIL import Image
import requests

# ========== CONFIG ==========
st.set_page_config(page_title="Comic Face Swap App", layout="centered")

UPLOAD_DIR = "covers"
DB_PATH = "covers.db"
REPLICATE_API_TOKEN = os.getenv("REPLICATE_API_TOKEN")
REPLICATE_MODEL = "your-replicate-username/your-model-name"

# Ensure upload directory exists
os.makedirs(UPLOAD_DIR, exist_ok=True)

# ========== DB INIT ==========
def init_db():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS covers (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            filename TEXT,
            title TEXT,
            issue TEXT,
            date TEXT
        )
    ''')
    conn.commit()
    conn.close()

init_db()

# ========== DB FUNCTIONS ==========
def save_cover_to_db(filename, title, issue, date):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("INSERT INTO covers (filename, title, issue, date) VALUES (?, ?, ?, ?)",
                   (filename, title, issue, date))
    conn.commit()
    conn.close()

def get_all_covers():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT filename, title, issue, date FROM covers")
    covers = cursor.fetchall()
    conn.close()
    return covers

# ========== UI SECTIONS ========== 
st.title("📸 Comic Face Swap")
st.subheader("Upload your selfie and pick a comic cover")

# === Step 1: Upload Selfie ===
selfie = st.file_uploader("Upload a selfie", type=["jpg", "jpeg", "png"])

# === Step 2: Upload Comic Cover ===
st.markdown("---")
st.markdown("### Upload a Comic Cover (Optional)")
cover_file = st.file_uploader("Upload comic cover", type=["jpg", "jpeg", "png"], key="cover")
title = st.text_input("Comic Title")
issue = st.text_input("Issue Number")
date = st.date_input("Publication Date", value=datetime.today())

if st.button("Save Cover") and cover_file:
    filename = f"{datetime.now().strftime('%Y%m%d%H%M%S')}_{cover_file.name}"
    filepath = os.path.join(UPLOAD_DIR, filename)
    with open(filepath, "wb") as f:
        f.write(cover_file.getbuffer())
    save_cover_to_db(filename, title, issue, date.isoformat())
    st.success("Cover saved!")

# === Step 3: Select from All Covers ===
st.markdown("---")
st.markdown("### Choose a Cover")
covers = get_all_covers()

selected = st.selectbox("Available Covers", options=[f"{c[1]} | Issue {c[2]} | {c[3]}" for c in covers])
selected_filename = covers[[f"{c[1]} | Issue {c[2]} | {c[3]}" for c in covers].index(selected)][0]

cover_path = os.path.join(UPLOAD_DIR, selected_filename)
st.image(cover_path, caption="Selected Comic Cover", use_column_width=True)

# === Step 4: Generate Comic ===
if st.button("Generate Comic"):
    if not selfie:
        st.warning("Please upload a selfie first.")
    else:
        # Save selfie to temp
        selfie_img = Image.open(selfie).convert("RGB")
        selfie_path = os.path.join("temp_selfie.jpg")
        selfie_img.save(selfie_path)

        with open(selfie_path, "rb") as img_file:
            files = {"image": img_file}
            headers = {"Authorization": f"Token {REPLICATE_API_TOKEN}"}
            response = requests.post(
                f"https://api.replicate.com/v1/predictions",
                headers=headers,
                json={
                    "version": REPLICATE_MODEL,
                    "input": {
                        "cover_image": open(cover_path, "rb").read(),
                        "selfie_image": open(selfie_path, "rb").read()
                    }
                }
            )

        if response.status_code == 200:
            output_url = response.json()["urls"]["get"]
            st.success("Comic generated successfully!")
            st.image(output_url)
        else:
            st.error("There was an error generating the comic.")
