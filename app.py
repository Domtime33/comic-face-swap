import streamlit as st
import requests
import replicate
import os
from PIL import Image
from io import BytesIO

# Set Streamlit page config
st.set_page_config(page_title="Comic Face Swap", layout="centered")

# --- Load Replicate API Token ---
try:
    api_token = st.secrets["REPLICATE_API_TOKEN"]
    os.environ["REPLICATE_API_TOKEN"] = api_token
except KeyError:
    st.error("REPLICATE_API_TOKEN not found in secrets. Please set it in Streamlit secrets.")
    st.stop()

# --- Title ---
st.title("🦸‍♂️ Comic Face Swap Generator")

# --- Upload photo ---
uploaded_file = st.file_uploader("Upload a selfie or photo", type=["jpg", "jpeg", "png"])

# --- Comic cover selection ---
comic_options = {
    "Superwoman Classic": "https://i.imgur.com/LuWjwHZ.png",
    "Space Hero": "https://i.imgur.com/NyAJJF3.png",
    "Vigilante City": "https://i.imgur.com/FCXymJ7.png"
}
selected_cover = st.selectbox("Choose a comic book cover", list(comic_options.keys()))
cover_url = comic_options[selected_cover]

# Show selected comic cover
st.image(cover_url, caption=f"{selected_cover} Cover", use_column_width=True)

# --- Generate comic button ---
if uploaded_file and st.button("Generate Comic"):
    st.subheader("Processing your image...")

    try:
        # Load uploaded image
        image_bytes = uploaded_file.read()

        # Call Replicate API for comic face generation
        with st.spinner("Generating comic face..."):
            output_url = replicate.run(
                "cjwbw/stable-diffusion-comic:db21e45e13cba57e71abdfd1041514f63c70ac2ae43e0d0d61651758b1ce0ae4",
                input={"image": image_bytes}
            )

        if output_url:
            # Download output image
            response = requests.get(output_url)
            output_img = Image.open(BytesIO(response.content))

            # Display final comic result
            st.image(output_img, caption="🧠 Your Comic-Style Face", use_column_width=True)
        else:
            st.error("No image returned. Please try again.")

    except Exception as e:
        st.error(f"⚠️ An error occurred while generating your comic: {e}")
