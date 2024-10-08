'''
    -*- coding: utf-8 -*-
    Time : 2024/10/08 17:26
    Author : HenryHuang
    File : demo_openai.py
    Software: PyCharm
'''
__author__ = 'HenryHuang'

import openai
import streamlit as st
from streamlit_chat import message
import uuid
import json
import os

openai.api_key_path = "api.key"

# Path to save conversation history
HISTORY_FILE = "chat_history.json"


# Load history from file
def load_history():
    try:
        if os.path.exists(HISTORY_FILE):
            with open(HISTORY_FILE, 'r') as f:
                st.session_state['conversations'] = json.load(f)
        else:
            st.session_state['conversations'] = {}  # Initialize as an empty dictionary
    except Exception as e:
        st.error(f"Error loading history: {e}")
        st.session_state['conversations'] = {}


# Save history to file
def save_history():
    try:
        with open(HISTORY_FILE, 'w') as f:
            json.dump(st.session_state['conversations'], f)
    except Exception as e:
        st.error(f"Error saving history: {e}")


# Initialize session state variables
if 'conversations' not in st.session_state:
    load_history()

if 'current_conversation' not in st.session_state:
    conversation_id = str(uuid.uuid4())  # Generate unique ID
    st.session_state['current_conversation'] = conversation_id
    st.session_state['conversations'][conversation_id] = {
        'model_choice': 'gpt-4',
        'prompts': [{"role": "system", "content": "You are a helpful assistant."}],
        'generated': [],
        'past': []
    }


# Function to generate response using selected model
def generate_response(prompt):
    conversation = st.session_state['conversations'][st.session_state['current_conversation']]
    conversation['prompts'].append({"role": "user", "content": prompt})
    try:
        completion = openai.ChatCompletion.create(
            model=conversation['model_choice'],
            messages=conversation['prompts']
        )
        message_content = completion.choices[0].message.content
    except Exception as e:
        st.error(f"Error generating response: {e}")
        message_content = "Sorry, there was an error."

    return message_content


# Function to start a new conversation
def new_chat():
    conversation_id = str(uuid.uuid4())  # New conversation ID
    st.session_state['current_conversation'] = conversation_id
    st.session_state['conversations'][conversation_id] = {
        'model_choice': 'gpt-4',  # default model
        'prompts': [{"role": "system", "content": "You are a helpful assistant."}],
        'generated': [],
        'past': []
    }
    st.session_state['user_input'] = ''
    save_history()


# Function to send a message
def send_message():
    user_input = st.session_state.get('user_input', '')
    if user_input:
        conversation = st.session_state['conversations'][st.session_state['current_conversation']]
        output = generate_response(user_input)
        # Store the conversation
        conversation['past'].append(user_input)
        conversation['generated'].append(output)
        conversation['prompts'].append({"role": "assistant", "content": output})
        st.session_state['user_input'] = ''
        save_history()


# Function to select a conversation
def select_conversation():
    st.session_state['current_conversation'] = st.session_state['selected_conversation']


# Sidebar for conversation history and model selection
with st.sidebar:
    st.title("Conversation History")

    if st.session_state['conversations']:
        # List all conversations for selection
        conversation_names = [f"Conversation {i + 1}" for i in range(len(st.session_state['conversations']))]
        conversation_ids = list(st.session_state['conversations'].keys())
        conversation_dict = dict(zip(conversation_names, conversation_ids))

        # Allow the user to select a conversation
        selected_name = st.selectbox("Select Conversation", conversation_names, key='selected_conversation_name',
                                     on_change=select_conversation)
        st.session_state['selected_conversation'] = conversation_dict[selected_name]
    else:
        st.write("No conversations yet.")

    st.button("New Chat", on_click=new_chat)

    # Model selection based on the current conversation
    current_conversation = st.session_state['conversations'][st.session_state['current_conversation']]
    current_model = current_conversation['model_choice']
    selected_model = st.selectbox(
        "Select Model",
        ("gpt-4", "gpt-4o-mini", "gpt-3.5-turbo"),
        index=["gpt-4", "gpt-4o-mini", "gpt-3.5-turbo"].index(current_model),
        key='model_choice'
    )
    st.session_state['conversations'][st.session_state['current_conversation']]['model_choice'] = selected_model

# Main chat interface
st.title("My Chat Bot")

# Display conversation
conversation = st.session_state['conversations'][st.session_state['current_conversation']]
if conversation['generated']:
    for i in range(len(conversation['generated'])):
        message(conversation['past'][i], is_user=True, key=f"{st.session_state['current_conversation']}_user_{i}")
        message(conversation['generated'][i], key=f"{st.session_state['current_conversation']}_bot_{i}")

# User input
st.text_input("You:", key='user_input', on_change=send_message)

