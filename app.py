'''
Streamlit powereded Chatbot Interface for OpenAI and Anthropics API.

This script provides a chatbot interface for OpenAI and Anthropics API. 
It allows the user to select the model, start a new chat, delete the current chat, and interact with the chatbot. 
The user can also modify the model parameters and view the chat history.

Developed by: Saksham Bhutani
'''

from functions import tools, get_current_weather, send_email, get_weather_forecast
from utils import Chat, Chat_Line
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.sql import exists
from anthropic import Anthropic
from openai import OpenAI
import streamlit as st
import base64
import requests
import json
import os


# Connect to the database
engine = create_engine('sqlite:///data/chat_database.db')  # Make sure this matches the URI you used to create the db
Session = sessionmaker(bind=engine)

# Create a session
session = Session()

# Set page config
st.set_page_config(page_title="Saksham's Chatbot", layout="wide", page_icon='🤖', menu_items={
                                        'Get Help': 'https://github.com/saksham2001/St.ChatInterface/tree/main',
                                        'Report a bug': "https://github.com/saksham2001/St.ChatInterface/issues",
                                        'About': requests.get('https://raw.githubusercontent.com/saksham2001/St.ChatInterface/main/README.md?token=GHSAT0AAAAAACINUV3CLIGB24H27E3J2AGAZPO2BTA').text
                                    }
    )

# check if either of the API keys are available
if ("OPENAI_API_KEY" in os.environ) or "ANTHROPIC_API_KEY" in os.environ:
    if "OPENAI_API_KEY" in os.environ:
        # Create the openai client
        openai_client = OpenAI()
        api_key = os.environ.get("OPENAI_API_KEY")

    if "ANTHROPIC_API_KEY" in os.environ:
        # Create the anthropic client
        anthropic_client = Anthropic(
            # This is the default and can be omitted
            api_key=os.environ.get("ANTHROPIC_API_KEY"),
        )
else:
    # If environment variable is not set, load the setup page
    st.page_link('https://github.com/saksham2001/St.ChatInterface', 'Setup Page')

# System Prompt to add before the users input
system_prompt = ""

# models and input/output token price per million tokens (in USD), and if multimodal, if function calling available
models = {'gpt-3.5-turbo-0125' : [0.50, 1.50, False, True],
          'gpt-4-0613' : [30.00, 60.00, False, True],
          'gpt-4-0125-preview' : [30.00, 60.00, False, True],
          'gpt-4-1106-vision-preview' : [10.00, 30.00, True, False],
          'claude-3-haiku-20240307': [0.25, 1.25, True, False],
          'claude-3-sonnet-20240229': [3.00, 15.00, True, False],
          'claude-3-opus-20240229': [15.00, 75.00, True, False]
          }

# Dictionary of available functions for the models
available_functions = {
    "get_current_weather": get_current_weather,
    "send_email": send_email,
    "get_weather_forecast": get_weather_forecast
}

def call_function(tool_call):
    '''
    This function calls the function specified in the tool_call object and returns the response to the model.

    Args:
        tool_call (list): List of tool_call objects
    
    Returns:
        str: Response from the model
    '''
    with st.spinner("Processing results..."):
        # Call all the functions and get the response
        for tool_call in tool_calls:
            function_name = tool_call.function.name
            function_to_call = available_functions[function_name]
            function_args = json.loads(tool_call.function.arguments)
            function_response = function_to_call(**function_args)

            # Append the response to the backend messages
            st.session_state.backend_messages.append(
                {
                    "tool_call_id": tool_call.id,
                    "role": "tool",
                    "name": function_name,
                    "content": function_response,
                }
            )

        # Call the model again with the updated backend messages
        second_response = openai_client.chat.completions.create(
            model=st.session_state.model,
            messages=st.session_state.backend_messages,
        )

        # Update the cost for the recent model call
        model_reply = response.model
        input_tokens = response.usage.completion_tokens
        output_tokens = response.usage.prompt_tokens

        st.session_state.cost_add = estimate_api_cost(model_reply, input_tokens, output_tokens)
        st.session_state.total_cost += st.session_state.cost_add

        update_cost()
        
        return second_response.choices[0].message.content

