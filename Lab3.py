import streamlit as st
from openai import OpenAI

st.title("Lab 3: Chatbot with Memory")

# setup OpenAI Client
if "OPENAI_API_KEY" in st.secrets:
    client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])
else:
    st.error("Missing API Key in Secrets!")
    st.stop()

# initialize chat history
if "messages" not in st.session_state:
    # 10-year-old level 
    st.session_state.messages = [
        {"role": "system", "content": "You are a helpful assistant. Explain things so a 10-year-old can understand. After every answer, you must ask 'Do you want more info?'"}
    ]

# chat history
for message in st.session_state.messages:
    if message["role"] != "system":
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

# user input
if prompt := st.chat_input("What is on your mind?"):
    # Add user message to history
    st.session_state.messages.append({"role": "user", "content": prompt})
    
    with st.chat_message("user"):
        st.markdown(prompt)

    # conversation buffer
    system_prompt = st.session_state.messages[0]
    recent_history = st.session_state.messages[-5:] # get last 5 messages
    # Filter to not get the system prompt if in the last 5
    filtered_history = [msg for msg in recent_history if msg["role"] != "system"]
    messages_to_send = [system_prompt] + filtered_history

    # generate stream response
    with st.chat_message("assistant"):
        stream = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=messages_to_send,
            stream=True,
        )
        response = st.write_stream(stream)
    
    # save response to history
    st.session_state.messages.append({"role": "assistant", "content": response})

    # Part C refining?
