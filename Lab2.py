import streamlit as st
from openai import OpenAI

# Update title
st.title("Lab 2: Document Summarizer")
# Get the key via Streamlit secrets
if "OPENAI_API_KEY" in st.secrets:
    client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])
else:
    st.error("Missing API Key in Secrets!")
    st.stop()

# Sidebar configuration for user selections
with st.sidebar:
    # Language Selection dropdown
    language = st.selectbox("Select Language", ["English", "Spanish", "French"])
    
    # Summary Type dropdown
    summary_type = st.selectbox(
        "Select Summary Type", 
        ["100 words", "2 connecting paragraphs", "5 bullet points"]
    )
    
    # Checkbox for advanced model
    use_advanced = st.checkbox("Use advanced model") 
    
    # Model choice logic
    model_choice = "gpt-4o" if use_advanced else "gpt-4o-mini" 

# File Uploader for the document
uploaded_file = st.file_uploader("Upload a document", type=("txt", "md", "pdf"))

if uploaded_file:
    # Process the document
    document_content = uploaded_file.read().decode()
    
    # Create the prompt using instructions from the sidebar
    # Note: The user no longer types in a question
    prompt = f"Summarize the following document in {language}. The summary should be: {summary_type}."
    
    messages = [
        {"role": "system", "content": prompt},
        {"role": "user", "content": f"Here is the document content: {document_content}"}
    ]

    # Generate the summary
    response = client.chat.completions.create(
        model=model_choice,
        messages=messages
    )
    
    # Display the final summary
    st.subheader("Summary")
    st.write(response.choices[0].message.content)
