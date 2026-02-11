import streamlit as st
from openai import OpenAI
import chromadb
from chromadb.utils.embedding_functions import OpenAIEmbeddingFunction
import pypdf
import os

st.title("Lab 4: Course Information RAG Chatbot")

# Setup OpenAI Client
if "OPENAI_API_KEY" in st.secrets:
    openai_api_key = st.secrets["OPENAI_API_KEY"]
    client = OpenAI(api_key=openai_api_key)
else:
    st.error("Missing API Key!")
    st.stop()

# Function to create Vector Database
def get_vector_db():
    # Use OpenAI embeddings as requested in Lab 4 instructions
    model_name = "text-embedding-3-small"
    embedding_function = OpenAIEmbeddingFunction(
        api_key=openai_api_key, 
        model_name=model_name
    )
    
    # Initialize Chroma client
    chroma_client = chromadb.PersistentClient(path="./chroma_db")
    collection = chroma_client.get_or_create_collection(
        name="Lab4Collection", 
        embedding_function=embedding_function
    )
    
    # Check if empty
    if collection.count() == 0:
        # Define the path to your syllabus files
        data_folder = "./Lab-04-Data" # Adjust this path as needed
        
        for filename in os.listdir(data_folder):
            if filename.endswith(".pdf"):
                path = os.path.join(data_folder, filename)
                
                # Extract text from PDF
                reader = pypdf.PdfReader(path)
                text = ""
                for page in reader.pages:
                    text += page.extract_text()
                
                # Add to ChromaDB with filename as ID and in metadata
                collection.add(
                    documents=[text],
                    ids=[filename],
                    metadatas=[{"source": filename}]
                )
    return collection

# Initialize Vector darabase
if "Lab4_VectorDB" not in st.session_state:
    with st.spinner("Initializing Vector Database..."):
        st.session_state.Lab4_VectorDB = get_vector_db()

# Initialize Chat History
if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "system", "content": "You are a helpful assistant. Use the provided context from course syllabi to answer questions. If the information is not in the context, be clear about that."}
    ]

# Display Chat
for message in st.session_state.messages:
    if message["role"] != "system":
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

# RAG Logic
if prompt := st.chat_input("Ask about the courses:"):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # Search the Vector for the top 3 chunks
    results = st.session_state.Lab4_VectorDB.query(
        query_texts=[prompt],
        n_results=3
    )
    
    # Prepare the context
    context = "\n\n".join(results['documents'][0])
    
    # System Prompt with retrieved context
    rag_prompt = f"Use the following course information to answer the user: \n\n {context}"
    
    # Prepare messages for the LLM
    # We include the original system message, the new RAG context, and recent history
    messages_to_send = [
        {"role": "system", "content": rag_prompt},
        *st.session_state.messages[-5:] # Last 5 messages for memory
    ]

    # Generation Step
    with st.chat_message("assistant"):
        stream = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=messages_to_send,
            stream=True,
        )
        response = st.write_stream(stream)
    
    st.session_state.messages.append({"role": "assistant", "content": response})