def estimate_api_cost(model, input_tokens, output_tokens):
    '''
    This function estimates the cost of the API call based on the model, input tokens and output tokens.

    Args:
        model (str): Model used for the API call
        input_tokens (int): Number of input tokens
        output_tokens (int): Number of output tokens
    
    Returns:
        float: Cost of the API call (in INR)
    '''
    usd_to_inr = 90.00
    
    # Estimate the cost
    cost = ((input_tokens/1e6)*models[model][0] + (output_tokens/1e6)*models[model][1])*usd_to_inr
    
    return cost

def encode_image(image_path):
    '''
    This function encodes the image to base64 format.

    Args:
        image_path (str): Path to the image

    Returns:
        str: Base64 encoded image
    '''
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode('utf-8')

def select_model():
    '''
    This is the callback function to change the model if the user selects a different model.
    '''
    st.session_state.model = st.session_state.model_input

    # Check if the api key of the model is loaded
    if st.session_state.model[:3] == "gpt" and "OPENAI_API_KEY" not in os.environ:
        st.warning("OpenAI API Key not found. Please set the OPENAI_API_KEY environment variable.")
    elif st.session_state.model[:3] == "cla" and "ANTHROPIC_API_KEY" not in os.environ:
        st.warning("Anthropic API Key not found. Please set the ANTHROPIC_API_KEY environment variable.")

    # Add image input option if the model is multimodal
    # if models[st.session_state.model][2]:
    #     image_input_placeholder.file_uploader("Upload an image", type=["jpg", "jpeg", "png"])

def update_cost():
    '''
    This is the callback function to update the cost metric.
    '''

    st.session_state.cost_metric_placeholder.metric(label='Total Cost', value=f"₹{st.session_state.total_cost:.2f}", delta=f"₹{st.session_state.cost_add:.2f}")

def start_new_chat():
    '''
    This is the callback function that starts a new chat, if start new chat button is clicked.
    '''

    # Reset the session state cost variables
    st.session_state.total_cost = 0.0
    st.session_state.cost_add = 0.0

    # Add a new chat to the database
    new_chat = Chat(total_cost=st.session_state.total_cost)
    
    session.add(new_chat)
    session.commit()

    # Update the chat_id in the session state
    st.session_state.chat_id = new_chat.id

    # Clear the chat messages
    st.session_state.messages = []
    st.session_state.backend_messages = []
    st.session_state.model = None

def delete_current_chat():
    '''
    This is the callback function that deletes the current chat, if delete chat button is clicked.
    '''

    # Get the chat from the database
    chat = session.query(Chat).filter(Chat.id == st.session_state.chat_id).first()

    # Delete chat lines from chat_line
    for line in chat.lines:
        session.delete(line)

    # Delete chat from chat
    session.delete(chat)
    session.commit()

    # Create a warning message for the user
    st.warning(f'Chat {st.session_state.chat_id} has been deleted.', icon="⚠️")

# -- Chatbot Interface --
    
