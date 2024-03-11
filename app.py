'''
Chat Bot using OpenAI API
'''

from openai import OpenAI
import streamlit as st
import json
from functions import get_current_weather, send_email, tools
import os
import base64
import requests
from utils import Base, Chat, Chat_Line
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.sql import exists
from anthropic import Anthropic

# Connect to the database
engine = create_engine('sqlite:///data/chat_database.db')  # Make sure this matches the URI you used to create the db
Session = sessionmaker(bind=engine)

# Create a session
session = Session()

st.set_page_config(page_title="Saksham's Chatbot", layout="wide", page_icon='🤖', menu_items={
                                        'Get Help': 'https://www.sakshambhutani.xyz',
                                        'Report a bug': "https://www.sakshambhutani.xyz",
                                        'About': "This is a chatbot (i.e. wrapper around LLMs). This is an *extremely* cool chatbot provides options to use OpenAI and Anthropic models!"
                                    }
    )

openai_client = OpenAI()

api_key = os.environ.get("OPENAI_API_KEY")

anthropic_client = Anthropic(
    # This is the default and can be omitted
    api_key=os.environ.get("ANTHROPIC_API_KEY"),
)

system_prompt = ""

# models and input/output token price per million tokens (in USD), and if tools are allowed
models = {'gpt-4-0613' : [30.00, 60.00, True],
          'gpt-4-0125-preview' : [30.00, 60.00, True],
          'gpt-4-1106-vision-preview' : [10.00, 30.00, False],
          'gpt-3.5-turbo-0125' : [0.50, 1.50, True],
          'claude-3-opus-20240229': [15.00, 75.00, True],
          'claude-3-sonnet-20240229': [3.00, 15.00, True]
          }

def call_function(tool_call):
    available_functions = {
        "get_current_weather": get_current_weather,
        "send_email": send_email
    }
    
    for tool_call in tool_calls:
        function_name = tool_call.function.name
        function_to_call = available_functions[function_name]
        function_args = json.loads(tool_call.function.arguments)
        function_response = function_to_call(**function_args)
        st.session_state.backend_messages.append(
            {
                "tool_call_id": tool_call.id,
                "role": "tool",
                "name": function_name,
                "content": function_response,
            }
        )

    with st.spinner("Processing results..."):
        second_response = openai_client.chat.completions.create(
            model=st.session_state.model,
            messages=st.session_state.backend_messages,
        )
        model_reply = response.model
        input_tokens = response.usage.completion_tokens
        output_tokens = response.usage.prompt_tokens

        st.session_state.cost_add = estimate_api_cost(model_reply, input_tokens, output_tokens)
        st.session_state.total_cost += st.session_state.cost_add

        update_cost()
    return second_response.choices[0].message.content

def estimate_api_cost(model, input_tokens, output_tokens):
    usd_to_inr = 90.00

    cost = ((input_tokens/1e6)*models[model][0] + (output_tokens/1e6)*models[model][1])*usd_to_inr
    
    return cost

# Function to encode the image
def encode_image(image_path):
  with open(image_path, "rb") as image_file:
    return base64.b64encode(image_file.read()).decode('utf-8')

def change_model():
    if st.session_state.model == "gpt-4-vision-preview":
        st.session_state.image = st.file_uploader("Upload an image", type=["jpg", "jpeg", "png"])

def update_cost():
    st.session_state.cost_metric_placeholder.metric(label='Total Cost', value=f"₹{st.session_state.total_cost:.2f}", delta=f"₹{st.session_state.cost_add:.2f}")

