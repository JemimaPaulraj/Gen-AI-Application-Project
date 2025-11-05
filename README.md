# 🚀 Gen AI Application Project

This project is a multi-functional Generative AI application built with Streamlit and powered by featuring six powerful Generative AI capabilities: AI Chatbot, Agentic RAG, Text Summarization, Database Querying, Image Generation, and Image Captioning.

**Web App Link** : https://generative-ai-application-jemimapaulraj.streamlit.app/

<img width="975" height="502" alt="image" src="https://github.com/user-attachments/assets/c747b6d0-f5ee-4a74-a291-01e8a7e8c9c0" />

<img width="3047" height="1471" alt="image" src="https://github.com/user-attachments/assets/77f675d8-2ae3-4bdb-a523-2aad407a74c7" />



## Features Overview 

1. AI Chatbot 💬 : Interactive conversational AI assistant for general questions and tasks
2. Agentic RAG 🔍 : Intelligent document retrieval and question answering with external tool integration.
3. Text Summarization 📝 : AI-powered text summarization that condenses documents or articles into concise, easy-to-read summaries
4. Query SQL/NoSQL 🗄️ : Natural language interface to database querying.
5. Image Generator 🎨: Generate images from text descriptions using AI.

## ✨ Features Descriptions

### 1. AI Chatbot 💬

**Purpose**: Interactive AI assistant powered by OpenAI GPT-4o. Maintains context-aware conversations with real-time streaming responses in a clean, intuitive interface.

**How it works**:
- Uses OpenAI GPT-4o to interpret user queries and generate relevant responses.
- Keeps track of conversation history to provide context-aware answers.
- Responds in real-time, enabling smooth multi-turn interactions.

**Usage**:
1. Click "AI ChatBot" from the home page
2. Type your question in the chat input
3. Press Enter to receive a response
4. Continue the conversation naturally

**Use Cases**: Q&A, brainstorming ideas, coding help, writing assistance, quick information lookup.

### 2. Agentic RAG 🔍

**Purpose**: Intelligent document retrieval & Q&A with multiple context-aware agents for tool selection, document fetching, relevance scoring, and query refinement via LangGraph—integrated with external tools for up-to-date information.

**How it works**:
- **Document Processing**: Uploads PDFs or scrapes websites
- **Embeddings**: Uses HuggingFace all-MiniLM-L6-V2 for text embeddings
- **Vector Storage**: FAISS for efficient similarity search
- **Agentic Workflow**: LangGraph orchestrates tool calls
- **Tool Selection**: AI agent dynamically chooses appropriate tools
- **Answer Generation**: Combines retrieved information with LLM reasoning

**Workflow**:
1. **Agent Node**: Decides which tool to use
2. **Retrieve Node**: Fetches relevant documents using selected tool
3. **Grade Documents**: Evaluates relevance of retrieved information
4. **Generate/Rewrite**: Generates answer or rewrites query if documents aren't relevant

**Usage**:
1. Upload PDF document(s) OR enter a website URL
2. Select additional tools from sidebar (Google Search, Wikipedia, Arxiv, Weather)
3. Click "Submit" to process documents
4. Ask questions in the chat interface
5. The agent will automatically:
   - Search your documents
   - Use external tools if needed
   - Grade relevance
   - Provide comprehensive answers

**Tool Descriptions**:
- **Domain Retriever**: Searches your uploaded PDFs/URLs
- **Google Search**: Real-time web search
- **Wikipedia**: Encyclopedia lookups
- **Arxiv**: Scientific paper retrieval
- **Weather**: Current weather information

**Use Cases**: Technical documentation Q&A, Real-time fact-checking, Research paper analysis, Technical documentation Q&A, Multi-source information synthesis

### 3. Text Summarization 📝

**Purpose**: AI-powered text summarization that condenses documents or articles into concise, easy-to-read summaries using various chain types (Stuff, Map-Reduce, Refine), while allowing control over style and length.

**How it works**:
- **Input Processing**: Handles multiple input types like Youtube URL, Website URL, PDF uploads, Text
- **Chain Types**:
  - **Stuff**: Combines all text at once (fast, for shorter docs)
  - **Map-Reduce**: Summarizes chunks then combines (for longer docs)
  - **Refine**: Iteratively refines summary (highest quality)
- **Style Control**: Adjusts tone and format
- **Length Control**: Limits output to specified word count

