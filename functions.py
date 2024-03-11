'''
Streamlit powereded Chatbot Interface for OpenAI and Anthropics API.

This script provides the functions for the chatbot to use in the app.py script.

Developed by: Saksham Bhutani
'''

import streamlit as st
import pandas as pd
import requests
import json
import os
# from nsepy import get_history

# openweather_api_key = os.environ.get("OPENWEATHER_API_KEY")
openweather_api_key = "53530ef14937ba102f82172efd4bf97a"

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
                "city_name": {
                    "type": "string",
                    "description": "The name of the city",
                },
                "unit": {
                    "type": "string",
                    "description": "The unit for the temperature",
                    "enum": ["celsius", "fahrenheit"],
                },
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

# def get_current_weather(location, unit="fahrenheit"):
#     """Get the current weather in a given location"""
#     if "tokyo" in location.lower():
#         return json.dumps({"location": "Tokyo", "temperature": "10", "unit": unit})
#     elif "san francisco" in location.lower():
#         # make a streamlit plot with random temp values
#         df = pd.DataFrame({
#             'temperature': [72, 73, 71, 75, 72, 69, 78, 79, 80, 76],
#             'date': ['2021-01-01', '2021-01-02', '2021-01-03', '2021-01-04', '2021-01-05', '2021-01-06', '2021-01-07', '2021-01-08', '2021-01-09', '2021-01-10']
#         })
#         st.line_chart(df, x='date', y='temperature')

#         return json.dumps({"location": "San Francisco", "temperature": "72", "unit": unit})
#     elif "paris" in location.lower():
#         df = pd.DataFrame({
#             'temperature': [21, 22, 20, 25, 22, 19, 28, 29, 30, 26],
#             'date': ['2021-01-01', '2021-01-02', '2021-01-03', '2021-01-04', '2021-01-05', '2021-01-06', '2021-01-07', '2021-01-08', '2021-01-09', '2021-01-10']
#         })
#         st.line_chart(df, x='date', y='temperature')

#         return json.dumps({"location": "Paris", "temperature": "22", "unit": unit})
#     else:
#         return json.dumps({"location": location, "temperature": "unknown"})
    
def send_email(to_email, title, body):
    """Send email information"""
    # In production, this could be your backend API or an external API
    print(f"Email sent to {to_email} with title: {title} and body: {body}")
    return json.dumps({"to_email": to_email, "title": title, "body": body})

def get_geocode(city_name):
    '''
    This function returns the latitude and longitude for a given city name.

    Args:
        city_name: str
    
    Returns:
        dict: latitude and longitude
    '''
    api_url = f"http://api.openweathermap.org/geo/1.0/direct?q={city_name}&appid={openweather_api_key}"
    response = requests.get(api_url)

    if response.status_code == 200:
        data = response.json()[0]
        lat, lon = data['lat'], data['lon']
        return json.dumps({'latitude': lat, 'longitude': lon})
    else:
        return json.dumps({"latitude": "unknown", "longitude": "unknown"})
    
def get_current_weather(city_name, unit='celsius'):
    '''
    This function returns the weather data for a given latitude and longitude.

    Args:
        city_name: str
        unit: str, default 'celsius'
    
    Returns:
        dict: weather data
    '''
    geocode = json.loads(get_geocode(city_name))
    latitude, longitude = geocode['latitude'], geocode['longitude']

    api_url = f"https://api.openweathermap.org/data/2.5/weather?lat={latitude}&lon={longitude}&appid={openweather_api_key}"
    response = requests.get(api_url)

    # conversion factor to convert from kelvin to celsius or fahrenheit
    conversion_factor = 273.15 if unit == 'celsius' else 459.67

    if response.status_code == 200:
        data = response.json()
        return json.dumps({'weather_description': data['weather'][0]['description'], 
                'temperature': int(data['main']['temp'])-conversion_factor, 
                'temperature_feels_like': int(data['main']['feels_like'])-conversion_factor,
                'termerature_minimum': int(data['main']['temp_min'])-conversion_factor,
                'temperature_maximum': int(data['main']['temp_max'])-conversion_factor,
                'temperature_unit': 'celsius' if unit == 'celsius' else 'fahrenheit',
                'humidity': data['main']['humidity'], 'humidity_unit': '%',
                'wind_speed': data['wind']['speed'], 'clouds': data['clouds']['all'], 
                'visibility': data['visibility'], 'visibility_unit': 'meters'})
    else:
        return json.dumps({"weather_description": "unknown", "temperature": "unknown", "temperature_feels_like": "unknown",
                "termerature_minimum": "unknown", "temperature_maximum": "unknown", "temperature_unit": "unknown",
                "humidity": "unknown", "humidity_unit": "unknown", "wind_speed": "unknown", "clouds": "unknown",
                "visibility": "unknown", "visibility_unit": "unknown"})


# def get_stock_price(stock_name, start_year, start_month, start_day, end_year, end_month, end_day):
#     """Get stock price for any Indian stocks on the NSE exchange"""
#     if stock_name:
#         stock = get_history(symbol=stock_name, start=date(start_year, start_month, start_day), end=date(end_year, end_month, end_day))
#         print(stock)
#         return json.dumps({"stock_name": stock_name, "stock_price": stock["Close"].values[-1]})
#     else:
#         return json.dumps({"stock_name": stock_name, "stock_price": "unknown"})