#========================================================== 
# 🚀 RAG With Memory + Dynamic Tools 
# ==========================================================

import os 
from dotenv import load_dotenv 
load_dotenv()

# API keys
os.environ['HF_TOKEN'] = os.getenv("HF_TOKEN")
os.environ['OPENAI_API_KEY'] = os.getenv("OPENAI_API_KEY")
os.environ["GOOGLE_API_KEY"] = os.getenv("GOOGLE_API_KEY")
os.environ["GOOGLE_CSE_ID"] = os.getenv("GOOGLE_CSE_ID")

# ----------------------------------------------------------
# Imports
# ----------------------------------------------------------

import streamlit as st
from pathlib import Path
from langchain_community.document_loaders import PyPDFDirectoryLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS
from langchain.tools.retriever import create_retriever_tool
from langchain.utilities import DuckDuckGoSearchAPIWrapper, WikipediaAPIWrapper, ArxivAPIWrapper
from langchain_community.tools import DuckDuckGoSearchResults
from langchain.utilities import GoogleSearchAPIWrapper
from langchain.tools import Tool
from langchain_openai import ChatOpenAI
from langchain.prompts import PromptTemplate
from langchain_community.tools.arxiv.tool import ArxivQueryRun
from langchain_community.tools.wikipedia.tool import WikipediaQueryRun
from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages
from langgraph.prebuilt import ToolNode, tools_condition
from langchain_core.messages import AnyMessage, HumanMessage, SystemMessage
from langgraph.checkpoint.memory import MemorySaver
from pydantic import BaseModel, Field
from typing_extensions import TypedDict
from typing import Annotated, Literal
from langgraph.checkpoint.memory import MemorySaver
from langchain_community.document_loaders import WebBaseLoader
from langchain_core.output_parsers import StrOutputParser
import requests
from langchain import hub

# ----------------------------------------------------------
# Streamlit User Interface
# ----------------------------------------------------------

st.set_page_config(page_title=" Agentic RAG ", layout="wide")

st.markdown("""
<style>
/* Remove extra space at top of page */
main .block-container {
    padding-top: 0rem;
    padding-left: 2rem;
    padding-right: 2rem;
}
/* MultiSelect tag styling */
.stMultiSelect [data-baseweb="tag"] {
    background-color: #C8A2C8 !important;
    color: white !important;
    border: none !important;
}
.stMultiSelect [data-baseweb="tag"] [aria-label="remove"] svg {
    color: white !important;
}
/* Header and button styling */
.custom-heading {
    width: 100%;
    height: 80px;
    background-color: #C9BBCF;
    color: black;
    font-size: 20px;
    font-weight: bold;
    border-radius: 12px;
    display: flex;
    align-items: center;
    justify-content: center;
    box-shadow: 0 4px 8px rgba(0,0,0,0.1);
    margin-bottom: 20px;
}
div.stButton > button {
    background-color: #C9BBCF !important;
    color: black !important;
    font-size: 16px !important;
    font-weight: bold !important;
    border-radius: 8px !important;
    padding: 10px 24px !important;
    box-shadow: 0 2px 4px rgba(0,0,0,0.1) !important;
    margin-top: 10px !important;
}
div.stButton > button:hover {
    background-color: #E2DCE8 !important;
    transform: scale(1.03) !important;
}
</style>
""", unsafe_allow_html=True)

st.markdown('<div class="custom-heading">RAG - Retrieval Augmented Generation 🔍</div>', unsafe_allow_html=True)

# ----------------------------------------------------------
# File Upload / URL Input
# ----------------------------------------------------------

col3, col4, col5, col6 = st.columns([1, 0.1, 1, 0.3])
with col3:
    uploaded_files = st.file_uploader("**Upload your document 📎**", type="pdf", accept_multiple_files=True)
with col4:
    for _ in range(4):
        st.write("")
    st.write("**OR**")
with col5:
    generic_url = st.text_area("**Website URL 🌐**", height=75, placeholder="Enter URL here")
with col6:
    for _ in range(2):
        st.write("")
    submit_clicked = st.button("Submit")

st.markdown("<hr style='margin: 15px 0;'>", unsafe_allow_html=True)

# ----------------------------------------------------------
# Session State Setup
# ----------------------------------------------------------

model_global = ChatOpenAI(model="gpt-4o")



# ----------------------------------------------------------
# Sidebar: Additional Tools
# ----------------------------------------------------------

st.sidebar.header("🧰 Select Additional Tools")
available_tools = [
    "Google Search",
    "Wikipedia",
    "Arxiv",
    "Weather"
]
selected_tool_names = st.sidebar.multiselect(
    "Choose tools to include along with your PDF retriever:",
    options=available_tools,
    default=["Google Search"]
)
st.sidebar.markdown("---")
st.sidebar.info("✅ These tools will be bound with the PDF retriever tool automatically.")

