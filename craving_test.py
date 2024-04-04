import streamlit as st
import requests

API_URL = "https://vji09nl8h56lm84s.us-east-1.aws.endpoints.huggingface.cloud"

# Add a text input field for the token
token = st.text_input("Enter your token (after 'Bearer'):", key="token_input")

headers = {
    "Accept": "application/json",
    "Authorization": f"Bearer {token}",  # Use the user's input as the token
    "Content-Type": "application/json"
}

def query(payload):
    response = requests.post(API_URL, headers=headers, json=payload, timeout=90)
    return response.json()                                                                                                                                                                                              

def format_input(user_input):                                                                                   
    input_string = f"""<|im_start|>system 
                        You are an AI assistant. You will be given a task to extract emotion towards brands in a social media post. You must generate a very short answer<|im_end|>
                        <|im_start|>user
                        Keep your answer very very SHORT
                        Extract the beverage brands and products from the following Social Media Post in a list. Example - Coke, Sprite, Soda
                        Tell me the emotion expressed towards the brand in the following social media post. The emotion has to be only one of the following - ['amusement', 'excitement', 'joy', 'love', 'desire', 'optimism', 'caring', 'pride', 'admiration', 'gratitude', 'relief', 'approval', 'realization', 'surprise', 'curiosity', 'confusion', 'fear', 'nervousness', 'remorse', 'embarrassment', 'disappointment', 'sadness', 'grief', 'disgust', 'anger', 'annoyance', 'disapproval', 'contempt', 'neutral']. The brands or products must be extracted separately with emotions associated to each one. Every extracted brand or product must have an emotion associated. Social Media Post: {user_input} <|im_end|>                                                                             
                        <|im_start|>assistant"""
    return input_string

st.title("Project Merge Model Test 2.0")

# Create a session state to store chat history
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

# Create a container to hold the chat history
chat_container = st.container()

# Create a function to display the chat history
def display_chat_history():
    with chat_container:
        for i, chat in enumerate(st.session_state.chat_history):
            with st.container():
                st.markdown(f"**You:** {chat['user']}")
                if i == len(st.session_state.chat_history) - 1:
                    st.markdown(f"**AI:** {chat['assistant']}")
                else:
                    st.markdown(f"**AI:** {chat['assistant']}", unsafe_allow_html=True)

# Create an input field for the user
user_input = st.text_input("Type your message here:", key="user_input_active")
submit_button = st.button("Send")

# Add a button to clear the chat history
delete_history_button = st.button("Delete History")
if delete_history_button:
    st.session_state.chat_history = []

if submit_button and user_input:
    formatted_input = format_input(user_input)
    output = query({"inputs": formatted_input, "parameters": {}})
    generated_text = output[0]['generated_text']
    cleaned_text = generated_text.split(formatted_input)[-1].strip()
    cleaned_text = cleaned_text.replace("assistant", "")

    # Add user input and AI response to chat history
    st.session_state.chat_history.append({"user": user_input, "assistant": cleaned_text})

    # Clear the user input field
    st.text_input("Type your message here:", key="user_input_cleared", value="")

    # Display the updated chat history
    display_chat_history()
else:
    # Display the existing chat history
    display_chat_history()