def start_new_chat():
    st.session_state.total_cost = 0.0
    st.session_state.cost_add = 0.0

    new_chat = Chat(model=st.session_state.model,
                    total_cost=st.session_state.total_cost)
    
    session.add(new_chat)
    session.commit()

    st.session_state.chat_id = new_chat.id

    # st.session_state.messages = [{"role": "assistant", "content": "Hello! How can I help you today?"}]
    # st.session_state.backend_messages = [{"role": "assistant", "content": "Hello! How can I help you today?"}]
    st.session_state.messages = []
    st.session_state.backend_messages = []

    # new_line = Chat_Line(chat_id=new_chat.id, role="assistant", line_text="Hello! How can I help you today?", line_backend_text="Hello! How can I help you today?")
    # session.add(new_line)

    # session.commit()

def delete_current_chat():
    chat = session.query(Chat).filter(Chat.id == st.session_state.chat_id).first()

    # Delete chat lines from chat_line
    for line in chat.lines:
        session.delete(line)
    # Delete chat from chat
    session.delete(chat)
    session.commit()

    st.warning(f'Chat {st.session_state.chat_id} has been deleted.', icon="⚠️")

with st.sidebar:
    st.markdown('''# Saksham's Chatbot
                ''')

    st.session_state.model = st.selectbox(
        'Select the Model',
        options=list(models.keys()),
        index=3, on_change=change_model, disabled=False)
    
    st.session_state.start_new_chat_button = st.button('Start New Chat', on_click=start_new_chat, use_container_width=True)

    with st.expander('Modify Model Parameters'):
        
        st.session_state.user_id_input = st.text_input('User ID', value='default', key='user_id')
        st.session_state.save_history_toggle = st.toggle('Save Chat History', value=True, key='save_history')
        st.session_state.function_calling_toggle = st.toggle('Enable Function Calling', value=True, key='function_calling')
        st.session_state.verbose_toggle = st.toggle('Verbose', value=False, key='verbose')
        st.session_state.temperature_input = st.slider('Temperature for the model', min_value=0.0, max_value=1.0, value=0.0, step=0.01, key='temperature')
        st.session_state.seed_input = st.number_input('Seed for the model', min_value=0, max_value=100, step=1, value=0, key='seed')
        st.session_state.max_tokens_input = st.number_input('Max Tokens', min_value=1, max_value=2048, step=1, value=300, key='max_tokens')

    if session.query(exists().where(Chat.id.isnot(None))).scalar():
        st.markdown('## Chat History')
        chat_id_widget = st.selectbox('Select Chat', options=[chat.id for chat in session.query(Chat).all()], key="chat_id")
    else:
        start_new_chat()

    # Display total cost (dynamic update)
    st.session_state.cost_metric_placeholder = st.empty()

    st.session_state.delete_chat_button = st.button('Delete Chat', on_click=delete_current_chat, use_container_width=True)

# Display chat messages from history on app rerun
chat = session.query(Chat).filter(Chat.id == chat_id_widget).first()

st.session_state.cost_add = 0.0
st.session_state.total_cost = chat.total_cost

update_cost()

st.session_state.messages = []
st.session_state.backend_messages = []
for line in chat.lines:
    st.session_state.messages.append({"role": line.role, "content": line.line_text})
    st.session_state.backend_messages.append({"role": line.role, "content": line.line_backend_text})

    with st.chat_message(line.role):
        st.markdown(line.line_text)

