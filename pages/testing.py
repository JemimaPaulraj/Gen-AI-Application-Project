# ==========================================================
# 🖼️ Image Generator (Streamlit Cloud Safe - CPU Only)
# ==========================================================
import os
import streamlit as st
import matplotlib.pyplot as plt
import torch
from diffusers import StableDiffusionPipeline
from PIL import Image

# ------------------ Hugging Face Token ------------------
HF_TOKEN = os.getenv("HF_TOKEN")
if HF_TOKEN is None:
    st.error("HF_TOKEN not found. Please set it as an environment variable in Streamlit Cloud.")
    st.stop()

# ------------------ Page Config ------------------
st.set_page_config(page_title="🖌️ Image Generator", layout="wide")

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
    }
    </style>
""", unsafe_allow_html=True)

st.markdown('<div class="custom-heading">🖼️ Text to Image Generator</div>', unsafe_allow_html=True)
st.write("Convert your ideas into art using a lightweight diffusion model!")

# ------------------ UI Inputs ------------------
col1, col2, col3 = st.columns([1, 1, 1])
with col1:
    model_name = st.selectbox("**Model**", ["Segmind Small-SD (Lightweight)"])
with col2:
    image_size = st.selectbox("**Image Size**", ["256x256", "512x512"])
with col3:
    num_images = st.slider("**Number of Images**", min_value=1, max_value=2, value=1, step=1)

st.markdown("<hr>", unsafe_allow_html=True)

prompt = st.text_area("**Enter your prompt**", placeholder="e.g. A cute kitten in a spaceship", height=100)
generate = st.button("Generate")

# ------------------ Model Map ------------------
model_map = {
    "Segmind Small-SD (Lightweight)": "segmind/small-sd"
}

# ------------------ Load Pipeline (Cached) ------------------
@st.cache_resource
def load_pipeline(model_id):
    try:
        pipe = StableDiffusionPipeline.from_pretrained(
            model_id,
            torch_dtype=torch.float32,   # ✅ CPU safe
            use_auth_token=HF_TOKEN,
            low_cpu_mem_usage=True       # ✅ reduces memory
        )
        return pipe.to("cpu")            # ✅ CPU-only mode
    except Exception as e:
        st.error(f"Model loading failed: {e}")
        return None

# ------------------ Image Generation ------------------
def generate_images(pipe, prompt, num_images, image_size):
    width, height = map(int, image_size.split("x"))
    images = []
    for i in range(num_images):
        with torch.no_grad():
            result = pipe(prompt, num_inference_steps=20, guidance_scale=7.5)
            image = result.images[0].resize((width, height))
            images.append(image)
    return images

# ------------------ Run ------------------
if generate and prompt.strip():
    model_id = model_map[model_name]
    pipe = load_pipeline(model_id)
    if pipe:
        with st.spinner("Generating image(s)... Please wait ⏳"):
            try:
                images = generate_images(pipe, prompt, num_images, image_size)
                for i, img in enumerate(images):
                    st.image(img, caption=f"Generated Image {i+1}", use_container_width=False)
            except Exception as e:
                st.error(f"⚠️ Image generation failed: {e}")