# ----------------------------------------------------------
# Create Vector Embeddings & Tools
# ----------------------------------------------------------

def create_vector_embedding():
    if st.session_state.uploaded_files:
        os.makedirs("Data", exist_ok=True)
        for file in st.session_state.uploaded_files:
            with open(os.path.join("Data", file.name), "wb") as f:
                f.write(file.getvalue())
    
        loader = PyPDFDirectoryLoader("Data")
        docs = loader.load()
    
    elif st.session_state.generic_url:
        try:
            docs = WebBaseLoader(st.session_state.generic_url).load()
        except Exception as e:
            st.error(f"⚠️ Failed to load the URL..")
            st.stop()

    splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=50)
    final_docs = splitter.split_documents(docs)

    embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-V2")
    db = FAISS.from_documents(final_docs, embeddings)
    retriever = db.as_retriever()

    # Base retriever tool (always included)
    retriever_tool = create_retriever_tool(
        retriever,
        name="Domain_Retriever",
        description="Use this tool to search uploaded PDFs or website URLs for relevant information."
    )

    # Initialize tool list
    tools_list = [retriever_tool]

    # Dynamically add selected tools
    if "Wikipedia" in selected_tool_names:
        wiki = WikipediaAPIWrapper()
        tools_list.append(
            Tool(name="Wikipedia_Search", func=wiki.run, description="Searches Wikipedia for factual info.")
        )
        
    if "Google Search" in selected_tool_names:
        google_api_key = os.environ.get("GOOGLE_API_KEY")
        google_cse_id = os.environ.get("GOOGLE_CSE_ID")
    
        if not google_api_key or not google_cse_id:
            st.error("⚠️ GOOGLE_API_KEY or GOOGLE_CSE_ID is missing.")
        else:
            google_search = GoogleSearchAPIWrapper(
                google_api_key=google_api_key,
                google_cse_id=google_cse_id
            )
            tools_list.append(
                Tool(
                    name="Web_Search",
                    func=google_search.run,
                    description="Search the web using Google Search API."
                )
            )
        
    if "Arxiv" in selected_tool_names:
        arxiv = ArxivAPIWrapper()
        tools_list.append(
            Tool(name="Arxiv_Search", 
                 func=arxiv.run,description=(
                "Use this tool to fetch abstracts, summaries, or details from scientific papers on arXiv. "
                "Always use this tool when the user asks about, references, or mentions any research paper, "
                "including requests to summarize, explain, compare, or find authors/titles of scientific papers. "
                "Do not answer from your own knowledge — call this tool directly for all paper-related queries.")))

    if "Weather" in selected_tool_names:
        tools_list.append(
            Tool(
                name="Weather_Info",
                func=lambda location: requests.get(f"http://wttr.in/{location}?format=3").text,
                description="Fetches current weather for any city eg. boston and responds short weather info as text"))

    st.session_state.tools = tools_list
    st.session_state.final_docs = final_docs

