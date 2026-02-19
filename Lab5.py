import streamlit as st
from openai import OpenAI
import requests
import json

st.title("☁️ Lab 5: The 'What to Wear' Bot")

# setup API Keys
if "OPENAI_API_KEY" in st.secrets and "OPENWEATHER_API_KEY" in st.secrets:
    client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])
    weather_api_key = st.secrets["OPENWEATHER_API_KEY"]
else:
    st.error("Missing API Keys in Secrets! Please add OPENAI_API_KEY and OPENWEATHER_API_KEY.")
    st.stop()

# define the weather data function
def get_current_weather(location, api_key=weather_api_key, units='imperial'):
    # Check if the location is empty or just whitespace 
    if not location or location.strip() == "":
        location = "Syracuse, NY"
    
    url = f"https://api.openweathermap.org/data/2.5/weather?q={location}&appid={api_key}&units={units}"
    
    response = requests.get(url)
    
    # Handle errors
    if response.status_code == 401:
        raise Exception('Authentication failed: Invalid API key (401 Unauthorized)')
    if response.status_code == 404:
        # more descriptive error
        raise Exception(f"404 error. City '{location}' not found.")
        
    data = response.json()
    return {
        'location': location,
        'temperature': round(data['main']['temp'], 2),
        'feels_like': round(data['main']['feels_like'], 2),
        'description': data['weather'][0]['description']
    }

# define tools for OpenAI
tools = [
    {
        "type": "function",
        "function": {
            "name": "get_current_weather",
            "description": "Get the current weather for a specific location",
            "parameters": {
                "type": "object",
                "properties": {
                    "location": {
                        "type": "string",
                        "description": "The city and state, e.g. San Francisco, CA",
                    }
                },
                "required": ["location"],
            },
        },
    }
]

# streamlit UI
target_city = st.text_input("Enter a city (e.g., Syracuse, NY, US):", placeholder="Syracuse, NY")

if st.button("Get Advice"):
    # Handle default location if empty 
    query_location = target_city if target_city.strip() != "" else "Syracuse, NY"

    messages = [
        {"role": "system", "content": "You are a clothing advisor. Use the weather tool for the provided location. If no location is specified, use 'Syracuse, NY'."},
        {"role": "user", "content": f"I am in {query_location}. What should I wear?"}
    ]

    # Determine if tool is needed
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=messages,
        tools=tools,
        tool_choice="auto"
    )
    
    response_message = response.choices[0].message
    tool_calls = response_message.tool_calls

    # Determine if LLM wants to use the tool 
    if tool_calls:
        for tool_call in tool_calls:
            function_args = json.loads(tool_call.function.arguments)
            
            # Call the local weather function 
            try:
                weather_data = get_current_weather(function_args.get("location"))
                
                # 7. Second LLM Call: Provide weather data for advice 
                messages.append(response_message)
                messages.append({
                    "role": "tool",
                    "tool_call_id": tool_call.id,
                    "name": "get_current_weather",
                    "content": json.dumps(weather_data),
                })
                
                final_response = client.chat.completions.create(
                    model="gpt-4o-mini",
                    messages=messages,
                )
                
                # Display output
                st.subheader(f"Weather for {weather_data['location']}")
                st.write(f"**Temp:** {weather_data['temperature']}°F | **Feels Like:** {weather_data['feels_like']}°F")
                st.write(f"**Conditions:** {weather_data['description']}")
                st.divider()
                st.markdown(final_response.choices[0].message.content)
                
            except Exception as e:
                st.error(f"Error fetching weather: {e}")
