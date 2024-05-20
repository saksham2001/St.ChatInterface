'''
Streamlit powereded Chatbot Interface for OpenAI and Anthropics API.

This script provides the definations for the database tables for the app.py script.

Developed by: Saksham Bhutani
'''

from sqlalchemy import create_engine, Column, ForeignKey, Integer, String, DateTime, Boolean, Float
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
import datetime

# Define the base class
Base = declarative_base()

# Define the Chat table
class Chat(Base):
    __tablename__ = 'chat'
    id = Column(Integer, primary_key=True)
    timestamp = Column(DateTime, default=datetime.datetime.utcnow)
    model1 = Column(String)
    model2 = Column(String)
    total_cost = Column(Float)
    mode = Column(String)

    # Establish relationship with Chat_Line
    lines = relationship("Chat_Line", back_populates="chat")

# Define the Chat_Line table
class Chat_Line_Model1(Base):
    __tablename__ = 'chat_line'
    id = Column(Integer, primary_key=True)
    chat_id = Column(Integer, ForeignKey('chat.id'))
    role = Column(String)
    line_text = Column(String)
    line_backend_text = Column(String)
    timestamp = Column(DateTime, default=datetime.datetime.utcnow)

    # Establish relationship with Chat
    chat = relationship("Chat", back_populates="lines")

# Define the Chat_Line table
class Chat_Line_Model2(Base):
    __tablename__ = 'chat_line'
    id = Column(Integer, primary_key=True)
    chat_id = Column(Integer, ForeignKey('chat.id'))
    role = Column(String)
    line_text = Column(String)
    line_backend_text = Column(String)
    timestamp = Column(DateTime, default=datetime.datetime.utcnow)

    # Establish relationship with Chat
    chat = relationship("Chat", back_populates="lines")
