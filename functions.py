'''
Streamlit powereded Chatbot Interface for OpenAI and Anthropics API.

This script provides the functions for the chatbot to use in the app.py script.

Developed by: Saksham Bhutani
'''

import streamlit as st
import pandas as pd
import json
# from nsepy import get_history

# Define the tools available to the models
tools = [
{
    "type": "function",
    "function": {
        "name": "get_current_weather",
        "description": "Get the current weather in a given location",
        "parameters": {
            "type": "object",
            "properties": {
                "location": {
                    "type": "string",
                    "description": "The city and state, e.g. San Francisco, CA",
                },
                "unit": {"type": "string", "enum": ["celsius", "fahrenheit"]},
            },
            "required": ["location"],
        },
    },
},
{
    "type": "function",
    "function": {
        "name": "send_email",
        "description": "Send email information",
        "parameters": {
            "type": "object",
            "properties": {
                "to_email": {
                    "type": "string",
                    "description": "Recipient's email address",
                },
                "title": {"type": "string", "description": "The title of the email"},
                "body": {"type": "string", "description": "The Body of the email"},
            },
            "required": ["to_email", "title", "body"],
        },
    },
},
]

def get_current_weather(location, unit="fahrenheit"):
    """Get the current weather in a given location"""
    if "tokyo" in location.lower():
        return json.dumps({"location": "Tokyo", "temperature": "10", "unit": unit})
    elif "san francisco" in location.lower():
        # make a streamlit plot with random temp values
        df = pd.DataFrame({
            'temperature': [72, 73, 71, 75, 72, 69, 78, 79, 80, 76],
            'date': ['2021-01-01', '2021-01-02', '2021-01-03', '2021-01-04', '2021-01-05', '2021-01-06', '2021-01-07', '2021-01-08', '2021-01-09', '2021-01-10']
        })
        st.line_chart(df, x='date', y='temperature')

        return json.dumps({"location": "San Francisco", "temperature": "72", "unit": unit})
    elif "paris" in location.lower():
        df = pd.DataFrame({
            'temperature': [21, 22, 20, 25, 22, 19, 28, 29, 30, 26],
            'date': ['2021-01-01', '2021-01-02', '2021-01-03', '2021-01-04', '2021-01-05', '2021-01-06', '2021-01-07', '2021-01-08', '2021-01-09', '2021-01-10']
        })
        st.line_chart(df, x='date', y='temperature')

        return json.dumps({"location": "Paris", "temperature": "22", "unit": unit})
    else:
        return json.dumps({"location": location, "temperature": "unknown"})
    
def send_email(to_email, title, body):
    """Send email information"""
    # In production, this could be your backend API or an external API
    print(f"Email sent to {to_email} with title: {title} and body: {body}")
    return json.dumps({"to_email": to_email, "title": title, "body": body})

# def get_stock_price(stock_name, start_year, start_month, start_day, end_year, end_month, end_day):
#     """Get stock price for any Indian stocks on the NSE exchange"""
#     if stock_name:
#         stock = get_history(symbol=stock_name, start=date(start_year, start_month, start_day), end=date(end_year, end_month, end_day))
#         print(stock)
#         return json.dumps({"stock_name": stock_name, "stock_price": stock["Close"].values[-1]})
#     else:
#         return json.dumps({"stock_name": stock_name, "stock_price": "unknown"})