import streamlit as st
from PIL import Image

st.set_page_config(page_title=" Home ", layout="wide")

st.markdown(
    "<h1 style='text-align: center; font-size: 30px;'>Generative AI Applications</h1>",
    unsafe_allow_html=True
)
# Spacer
st.markdown("<hr style='margin: 20px 0;'>", unsafe_allow_html=True)

st.markdown(
    """
    <style>
    div.stButton > button {
        width: 90%;
        height: 100px;
        background-color: #C9BBCF;
        color: black;
        font-size: 28px;
        font-weight: bold;
        border-radius: 12px;
        border: none;
        cursor: pointer;
        box-shadow: 0 4px 8px rgba(0,0,0,0.1);
        transition: all 0.3s ease-in-out;
    }
    div.stButton > button:hover {
        background-color: #E2DCE8;
        transform: scale(1.02);
    }
    .feature-box {
        padding: 10px 0;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# Create rows with clean alignment
with st.container():
    col1, col2, col3 = st.columns(3)

    with col1:
        st.markdown("##### 💬 AI Chatbot")
        st.markdown('<p style="color: grey; font-size: 14px; ">Responds intelligently to your questions.</p>', unsafe_allow_html=True)
        if st.button("AI ChatBot"):
            st.switch_page("pages/1_AI ChatBot.py")

    with col2:
        st.markdown("##### 🔍 Agentic RAG")
        st.markdown('<p style="color: grey; font-size: 14px; ">Search using AI-powered retrieval.</p>', unsafe_allow_html=True)
        if st.button("Retrieval Augmented Generation (RAG)"):
            st.switch_page("pages/2_Agentic RAG.py")

    with col3:
        st.markdown("##### 📝 Text Summarizer")
        st.markdown('<p style="color: grey; font-size: 14px; ">Turn long text into clear, concise summaries.</p>', unsafe_allow_html=True)
        if st.button("Text Summarization"):
            st.switch_page("pages/3_Text Summarization.py")

# Spacer
st.markdown("<hr style='margin: 20px 0;'>", unsafe_allow_html=True)

with st.container():
    col4, col5, col6 = st.columns(3)

    with col4:
        st.markdown("##### 🗄️ Query SQL / NOSQL")
        st.markdown('<p style="color: grey; font-size: 14px; ">Create images from your imagination using text.</p>', unsafe_allow_html=True)
        if st.button(" Query SQL / NOSQL "):
            st.switch_page("pages/4_Query SQL and NOSQL.py")

    with col5:
        st.markdown("##### 🎨 Image Generator")
        st.markdown('<p style="color: grey; font-size: 14px; ">Turn long text into clear, concise summaries.</p>', unsafe_allow_html=True)
        if st.button("Image Generator"):
            st.switch_page("pages/5_Image Generator.py")

    with col6:
        st.markdown("##### 🖼️ Image Captioning")
        st.markdown('<p style="color: grey; font-size: 14px; ">Create images from your imagination using text.</p>', unsafe_allow_html=True)
        if st.button("Image Captioning"):
            st.switch_page("pages/6_Image Captioning.py")
