with st.sidebar:
    st.title("Summarization Options")
    # Language Selection
    language = st.selectbox("Select Language", ["English", "Spanish", "French"])
    
    # Summary Type Selection
    summary_type = st.selectbox(
        "Select Summary Type",
        ["100 words", "2 connecting paragraphs", "5 bullet points"]
    ) 
    
    # Model Selection
    advanced_model = st.checkbox("Use advanced model") 
    model_to_use = "gpt-4o" if advanced_model else "gpt-4o-mini"
