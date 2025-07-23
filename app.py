import streamlit as st
import replicate
import base64
import os
from PIL import Image
from io import BytesIO

# Set your Replicate API token securely
REPLICATE_API_TOKEN = "r8_2bZyEXAMPLE123456789abcdefg"
os.environ["REPLICATE_API_TOKEN"] = REPLICATE_API_TOKEN

st.set_page_config(page_title="Comic Face Swap Generator", page_icon="🦸", layout="centered")

st.title("🦸 Comic Face Swap Generator")
st.markdown("Upload a selfie, choose a comic book cover, and generate your comic-style transformation!")

# Upload user image
uploaded_file = st.file_uploader("Upload a selfie or photo", type=["jpg", "jpeg", "png"])

# Select comic cover (dropdown)
cover_options = {
    "Vigilante City": "https://i.imgur.com/abc123.jpg",  # Replace with real public URLs
    "Neon Samurai": "https://i.imgur.com/def456.jpg",
    "Star Voyage": "https://i.imgur.com/ghi789.jpg"
}
selected_cover = st.selectbox("Choose a comic book cover", list(cover_options.keys()))

# Preview the selected cover
st.image(cover_options[selected_cover], caption=f"{selected_cover} Cover", use_container_width=True)

# Generate button
if st.button("Generate Comic") and uploaded_file:
    st.subheader("Processing your image...")

    try:
        # Convert uploaded image to base64
        image_bytes = uploaded_file.read()
        image_base64 = base64.b64encode(image_bytes).decode("utf-8")

        # Call Replicate API with base64 image and selected cover
        output = replicate.run(
            "your-username/comic-style-face-swap:latest",  # Replace with your model
            input={
                "image": f"data:image/jpeg;base64,{image_base64}",
                "cover_url": cover_options[selected_cover]
            }
        )

        st.image(output["image"], caption="Your Comic Cover", use_container_width=True)

    except Exception as e:
        st.error(f"An error occurred while generating your comic: {str(e)}")
