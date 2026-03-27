import streamlit as st
from openai import OpenAI
from pydantic import BaseModel

# Setup OpenAI Client
if "OPENAI_API_KEY" in st.secrets:
    client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])
else:
    st.error("Missing OpenAI API Key in secrets!")
    st.stop()

st.title("Lab 6: OpenAI Responses Agent")

# Part D Define Pydantic Model
class ResearchSummary(BaseModel):
    main_answer: str
    key_facts: list[str]
    source_hint: str

# Sidebar
with st.sidebar:
    st.header("Agent Settings")
    use_structured = st.checkbox("Return structured summary")
    use_streaming = st.checkbox("Support streaming", value=True)
    st.caption("Web Search is enabled for this agent.")

# Part A/B UI for Questions
user_question = st.text_input("Ask a question:")
follow_up = st.text_input("Ask a follow-up question:")

# Helper function to run the response
def run_agent_call(query, is_follow_up=False):
    # get previous ID for chaining
    prev_id = st.session_state.get("last_response_id") if is_follow_up else None
    
    # Part D (chose parse)
    if use_structured:
        response = client.responses.parse(
            model="gpt-4o",
            instructions="You are a helpful research assistant. Cite your sources.",
            input=query,
            tools=[{"type": "web_search_preview"}], # Part C
            previous_response_id=prev_id,
            response_format=ResearchSummary
        )
    else:
        response = client.responses.create(
            model="gpt-4o",
            instructions="You are a helpful research assistant. Cite your sources.",
            input=query,
            tools=[{"type": "web_search_preview"}],
            previous_response_id=prev_id
        )
    
    # Store ID for next turn
    st.session_state.last_response_id = response.id
    return response

# Execution Logic
if user_question:
    st.subheader("Initial Response")
    res1 = run_agent_call(user_question)
    
    if use_structured:
        # Part D Structured Fields
        parsed = res1.parsed
        st.write(parsed.main_answer)
        st.write("**Key Facts:**")
        for fact in parsed.key_facts:
            st.write(f"- {fact}")
        st.caption(f"Source: {parsed.source_hint}")
    else:
        st.write(res1.output_text)

if follow_up:
    st.subheader("Follow-up Response")
    res2 = run_agent_call(follow_up, is_follow_up=True)
    
    if use_structured:
        parsed_f = res2.parsed
        st.write(parsed_f.main_answer)
        st.write("**Key Facts:**")
        for fact in parsed_f.key_facts:
            st.write(f"- {fact}")
        st.caption(f"Source: {parsed_f.source_hint}")
    else:
        st.write(res2.output_text)
