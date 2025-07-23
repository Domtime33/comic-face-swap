import streamlit as st
from PIL import Image
import os
import replicate
import io

# -----------------------------
# REPLICATE AUTHENTICATION
# -----------------------------
REPLICATE_API_TOKEN = st.secrets["REPLICATE_API_TOKEN"]
os.environ["REPLICATE_API_TOKEN"] = REPLICATE_API_TOKEN

# -----------------------------
# UTILITY FUNCTIONS
# -----------------------------
def list_comic_covers(folder_path="covers"):
    covers = []
    for file in os.listdir(folder_path):
        if file.endswith(('.png', '.jpg', '.jpeg')):
            title, issue = file.rsplit('_', 1)
            issue = issue.split('.')[0]
            covers.append((f"{title.replace('-', ' ')} - Issue #{issue}", os.path.join(folder_path, file)))
    return sorted(covers, key=lambda x: x[0])

def generate_comic_style(user_image, cover_image_path):
    model = replicate.models.get("your-username/comic-face-swap")  # Replace with your model name
    version = model.versions.get("latest")  # Or use a pinned version hash

    with open(cover_image_path, "rb") as f:
        cover_bytes = f.read()
    cover_img_io = io.BytesIO(cover_bytes)

    output_url = replicate.run(
        version,
        input={
            "face_image": user_image,
            "comic_cover": cover_img_io
        }
    )
    return output_url

# -----------------------------
# STREAMLIT INTERFACE
# -----------------------------
st.set_page_config(page_title="Comic Face Swap", layout="centered")

st.title("🦸 Comic Face-Swap Generator")
st.markdown("Upload a face and select a comic cover to generate your stylized comic panel!")

# Upload face image
user_face = st.file_uploader("Upload your face photo", type=["jpg", "jpeg", "png"])
if user_face:
    st.image(user_face, caption="Uploaded Face", use_column_width=True)

# Select comic cover
covers = list_comic_covers()
cover_labels = [label for label, _ in covers]
selected_cover_label = st.selectbox("Choose a comic cover", cover_labels)
selected_cover_path = dict(covers)[selected_cover_label]

st.image(selected_cover_path, caption="Selected Comic Cover", use_column_width=True)

# Generate comic
if st.button("Generate Comic Face Swap") and user_face:
    with st.spinner("Generating your comic... please wait"):
        result_url = generate_comic_style(user_face, selected_cover_path)
        if result_url:
            st.success("✅ Comic created!")
            st.image(result_url, caption="Your Comic Panel", use_column_width=True)
        else:
            st.error("❌ Something went wrong generating the comic.")

