# To Import the .env file
import os
from dotenv import load_dotenv
load_dotenv()

import streamlit as st
from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI
from langchain_core.messages import AIMessage, HumanMessage
from PIL import Image
from langchain_openai import ChatOpenAI

# Import the API keys from .env file
os.environ['OPENAI_API_KEY'] = os.getenv("OPENAI_API_KEY")

#----------------------------------------------------------------
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
st.markdown('<div class="custom-heading">1 . AI Chatbot🔍📝</div>', unsafe_allow_html=True)
st.markdown("<hr style='margin: 15px 0;'>", unsafe_allow_html=True)

st.write("***🤖 Ask away , your smart little helper is here 24/7 !***")

# Spacer
st.write("")
#---------------------------------------------------------------

# Initialize chat history in session state
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

# Display chat history
for msg in st.session_state.chat_history:
    with st.chat_message(msg["role"]):
        st.markdown(msg["text"])

# Chat input
user_input = st.chat_input("Type your message...")
if user_input:
    # Display user message
    with st.chat_message("user"):
        st.markdown(user_input)
    st.session_state.chat_history.append({"role": "user", "text": user_input})

    # Prepare chat history for the prompt
    history_text = "\n".join(
        f"{m['role'].capitalize()}: {m['text']}" for m in st.session_state.chat_history if m["role"] != "assistant"
    )

    # Create LangChain prompt
    template = """
    You are a helpful assistant. Use the conversation history to answer the user's question.
    Chat history:
    {chat_history}

    User question: {user_question}
    """
    prompt = ChatPromptTemplate.from_template(template)
    llm = ChatOpenAI(model="gpt-4o")

    # Build the chain and get streaming response
    chain = prompt | llm

    # Stream the response in Streamlit
    with st.chat_message("assistant"):
        response = chain.invoke({
            "chat_history": history_text,
            "user_question": user_input
        })
        st.markdown(response.content)
        st.session_state.chat_history.append({"role": "assistant", "text": response.content})
