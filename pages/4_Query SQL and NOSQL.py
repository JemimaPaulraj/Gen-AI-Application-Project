# --------------------------Import Libraries---------------------------------
import streamlit as st
from pathlib import Path
import sqlite3
import pandas as pd
import os
from sqlalchemy import create_engine

from langchain.agents import create_sql_agent
from langchain.sql_database import SQLDatabase
from langchain.agents.agent_types import AgentType
from langchain.callbacks import StreamlitCallbackHandler
from langchain.agents.agent_toolkits import SQLDatabaseToolkit
from langchain_experimental.agents.agent_toolkits import create_pandas_dataframe_agent
from langchain.chat_models import ChatOpenAI
from pymongo import MongoClient
from langchain.schema import SystemMessage,HumanMessage

# ----------------------------Set OpenAI API Key--------------------------------------
os.environ['OPENAI_API_KEY'] = os.getenv("OPENAI_API_KEY")

# ----------------------------------------------------------
# Streamlit User Interface

st.set_page_config(page_title=" Query SQL and NOSQL", layout="wide")

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
    width: 100%; height: 80px; background-color: #C9BBCF;
    color: black; font-size: 20px; font-weight: bold;
    border-radius: 12px; display: flex; align-items: center;
    justify-content: center; box-shadow: 0 4px 8px rgba(0,0,0,0.1);
    margin-bottom: 20px;
}
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

st.markdown('<div class="custom-heading"> Query SQL and NOSQL Database</div>', unsafe_allow_html=True)

# ----------------------------Create Sidebar Options-----------------------------------
radio_opt = ["Connect to MySQL Database", "Connect to SQLite Database", "Connect to MongoDB Database", "Connect to Excel/CSV"]
selected_opt = st.sidebar.radio("Choose the DB you want to chat with:", options=radio_opt)

# Sidebar credentials
if radio_opt.index(selected_opt) == 0:  # MySQL
    db_uri = "USE_MYSQL"
    mysql_host = st.sidebar.text_input("Enter MySQL Host:")
    mysql_user = st.sidebar.text_input("User Name:")
    mysql_password = st.sidebar.text_input("Password:", type="password")
    mysql_db = st.sidebar.text_input("Database Name:")
elif radio_opt.index(selected_opt) == 1:  # SQLite
    db_uri = "USE_LOCALDB"
elif radio_opt.index(selected_opt) == 2:  # MongoDB
    db_uri = "USE_MONGODB"
    mongo_uri = st.sidebar.text_input("MongoDB Connection String (SRV or normal):")
    mongo_db = st.sidebar.text_input("Database Name:")
    mongo_collection_name = st.sidebar.text_input("Collection Name:")
else:  # Excel/CSV
    db_uri = "USE_EXCEL_CSV"
    uploaded_file = st.sidebar.file_uploader("Upload Excel or CSV file", type=["xlsx", "csv"])

# ----------------------------LLM Initialization--------------------------------------
llm = ChatOpenAI(model="gpt-4o", temperature=0)

# -----------------------Configure SQL Database----------------------------------------
@st.cache_resource(ttl="2h")
def configure_db(db_uri, mysql_host=None, mysql_user=None, mysql_password=None, mysql_db=None):
    if db_uri == "USE_LOCALDB":
        dbfilepath = (Path(__file__).parent / "student.db").absolute()
        creator = lambda: sqlite3.connect(f"file:{dbfilepath}?mode=ro", uri=True)
        return SQLDatabase(create_engine("sqlite:///", creator=creator))
    elif db_uri == "USE_MYSQL":
        if not (mysql_host and mysql_user and mysql_password and mysql_db):
            st.error("Please provide all MySQL connection details.")
            st.stop()
        engine = create_engine(
            f"mysql+mysqlconnector://{mysql_user}:{mysql_password}@{mysql_host}/{mysql_db}"
        )
        return SQLDatabase(engine)

# --------------------Connect to the Database------------------------------------------
db = None
collection = None
df = None
agent = None

if radio_opt.index(selected_opt) == 0:  # MySQL
    db = configure_db(db_uri, mysql_host, mysql_user, mysql_password, mysql_db)
elif radio_opt.index(selected_opt) == 1:  # SQLite
    db = configure_db(db_uri)
elif radio_opt.index(selected_opt) == 2:  # MongoDB
    if not (mongo_uri and mongo_db and mongo_collection_name):
        st.error("Please provide MongoDB connection details.")
        st.stop()
    client = MongoClient(mongo_uri)
    db_mongo = client[mongo_db]
    collection = db_mongo[mongo_collection_name]
else:  # Excel/CSV
    if uploaded_file is None:
        st.error("Please upload a file.")
        st.stop()
    if uploaded_file.name.endswith(".csv"):
        df = pd.read_csv(uploaded_file)
    else:
        df = pd.read_excel(uploaded_file, sheet_name=0)
    agent = create_pandas_dataframe_agent(
        llm,
        df,
        handle_parsing_errors=True,
        agent_type=AgentType.ZERO_SHOT_REACT_DESCRIPTION,
        verbose=True,
        allow_dangerous_code=True
    )

# -------------------Create SQL Toolkit and Agent--------------------------------------
if radio_opt.index(selected_opt) in [0, 1]:  # MySQL or SQLite
    toolkit = SQLDatabaseToolkit(db=db, llm=llm)
    agent = create_sql_agent(
        llm=llm,
        toolkit=toolkit,
        verbose=True,
        handle_parsing_errors=True,
        agent_type=AgentType.ZERO_SHOT_REACT_DESCRIPTION
    )

# ----------------Display the Output---------------------------------------------------
# Clear message history
if "messages" not in st.session_state or st.sidebar.button("Clear message history"):
    st.session_state["messages"] = [{"role": "assistant", "content": "Hi, how can I help you?"}]

# Display previous messages
for msg in st.session_state.messages:
    st.chat_message(msg["role"]).write(msg["content"])

# Handle user input
user_query = st.chat_input(placeholder="Ask anything from the database")

if user_query:
    st.session_state.messages.append({"role": "user", "content": user_query})
    st.chat_message("user").write(user_query)

    with st.chat_message("assistant"):
        st_cb = StreamlitCallbackHandler(st.container())
        try:
            if radio_opt.index(selected_opt) in [0, 1] or df is not None:
                # messages = [system_prompt, HumanMessage(content=user_query)]
                #response = agent.run(messages, callbacks=[st_cb])
                response = agent.run(user_query, callbacks=[st_cb])
            elif radio_opt.index(selected_opt) == 2 and collection is not None:
                # MongoDB handling
                docs = list(collection.find({}).limit(100))  # limit for safety
                data_str = "\n".join([str(doc) for doc in docs])
                prompt = f"You are a helpful assistant. Here is the data from MongoDB:\n{data_str}\nAnswer the user query: {user_query}"
                answer = llm([HumanMessage(content=prompt)])
                response = answer.content
            else:
                response = "No database connected."
            
            st.session_state.messages.append({'role': 'assistant', 'content': response})
            st.write(response)

        except Exception as e:
            st.error(f"Error: {str(e)}")
