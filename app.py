import streamlit as st
import requests
from PIL import Image
import io

# -----------------------
# PAGE CONFIG & STYLES
# -----------------------
st.set_page_config(
    page_title="Comic Face-Swap",
    page_icon="🦸",
    layout="centered",
)

st.markdown(
    """
    <style>
        .main {
            background-color: #1c1c1e;
            color: white;
        }
        .block-container {
            padding-top: 2rem;
        }
        .css-18e3th9 {
            padding: 2rem 1rem;
        }
        h1, h2, h3 {
            color: #00FFD1;
        }
        .stButton>button {
            background-color: #00FFD1;
            color: black;
            font-weight: bold;
            border-radius: 12px;
            padding: 0.5rem 1rem;
        }
    </style>
    """,
    unsafe_allow_html=True,
)

# -----------------------
# TITLE
# -----------------------
st.title("🦸 Comic Face-Swap Generator")

st.markdown("Upload your face and pick a comic book cover to transform yourself into a comic superhero!")

# -----------------------
# IMAGE UPLOAD
# -----------------------
uploaded_face = st.file_uploader("Upload a selfie", type=["jpg", "jpeg", "png"])

# -----------------------
# COVER TEMPLATE SELECTION
# -----------------------
cover_options = {
    "Spider-Hero": "https://i.imgur.com/kZ9bZpO.jpg",
    "Superwoman Classic": "https://i.imgur.com/lQxEJ8A.jpg",
    "Cosmic Avenger": "https://i.imgur.com/fZ2LVIm.jpg"
}

selected_cover = st.selectbox("Choose a comic book cover", list(cover_options.keys()))

# Display the cover preview
st.image(cover_options[selected_cover], caption=f"{selected_cover} Cover", use_container_width=True)

# -----------------------
# SUBMIT TO REPLICATE
# -----------------------
if st.button("Generate Comic"):
    if uploaded_face is None:
        st.error("Please upload a selfie before generating.")
    else:
        st.success("Processing your image...")

        api_token = st.secrets["REPLICATE_API_TOKEN"]
        replicate_url = "https://api.replicate.com/v1/predictions"

        # Prepare image bytes
        image_bytes = uploaded_face.read()
        image_io = io.BytesIO(image_bytes)

        headers = {
            "Authorization": f"Token {api_token}",
            "Content-Type": "application/json"
        }

        json_payload = {
            "version": "INSERT_YOUR_MODEL_VERSION_HERE",  # Replace with the correct version
            "input": {
                "face_image": f"data:image/png;base64,{image_bytes.hex()}",
                "template_url": cover_options[selected_cover]
            }
        }

        response = requests.post(replicate_url, headers=headers, json=json_payload)

        if response.status_code == 201:
            prediction_url = response.json()["urls"]["get"]
            with st.spinner("Waiting for model to complete..."):
                while True:
                    result = requests.get(prediction_url, headers=headers).json()
                    status = result["status"]
                    if status == "succeeded":
                        image_url = result["output"]
                        break
                    elif status == "failed":
                        st.error("Face-swap failed. Try again.")
                        break
            st.image(image_url, caption="Your Comic Cover", use_container_width=True)
        else:
            st.error("There was an error connecting to the model.")

# -----------------------
# FOOTER
# -----------------------
st.markdown("---")
st.caption("Built with ❤️ using Streamlit + Replicate")