# ----------------------------------------------------------
# Build LangGraph
# ----------------------------------------------------------
def build_Graph():
    if st.session_state.graph is not None:
        return
    tools = st.session_state.tools
    
    
    class State(TypedDict):
        messages: Annotated[list[AnyMessage], add_messages]

    def agent(state: State):
        """
        Invokes the agent to generate a response based on the current state.
        Given the question, it will decide to retrieve using the retriever tool, or simply end.
    
        Args:
        state (messages} : The current state
    
        Returns:
        dict: The updated state with the agent response appended to the messages
        """
        print("🧩 Node: Entering agent Node")
        model_with_tools = model_global.bind_tools(tools)
        response = model_with_tools.invoke(state["messages"])
        print("response from agent : ",response)
        return {"messages": [response]}

    def grade_documents(state: State) -> Literal["generate", "rewrite"]:
        """
        Determines whether the retrieved documents are relevant to the question.
    
        Args:
        state (messages} : The current state
    
        Returns:
        str: A decision for whether the documents are relevant or not
        """
        print("🧩 Node: Entering grade_documents")
        class Grade(BaseModel):
            binary_score: str = Field(description="Relevance score 'yes' or 'no'")

        model_with_tools_validation = model_global.with_structured_output(Grade)
        
        template = """You are a grader assessing relevance of a retrieved document to a user question. 
        Here is the retrieved document:
        {context}
        Here is the user question: {question}
        If the document contains keywords or semantic meaning related to the user question, grade it as relevant.
        Give a binary score 'yes' or 'no' to indicate whether the document is relevant to the question."""
        
        prompt = PromptTemplate(template=template, input_variables=["context", "question"])
        chain = prompt | model_with_tools_validation

        
        messages = state["messages"]

        for msg in reversed(messages):
            if isinstance(msg, HumanMessage):
                question = msg.content
                break
        
        print("Context for this particular question:",messages[-1].content)
        
        context = messages[-1].content
        # question = state["messages"][0].content
        print("final question :", question)
        scored_result = chain.invoke({"context": context, "question": question})
    
        score = scored_result.binary_score # Condition if the score is 'yes' or 'no'

        print(f"✅ Decision: {score}")
    
        if score == "yes": # docs relevant
            return "generate"
    
        else: # docs not relevant
            return "rewrite"

    def generate(state: State):
        """
        Generate the answer
    
        Args : 
        state (messages} : The current state
    
        Returns:
        str: The updated Message
        """
        print("🧩 Node: Entering generate")
        messages = state["messages"]

        for msg in reversed(messages):
            if isinstance(msg, HumanMessage):
                question = msg.content
                break
                
        context = state["messages"][-1].content
        llm = model_global
        prompt = hub.pull("rlm/rag-prompt")
        rag_chain = prompt|llm|StrOutputParser()
        response = rag_chain.invoke({"context":context,"question":question})
        print(f"🪄 Final answer from generate node: {response}")
        return {"messages": [response]}

    def rewrite(state: State):
        """ 
        Transform the query to produce a better question.
    
        Args : 
        state (messages} : The current state
    
        Returns:
        str: The updated state with rephrased question
        """
        print("🧩 Node: Entering rewrite")
        messages = state["messages"]

        for msg in reversed(messages):
            if isinstance(msg, HumanMessage):
                question = msg.content
                break
        # question = state["messages"][0].content
        llm = model_global
        msg = [HumanMessage( content=f"""\n
        Look at the input and try to reason about the underlying semantic intent/meaning. \n
        Here is the initial question:
        \n-----\n
        {question}
        \n-----\n
        Formulate an improved question: """)]
        response = llm.invoke(msg)
        print(f"✍️ Rewritten query: {response}")
        return {"messages": [response]}


    builder = StateGraph(State)
    builder.add_node("agent", agent)
    builder.add_node("retrieve", ToolNode(st.session_state.tools))
    builder.add_node("generate", generate)
    builder.add_node("rewrite", rewrite)

    builder.add_edge(START, "agent")
    builder.add_conditional_edges("agent", tools_condition, {"tools": "retrieve", END: END}) # if tool call happened go to retrieve node else to END
    builder.add_conditional_edges("retrieve", grade_documents)
    builder.add_edge("generate", END)
    builder.add_edge("rewrite", "agent")
    memory = MemorySaver()
    st.session_state.graph = builder.compile(checkpointer=memory)

# ----------------------------------------------------------
# Execute Pipeline
# ----------------------------------------------------------
    
if submit_clicked:
    st.session_state.tools = []
    st.session_state.graph = None
    st.session_state.chat_history = []
    st.session_state.thread_id = "chat-thread-1"
    st.session_state.graph_prompted = False
    st.session_state.uploaded_files = uploaded_files or []
    st.session_state.generic_url = generic_url or ""

    if st.session_state.uploaded_files or st.session_state.generic_url:
        with st.spinner("Processing and setting up tools..."):
            create_vector_embedding()
            # Ensure tools exist before graph
            if "tools" not in st.session_state or not st.session_state.tools:
                st.error("⚠️ Tools could not be created. Please check your file uploads or selections.")
            else:
                build_Graph()

    if not st.session_state.get("graph_prompted"):
        st.session_state.chat_history.append({"role": "assistant", "content": "Hello! How can I assist you today?"})
        st.session_state.graph_prompted = True

# ----------------------------------------------------------
# Chat Interaction
# ----------------------------------------------------------
user_input = st.chat_input("Type your question here...")
if user_input:
    st.session_state["user_input"] = user_input
    if not st.session_state.get("graph"):
        st.error("⚠️ Please upload a PDF and click Submit before chatting!")
    else:
        st.session_state.chat_history.append({"role": "user", "content": user_input})

        response = st.session_state.graph.invoke(
            {"messages": [HumanMessage(content=user_input)]},
            config={"configurable": {"thread_id": st.session_state.thread_id}}
        )
        ai_message = response["messages"][-1].content
        st.session_state.chat_history.append({"role": "assistant", "content": ai_message})

# ----------------------------------------------------------
# Display Chat History
# ----------------------------------------------------------

for msg in st.session_state.get("chat_history", []):
    if isinstance(msg, dict) and "content" in msg and "role" in msg:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])
