import os
from dotenv import load_dotenv
load_dotenv()

# API keys
os.environ['HF_TOKEN'] = os.getenv("HF_TOKEN")
os.environ['OPENAI_API_KEY'] = os.getenv("OPENAI_API_KEY")

# Imports
import os
import re
import streamlit as st
import validators
from langchain_community.document_loaders import PyPDFDirectoryLoader, UnstructuredURLLoader
from langchain.schema import Document
from youtube_transcript_api import YouTubeTranscriptApi
from youtube_transcript_api._errors import (
    TranscriptsDisabled,
    NoTranscriptFound,
    VideoUnavailable,
    CouldNotRetrieveTranscript
)
from langchain.prompts import PromptTemplate
from langchain_openai import ChatOpenAI
from langchain.chains.summarize import load_summarize_chain

st.set_page_config(page_title=" Text Summarization", layout="wide")

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

# Header
st.markdown('<div class="custom-heading">Text Summarization 📝</div>', unsafe_allow_html=True)
st.markdown("<hr style='margin: 15px 0;'>", unsafe_allow_html=True)

# Summary length selector and model selector
model_selection, summary_style, length = st.columns([1, 1, 1])
with model_selection:
    model = st.selectbox("***Summarization Type*** ", ["StuffDocumentChain", "Map-Reduce", "Refine"])

with summary_style:
    Tone = st.selectbox("***Summarization Style*** ", ["Formal", "Casual", "Technical"])

with length:
    summary_length = st.slider("***Summary length***", min_value=50, max_value=200, step=50, value=100)

st.markdown("<hr style='margin: 15px 0;'>", unsafe_allow_html=True)

# Layout: inputs left, output right
input_col, output_col = st.columns([1, 1])

with input_col:
    generic_url = st.text_input("**YouTube URL ▶️ or Website URL 🌐**", placeholder="Enter URL here")
    st.markdown("""<div style='text-align: center; margin: 5px 0; font-size: 14px;'>OR</div>""", unsafe_allow_html=True)
    input_text = st.text_area("**Enter text to summarize 📝**", height=120, placeholder="Paste or type your text here...")
    st.markdown("""<div style='text-align: center; margin: 5px 0; font-size: 14px;'>OR</div>""", unsafe_allow_html=True)
    uploaded_files = st.file_uploader("**Choose a PDF File 📎**", type="pdf", accept_multiple_files=True)
    st.write("")

    col_left, col_center, col_right = st.columns([1, 1, 1])
    with col_center:
        summarize_clicked = st.button("Summarize")

with output_col:
    if summarize_clicked:
        docs = None

        # Handle PDF upload
        if uploaded_files and len(uploaded_files) > 0:
            os.makedirs("Data", exist_ok=True)
            for f in os.listdir("Data"):
                os.remove(os.path.join("Data", f))
            for file in uploaded_files:
                filepath = os.path.join("Data", file.name)
                with open(filepath, "wb") as f:
                    f.write(file.getvalue())
            loader = PyPDFDirectoryLoader("Data")
            docs = loader.load()

        # Handle generic URL / YouTube
        elif generic_url:
            if not validators.url(generic_url):
                st.error("Please enter a valid URL")
            else:
                with st.spinner("Loading content..."):
                    # YouTube video
                    youtube_match = re.search(r"(?:v=|youtu\.be/)([A-Za-z0-9_-]{11})", generic_url)
                    if youtube_match:
                        video_id = youtube_match.group(1)
                        try:
                            # Create instance of API
                            ytt_api = YouTubeTranscriptApi()
                            fetched = ytt_api.fetch(video_id, languages=['en'])
                            full_text = " ".join([entry.text for entry in fetched])
                            docs = [Document(page_content=full_text)]

                        except Exception as e:
                            st.error(f"Unexpected error fetching transcript: {e}")
                            docs = None
        
                    else:
                        # Generic website
                        st.write("entered else")
                        try:
                            loader = UnstructuredURLLoader(
                                urls=[generic_url_value],
                                ssl_verify=False,
                                headers={"User-Agent": "Mozilla/5.0"}
                            )
                            docs = loader.load()
                        except Exception as e:
                            st.error(f"Failed to load content from URL: {e}")
                            docs = None

        # Handle raw input text
        elif input_text:
            docs = [Document(page_content=input_text)]

        # Run summarization if docs are loaded
        if docs:
            prompt_template = f"""
            Content: {{text}}
            Style: {{Tone}}

            Summarize the above content in the given style.
            Use clear and concise language. Limit the summary to approximately {summary_length} words.
            """
            prompt = PromptTemplate(input_variables=["text", "Tone"], template=prompt_template)

            chain_type_map = {
                "StuffDocumentChain": "stuff",
                "Map-Reduce": "map_reduce",
                "Refine": "refine"
            }
            selected_chain_type = chain_type_map[model]

            llm = ChatOpenAI(model="gpt-4o")
            if selected_chain_type == "stuff":
                chain = load_summarize_chain(llm=llm, chain_type="stuff", prompt=prompt)
            elif selected_chain_type == "map_reduce":
                chain = load_summarize_chain(llm=llm, chain_type="map_reduce", combine_prompt=prompt)
            else:  # refine
                chain = load_summarize_chain(llm=llm, chain_type="refine", refine_prompt=prompt)

            output_summary = chain.run({"input_documents": docs, "Tone": Tone})
            st.markdown("### 📝 Summary:")
            st.success(output_summary)
        else:
            st.warning("No valid input source provided. Please upload a PDF, enter a URL, or paste text.")

