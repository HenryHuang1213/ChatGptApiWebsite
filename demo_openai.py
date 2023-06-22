'''
    -*- coding: utf-8 -*-
    Time : 2023/5/15 16:30
    Author : HenryHuang
    File : demo_openai.py
    Software: PyCharm
'''
__author__ = 'HenryHuang'


import openai
import streamlit as st
from streamlit_chat import message

openai.api_key_path = "api.key"
if 'prompts' not in st.session_state:
    st.session_state['prompts'] = [{"role": "system",
                                    "content": "You are a helpful assistant. Answer as concisely as possible."}]
if 'generated' not in st.session_state:
    st.session_state['generated'] = []
if 'past' not in st.session_state:
    st.session_state['past'] = []


def generate_response(prompt):
    st.session_state['prompts'].append({"role": "user", "content": prompt})
    completion = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=st.session_state['prompts']
    )

    message = completion.choices[0].message.content
    return message


def end_click():
    st.session_state['prompts'] = [{"role": "system",
                                    "content": "You are a helpful assistant. Answer as concisely as possible."}]
    st.session_state['past'] = []
    st.session_state['generated'] = []
    st.session_state['user'] = ""


def chat_click():
    if st.session_state['user'] != '':
        chat_input = st.session_state['user']
        output = generate_response(chat_input)
        # store the output
        st.session_state['past'].append(chat_input)
        st.session_state['generated'].append(output)
        st.session_state['prompts'].append({"role": "assistant", "content": output})
        st.session_state['user'] = ""

st.set_page_config(page_title="MoqiZhai", page_icon="moqizhai.png", layout="wide")
st.image("moqizhai.png", width=300)
st.title("My Chat Bot")

user_input = st.text_input("You:", key="user")

chat_button = st.button("Send", on_click=chat_click)
end_button = st.button("New Chat", on_click=end_click)

if st.session_state['generated']:
    for i in range(len(st.session_state['generated']) - 1, -1, -1):
        tab1, tab2 = st.tabs(["normal", "rich"])
        with tab1:
            message(st.session_state['generated'][i], key=str(i))
        with tab2:
            st.markdown(st.session_state['generated'][i])
        message(st.session_state['past'][i], is_user=True, key=str(i) + '_user')