import streamlit as st
from transformers import BlipProcessor, BlipForConditionalGeneration
from PIL import Image
import torch

st.set_page_config(page_title=" Image Captioning ", layout="wide")
# -----------------------------
# Styling
# -----------------------------
st.markdown("""
<style>
.custom-heading {
    width: 100%; height: 80px; background-color: #C9BBCF;
    color: black; font-size: 20px; font-weight: bold;
    border-radius: 12px; display: flex; align-items: center;
    justify-content: center; box-shadow: 0 4px 8px rgba(0,0,0,0.1);
    margin-bottom: 20px;
}
.custom-heading:hover { background-color: #E2DCE8; transform: scale(1.02); }
div.stButton > button {
    background-color: #C9BBCF !important; color: black !important;
    font-size: 16px !important; font-weight: bold !important;
    border-radius: 8px !important; padding: 10px 24px !important;
    box-shadow: 0 2px 4px rgba(0,0,0,0.1) !important;
    margin-top: 10px !important;
}
div.stButton > button:hover {
    background-color: #E2DCE8 !important; transform: scale(1.03) !important;
}
</style>
""", unsafe_allow_html=True)

st.markdown('<div class="custom-heading">BLIP Image Captioning 📝</div>', unsafe_allow_html=True)
#st.markdown('<p style="color: grey; font-size: 14px; text-align: center;">📷 Upload an image and let BLIP describe it in words !</p>',unsafe_allow_html=True)
st.markdown("<hr style='margin: 15px 0;'>", unsafe_allow_html=True)

# -----------------------------
# Device check
# -----------------------------
device = "cuda" if torch.cuda.is_available() else "cpu"

# -----------------------------
# Load BLIP in session state
# -----------------------------
if "blip_processor" not in st.session_state or "blip_model" not in st.session_state:
    with st.spinner("Loading BLIP model (may take some time)..."):
        st.session_state.blip_processor = BlipProcessor.from_pretrained("Salesforce/blip-image-captioning-base")
        st.session_state.blip_model = BlipForConditionalGeneration.from_pretrained("Salesforce/blip-image-captioning-base").to(device)

processor = st.session_state.blip_processor
model = st.session_state.blip_model

# -----------------------------
# Upload image
# -----------------------------
col1, col2 = st.columns([3, 1])
with col1:
    uploaded_file = st.file_uploader("***📎Upload an image and let BLIP describe it in words !***", type=["jpg", "jpeg", "png"])
with col2:
    st.write("")
    st.write("")
    generate_clicked = st.button("Generate Caption")

if uploaded_file:
    image = Image.open(uploaded_file).convert("RGB")
    max_size = (400, 400)
    image.thumbnail(max_size)

    # Use columns for layout
    col3, col4 = st.columns([1, 1])

    with col3:
        st.image(image, use_container_width=True)

    with col4:
        # Only generate caption if button clicked
        if generate_clicked:
            with st.spinner("Generating caption..."):
                inputs = processor(images=image, return_tensors="pt").to(device)
                out = model.generate(**inputs)
                caption = processor.decode(out[0], skip_special_tokens=True)
            st.markdown("<h4>📝 Generated Caption:</h4>", unsafe_allow_html=True)
            st.success(caption)
            #st.write(caption)