# Create the sidebar
with st.sidebar:
    # Add a title to the sidebar
    st.markdown('''# Saksham's Chatbot
                ''')
    
    # If the database has chats, display the chat history
    if session.query(exists().where(Chat.id.isnot(None))).scalar():
        st.markdown('## Chat History')

        # Widget to select the chat
        chat_id_widget = st.selectbox('Select Chat', options=[chat.id for chat in session.query(Chat).all()], key="chat_id")
    else: # Otherwise start a new chat
        start_new_chat()
        st.rerun()

    # Chat deletion button widget
    st.session_state.delete_chat_button = st.button('Delete this Chat', on_click=delete_current_chat, use_container_width=True)
    
    # Start new chat button widget
    st.session_state.start_new_chat_button = st.button('Start New Chat', on_click=start_new_chat, use_container_width=True)

    # Expander to change model parameters
    with st.expander('Modify Model Parameters'):
        st.session_state.user_id_input = st.text_input('User ID', value='default', key='user_id')
        st.session_state.save_history_toggle = st.toggle('Save Chat History', value=True, key='save_history')

        # check if function calling is available for the model
        if 'model' in st.session_state :
            if st.session_state.model is not None and models[st.session_state.model][3]:
                st.session_state.function_calling_toggle = st.toggle('Enable Function Calling', value=True, key='function_calling')

        st.session_state.verbose_toggle = st.toggle('Verbose', value=False, key='verbose')
        st.session_state.temperature_input = st.slider('Temperature for the model', min_value=0.0, max_value=1.0, value=0.0, step=0.01, key='temperature')
        st.session_state.seed_input = st.number_input('Seed for the model', min_value=0, max_value=100, step=1, value=0, key='seed')
        st.session_state.max_tokens_input = st.number_input('Max Tokens', min_value=1, max_value=2048, step=1, value=300, key='max_tokens')

    # Display total cost (dynamic update)
    st.session_state.cost_metric_placeholder = st.empty()

# Display chat messages from history on app rerun
chat = session.query(Chat).filter(Chat.id == chat_id_widget).first()

# Read the cost value from the database
st.session_state.cost_add = 0.0
st.session_state.total_cost = chat.total_cost

# Update the cost metric widget
update_cost()

# Update the messages in session state variables from the database
st.session_state.messages = []
st.session_state.backend_messages = []

# If no lines in the chat, create a option to select the model
if len(chat.lines) == 0 and st.session_state.model is None:
    # Model selection widget
    model_input = st.selectbox(
        'Select the Model',
        options=list(models.keys()),
        index=0, disabled=False, key="model_input")
    
    # Model selection button
    st.button('Start Chatting...', on_click=select_model, use_container_width=True)
    
    # Update model in the database
    chat.model = st.session_state.model_input
    session.commit()
else:
    if len(chat.lines) == 0:
        st.markdown(f"#### Model: {chat.model}")
        st.markdown("## Start a new chat by saying something!")
    else:
        st.session_state.model = chat.model
        st.markdown(f"#### Model: {st.session_state.model}")
        for line in chat.lines:
            st.session_state.messages.append({"role": line.role, "content": line.line_text})
            st.session_state.backend_messages.append({"role": line.role, "content": line.line_backend_text})

            # Display chat messages
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
            # Call the model

            if (not models[st.session_state.model][2]) and st.session_state.model[:3] == "gpt": # OpenAI API call (text only)
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
            elif st.session_state.model[:3] == "cla": # Anthropics API call
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
            # else: # OpenAI Multimodal API call
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

            # Estimate the cost of the API call
            st.session_state.cost_add = estimate_api_cost(model_reply, input_tokens, output_tokens)
            st.session_state.total_cost += st.session_state.cost_add

            # Update chat cost in Chat database
            chat.total_cost = st.session_state.total_cost
            session.commit()

            update_cost()

            # If tools calls are required and function calling is enabled and the model supports it, call the function
            if tool_calls and st.session_state.function_calling_toggle and models[st.session_state.model][3]:
                st.session_state.backend_messages.append(response_message)
                response_message = call_function(tool_calls)
        
        # Display assistant response in chat message container
        with st.chat_message("assistant"):
            st.markdown(response_message)

            # Display verbose message if verbose toggle is on
            if st.session_state.verbose_toggle:
                st.markdown(verbose_message)
        
        # Add assistant response to chat history
        st.session_state.messages.append({"role": "assistant", "content": response_message})

        # Add the message to the database
        new_line = Chat_Line(chat_id=chat_id_widget, role="assistant", line_text=response_message, line_backend_text=response_message)
        session.add(new_line)

        # Commit the changes
        session.commit()
    # image_input_placeholder = st.empty()