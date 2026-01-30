import streamlit as st
from openai import OpenAI

# Show title and description
st.title("MY Document question answering")
st.write(
    "Upload a document below and ask a question about it – GPT will answer!"
)

# Access the key via Streamlit secrets
if "OPENAI_API_KEY" in st.secrets:
    openai_api_key = st.secrets["OPENAI_API_KEY"]
else:
    st.error("Please add your OpenAI API key to the Streamlit secrets file.")
    st.stop() # In case no key

# Create the OpenAI client using the secret key
client = OpenAI(api_key=openai_api_key)

# Let the user upload a file
uploaded_file = st.file_uploader(
    "Upload a document (.txt or .md)", type=("txt", "md")
)

if uploaded_file:
    # Process the file
    document = uploaded_file.read().decode()
    messages = [
        {
            "role": "user",
            "content": f"Here's a document: {document}",
        }
    ]

    # Generate an answer
    stream = client.chat.completions.create(
        model="gpt-4o-mini", 
        messages=messages,
        stream=True,
    )

    # Stream the response
    st.write_stream(stream)