# React to user input
if prompt := st.chat_input("Say something!"):
    # Display user message in chat message container
    st.chat_message("user").markdown(prompt)

    # Add user message to chat history
    st.session_state.messages.append({"role": "user", "content": prompt})

    # Add user message to backend messages
    st.session_state.backend_messages.append({"role": "user", "content": system_prompt+'\n'+prompt})

    # Add data to the chat_line db
    new_line = Chat_Line(chat_id=chat_id_widget, role="user", line_text=prompt, line_backend_text=system_prompt+prompt)

    session.add(new_line)

    # Commit the changes
    session.commit()

    st.session_state.image = st.empty()

    with st.spinner("Thinking..."):

        if models[st.session_state.model][2] and st.session_state.model[:3] == "gpt":
            response = openai_client.chat.completions.create(
                model=st.session_state.model,
                messages=st.session_state.backend_messages,
                tools=tools,
                tool_choice="auto",
                temperature=st.session_state.temperature,
                seed=st.session_state.seed if (st.session_state.seed!=0) else None,
                user=st.session_state.user_id_input if (st.session_state.user_id_input!="default") else None,
                max_tokens=st.session_state.max_tokens
            )
            if response.choices[0].message.content:
                response_message = response.choices[0].message.content
                verbose_message = f"**User:** {st.session_state.user_id_input}, **Role:** {response.choices[0].message.role}, **Model:** {response.model}, **Function/Tool Call:** {response.choices[0].message.function_call}/{response.choices[0].message.tool_calls}, **Cost:** ₹{st.session_state.cost_add:.2f}, **Seed:** {st.session_state.seed}, **Temperature:** {st.session_state.temperature_input}, **Max Tokens:** {st.session_state.max_tokens_input}, **Stop Reason:** {response.choices[0].finish_reason}, **Input Tokens:** {response.usage.completion_tokens}, **Output Tokens:** {response.usage.prompt_tokens}"
            else:
                response_message = response.choices[0].message
            tool_calls = response.choices[0].message.tool_calls
            model_reply = response.model
            input_tokens = response.usage.completion_tokens
            output_tokens = response.usage.prompt_tokens
        elif models[st.session_state.model][2] and st.session_state.model[:3] == "cla":
            response = anthropic_client.messages.create(
                model=st.session_state.model,
                messages=st.session_state.backend_messages,
                temperature=st.session_state.temperature,
                max_tokens=st.session_state.max_tokens
            )
            response_message = response.content[0].text
            verbose_message = f'**Role:** {response.role}, **Model:** {response.model}, **Temperature:** {st.session_state.temperature_input}, **Max Tokens:** {st.session_state.max_tokens_input}, **Stop Reason:** {response.stop_reason}, **Input Tokens:** {response.usage.input_tokens}, **Output Tokens:** {response.usage.output_tokens}'
            tool_calls = None
            model_reply = response.model
            input_tokens = response.usage.input_tokens
            output_tokens = response.usage.output_tokens
        # else: # vision input
        #     headers = {
        #         "Content-Type": "application/json",
        #         "Authorization": f"Bearer {api_key}"
        #         }
            
        #     # Getting the base64 string
        #     base64_image = encode_image(st.session_state)

        #     payload = {
        #         "model": st.session_state.model,
        #         "messages": [
        #             {
        #             "role": "user",
        #             "content": [
        #                 {
        #                 "type": "text",
        #                 "text": prompt
        #                 },
        #                 {   
        #                 "type": "image_url",
        #                 "image_url": {
        #                     "url": f"data:image/jpeg;base64,{base64_image}"
        #                 }
        #                 }
        #             ]
        #             }
        #         ],
        #         "max_tokens": 300
        #         }

        #       response = requests.post("https://api.openai.com/v1/chat/completions", headers=headers, json=payload)

        st.session_state.cost_add = estimate_api_cost(model_reply, input_tokens, output_tokens)
        st.session_state.total_cost += st.session_state.cost_add

        # update chat cost in Chat database
        chat.total_cost = st.session_state.total_cost
        session.commit()

        update_cost()

        if tool_calls:
            st.session_state.backend_messages.append(response_message)
            response_message = call_function(tool_calls)
    
    # Display assistant response in chat message container
    with st.chat_message("assistant"):
        st.markdown(response_message)

        if st.session_state.verbose_toggle:
            st.markdown(verbose_message)
    
    # Add assistant response to chat history
    st.session_state.messages.append({"role": "assistant", "content": response_message})

    #add line to db
    new_line = Chat_Line(chat_id=chat_id_widget, role="assistant", line_text=response_message, line_backend_text=response_message)
    session.add(new_line)

    # Commit the changes
    session.commit()

        

