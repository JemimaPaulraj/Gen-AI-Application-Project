# Import Necessary packages
import torch # Imports PyTorch library for tensor operations and GPU acceleration
import streamlit as st
import matplotlib.pyplot as plt
from diffusers import StableDiffusionPipeline  # it comes from Hugging Face diffusers library to generate image to text.

#---------------------------------------------------------------------------------------------------------------
st.set_page_config(page_title=" Image Generator ", layout="wide")
# Styling the heading

# Styling
st.markdown("""
    <style>
    .element-container { margin-top: -0.5rem; }
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
    .center-button { display: flex; justify-content: center; margin-top: 20px; }
    .stTextInput input::placeholder {font-size: 14px;}
    textarea::placeholder {font-size: 14px;}
    </style>
""", unsafe_allow_html=True)

st.markdown('<div class="custom-heading">Image Generator 🎨</div>', unsafe_allow_html=True)

st.markdown('<p style="color: grey; font-size: 14px; text-align: center;">🖌️ Turn your ideas into art with just a few words !</p>',unsafe_allow_html=True)

st.markdown("<hr style='margin: 15px 0;'>", unsafe_allow_html=True)

#---------------------------------------------------------------------------------------------------------------
                                    # Get Inputs from the user

# Get the input model name from user
col1, col2, col3= st.columns([1, 1, 1])
with col1:
    model = st.selectbox("***Model***", ["Stable Diffusion v1.5","Dreamlike Photoreal 2.0"])


with col2:
    Image_Size = st.selectbox("***Image Size***", ["256x256","512x512"])

with col3:
    Number_of_Images = st.slider("***Number of Images***", min_value=1, max_value=3, value=1, step=1)

#spacer 
st.markdown("<hr style='margin: 15px 0;'>", unsafe_allow_html=True)

# Create text area to get user prompt
col1, col2= st.columns([5, 1])
with col1:
        User_Prompt = st.text_area("**Enter your prompt**", height=100, placeholder="e.g. A futuristic cityscape at sunset")

with col2:
    for _ in range(5):
        st.write("")
    summarize_clicked = st.button("Generate")

model_map = {
    "Stable Diffusion v1.5": "runwayml/stable-diffusion-v1-5",
    "Dreamlike Photoreal 2.0": "dreamlike-art/dreamlike-photoreal-2.0",
}
#---------------------------------------------------------------------------------------------------------------
# Cache Model Loading for faster reloads
@st.cache_resource
def load_pipeline(model_id, device):
    pipe = StableDiffusionPipeline.from_pretrained(
        model_id,
        torch_dtype = torch.float16 if device=="cuda" else torch.float32
    )
    return pipe.to(device)

#---------------------------------------------------------------------------------------------------------------
                                # Model Pipeline

# Function to generate images
def generate_images(pipe, prompt, params):
    width, height = Image_Size.split("x")
    images = pipe(prompt, **params).images
    n = len(images)
    if n > 1:
        fig, axs = plt.subplots(1, n, figsize=(5 * n, 5))
        for i, img in enumerate(images):
            axs[i].imshow(img)
            axs[i].axis("off")
        st.pyplot(fig)
    else:
        small_img = images[0].resize((int(width), int(height)))
        st.image(small_img, caption="Generated Image", use_container_width=False)

# generating images
if summarize_clicked and User_Prompt.strip():
    with st.spinner("Generating Images, It may take some time..."):
        st.error("⚠️ Please run image generation locally with GPU. Stable Diffusion models require significant memory and may cause memory overload on Streamlit Cloud.") # remove this line when running in local
        model_id = model_map[model]
        device = "cuda" if torch.cuda.is_available() else "cpu"
        st.write(f"Running on: {device.upper()}")
        pipe = load_pipeline(model_id, device)
        params = {
            "num_inference_steps": 50,
            "num_images_per_prompt": Number_of_Images
        }
        generate_images(pipe, User_Prompt, params)
