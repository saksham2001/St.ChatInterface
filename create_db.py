'''
Streamlit powereded Chatbot Interface for OpenAI and Anthropics API.

This script creates a database for chatbot to store the conversation history.

Developed by: Saksham Bhutani
'''

from sqlalchemy import create_engine
from utils import Base

# Connect to the database (or create it if it doesn't exist)
engine = create_engine('sqlite:///data/chat_database.db', echo=True)

# Create all tables in the engine. This is equivalent to "Create Table" statements in raw SQL.
Base.metadata.create_all(engine)