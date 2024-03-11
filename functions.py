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
{
    "type": "function",
    "function": {
        "name": "get_weather_forecast",
        "description": "Get the weather forecast for a given location for next 5 days at an interval of every three hours",
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
            "required": ["city_name"],
        },
    },
},
]
    
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
    if "OPENWEATHER_API_KEY" in os.environ:
        openweather_api_key = os.environ.get("OPENWEATHER_API_KEY")
    else:
        st.warning("Please set the OPENWEATHER_API_KEY environment variable to use this function.")
        return json.dumps({"latitude": "unknown", "longitude": "unknown"})
    
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
    if "OPENWEATHER_API_KEY" in os.environ:
        openweather_api_key = os.environ.get("OPENWEATHER_API_KEY")
    else:
        st.warning("Please set the OPENWEATHER_API_KEY environment variable to use this function.")
        return json.dumps({"weather_description": "unknown", "temperature": "unknown", "temperature_feels_like": "unknown",
                "termerature_minimum": "unknown", "temperature_maximum": "unknown", "temperature_unit": "unknown",
                "humidity": "unknown", "humidity_unit": "unknown", "wind_speed": "unknown", "clouds": "unknown",
                "visibility": "unknown", "visibility_unit": "unknown"})

    geocode = json.loads(get_geocode(city_name))
    latitude, longitude = geocode['latitude'], geocode['longitude']

    if latitude == "unknown" or longitude == "unknown":
        return json.dumps({"forecast": "unknown"})
    else:
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

def get_weather_forecast(city_name, unit="celcius"):
    '''
    This function returns the weather forecast for a given city name.

    Args:
        city_name: str
        unit: str, default 'celsius'
    
    Returns:
        dict: weather forecast
    '''
    if "OPENWEATHER_API_KEY" in os.environ:
        openweather_api_key = os.environ.get("OPENWEATHER_API_KEY")
    else:
        st.warning("Please set the OPENWEATHER_API_KEY environment variable to use this function.")
        return json.dumps({"forecast": "unknown"})

    geocode = json.loads(get_geocode(city_name))
    latitude, longitude = geocode['latitude'], geocode['longitude']

    if latitude == "unknown" or longitude == "unknown":
        return json.dumps({"forecast": "unknown"})
    else:
        api_url = f'https://api.openweathermap.org/data/2.5/forecast?lat={latitude}&lon={longitude}&appid={openweather_api_key}'

        response = requests.get(api_url)

        # conversion factor to convert from kelvin to celsius or fahrenheit
        conversion_factor = 273.15 if unit == 'celsius' else 459.67

        if response.status_code == 200:
            data = response.json()

            num_pts = data['cnt']

            forecast = []
            for i in range(num_pts):
                forecast.append({'date': data['list'][i]['dt_txt'], 
                                 'temperature': int(data['list'][i]['main']['temp'])-conversion_factor, 'temperature_unit': 'celsius' if unit == 'celsius' else 'fahrenheit',
                                 'humidity': data['list'][i]['main']['humidity'], 
                                 'weather_description': data['list'][i]['weather'][0]['description']})

            # create a dataframe and plot the forecast
            df = pd.DataFrame(forecast)
            st.line_chart(df, x='date', y=['temperature', 'humidity'])

            return json.dumps({'forecast': forecast})
        else:
            return json.dumps({"forecast": "unknown"})


# def get_stock_price(stock_name, start_year, start_month, start_day, end_year, end_month, end_day):
#     """Get stock price for any Indian stocks on the NSE exchange"""
#     if stock_name:
#         stock = get_history(symbol=stock_name, start=date(start_year, start_month, start_day), end=date(end_year, end_month, end_day))
#         print(stock)
#         return json.dumps({"stock_name": stock_name, "stock_price": stock["Close"].values[-1]})
#     else:
#         return json.dumps({"stock_name": stock_name, "stock_price": "unknown"})