**Usage**:
1. Configure settings:
   - **Summarization Type**: Choose chain type
   - **Style**: Formal, Casual, or Technical
   - **Length**: 50-200 words
2. Provide input:
   - **YouTube URL**: Extracts and summarizes transcript
   - **Website URL**: Scrapes and summarizes content
   - **Direct Text**: Paste text to summarize
   - **PDF Upload**: Upload document(s)
4. Click "Summarize" and view the summarized content.

**Best Practices**:
- Use **Stuff** for documents < 4000 tokens
- Use **Map-Reduce** for very long documents
- Use **Refine** when quality is more important than speed

**Use Cases**: Article summarization, Video content summarization, Academic paper summarization, Meeting notes condensation

### 4. Query SQL/NoSQL 🗄️

**Purpose**: Provides a natural language interface for querying and analyzing structured and semi-structured data across SQL, NoSQL, and spreadsheet formats, enabling fast insights, reporting, and exploration without writing code.

**How it works**:
- **Supported Databases**: MySQL, SQLite, MongoDB, Excel/CSV
- **SQL Agent**: Uses LangChain SQL agent with toolkit
- **Pandas Agent**: For CSV/Excel file analysis
- **MongoDB Handler**: Direct query generation for NoSQL

**Usage**:

**For MySQL**: Remote/cloud databases
1. Select "Connect to MySQL Database"
2. Enter connection details (host, username, password, database name) in sidebar
3. Ask questions like:
   - "Show me all tables"
   - "What is the total revenue by region?"
   - "Find top 10 customers by sales"

**For SQLite**:
1. Select "Connect to SQLite Database"
2. Upload your .db file
3. Query naturally

**For MongoDB**:
1. Select "Connect to MongoDB Database"
2. Enter connection string, database, and collection
3. Ask questions about your data

**For Excel/CSV**:
1. Select "Connect to Excel/CSV"
2. Upload your file
3. Ask analytical questions

**Example Queries**:
- "How many records are in the database?"
- "What's the average age of customers?"
- "Show me sales trends by month"
- "Which product category has the highest revenue?"
- "Find all orders from last week"

**Use Cases**: Data exploration, Report generation, Data validation, Business intelligence


### 5. Image Generator 🎨

**Purpose**: Generate beautiful images from text descriptions using light weight Stable Diffusion models


**How it works**:
- **Model**: Uses Stable Diffusion pipelines - Segmind Small-SD (Light weight)
- **Process**:
  1. Text prompt encoded into latent space
  2. Iterative denoising (30 steps)
  3. Image decoded from latent representation


**Usage**:
1. Navigate to "Image Generator"
2. Configure settings:
   - **Model**: Choose generation model
   - **Image Size**: 256x256 or 512x512
   - **Number of Images**: 1-3 images per prompt
3. Enter your text prompt
4. Click "Generate"
5. Wait for generation (5 to 10 minutes on CPU, 0-5 minutes on GPU)

**Example Prompts**:
- "A girl with a rainbow hair, holding a flower"
- "A dog with a Christmas hat"

**Use Cases**: Concept art creation, Marketing visuals, Social media content, Storyboarding, Product mockups


### 6. Image Captioning 🖼️

**Purpose**: Generate descriptive text captions for images.

**How it works**:
- **Model**: Salesforce BLIP (Bootstrapping Language-Image Pre-training)
- **Process**:
  1. Image preprocessed and converted to tensors
  2. Visual features extracted
  3. Language model generates caption
  4. Caption decoded to text

**Usage**:
1. Navigate to "Image Captioning"
2. Upload an image (JPG, JPEG, or PNG)
3. Click "Generate Caption"
4. View the AI-generated description

**Example Outputs**:
- Input: Photo of a dog playing in a park
  - Output: "a dog playing with a ball in the grass"
- Input: City skyline at sunset
  - Output: "a city skyline with buildings and a sunset in the background"

**Use Cases**: Image accessibility, Image organization and tagging

## ⚡ Quick Start Commands

1. Clone the repository
git clone <your-repo-url>
cd Gen-AI-Application-Project

2. Create and activate virtual environment
python -m venv venv
venv\Scripts\activate

3. Install dependencies
pip install -r requirements.txt

4. Configure environment
Edit .env with your API keys

5. Run the application
streamlit run Home.py
