import streamlit as st
import json
import os
from openai import OpenAI

# page setup
st.title("Chatbot with Long-Term Memory")

# setup OpenAI client
if "OPENAI_API_KEY" in st.secrets:
    client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])
else:
    st.error("Missing API Key in Secrets!")
    st.stop()

MEMORY_FILE = "memories.json"

#create memor system

def load_memories():
    """Loads memories from a JSON file."""
    if os.path.exists(MEMORY_FILE):
        with open(MEMORY_FILE, "r") as f:
            return json.load(f)
    return []

def save_memories(memories):
    """Saves a list of memories to a JSON file."""
    with open(MEMORY_FILE, "w") as f:
        json.dump(memories, f)

# sidebar
with st.sidebar:
    st.header("Memory Bank")
    current_memories = load_memories()
    
    if current_memories:
        for mem in current_memories:
            st.write(f"• {mem}")
    else:
        st.write("No memories yet. Start chatting!")
    
    if st.button("Clear All Memories"):
        save_memories([])
        st.rerun()

# chatbot

# initialize session state for short-term chat history
if "messages" not in st.session_state:
    st.session_state.messages = []

# display chat history
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# ui
if prompt := st.chat_input("Tell me something about yourself!"):
    # Add user message to UI/History
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # Inject memories into the system prompt
    memories_str = ", ".join(current_memories) if current_memories else "None"
    system_prompt = f"""You are a helpful assistant. 
    Here are things you remember about this user from past conversations: {memories_str}
    Use this information to be more personal in your responses."""

    # Generate response
    messages_to_send = [{"role": "system", "content": system_prompt}] + st.session_state.messages
    
    with st.chat_message("assistant"):
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=messages_to_send
        )
        assistant_reply = response.choices[0].message.content
        st.markdown(assistant_reply)
    
    st.session_state.messages.append({"role": "assistant", "content": assistant_reply})

    # Extract new memories
    extraction_prompt = f"""
    Analyze the following conversation exchange and extract new permanent facts about the user 
    (name, location, preferences, etc.). 
    Existing memories: {memories_str}
    ONLY return new facts that are not already in existing memories.
    Return the facts as a simple JSON list of strings. If no new facts, return [].
    
    User: {prompt}
    Assistant: {assistant_reply}
    """
    
    try:
        extract_res = client.chat.completions.create(
            model="gpt-4o-mini", # Using mini for efficiency
            messages=[{"role": "system", "content": extraction_prompt}],
            response_format={ "type": "json_object" }
        )
        # Parse the JSON from the LLM
        raw_output = json.loads(extract_res.choices[0].message.content)
        # Assuming the LLM follows the "list of strings" instruction
        new_facts = raw_output.get("facts", raw_output.get("new_facts", []))
        
        if isinstance(new_facts, list) and len(new_facts) > 0:
            updated_memories = current_memories + new_facts
            save_memories(updated_memories)
            st.rerun() # Refresh to show new memories in sidebar
            
    except Exception as e:
        st.error(f"Memory extraction failed: {e}")
