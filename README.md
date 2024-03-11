# St.ChatInterface
**A Streamlit powered chat interface to use powerful LLM models by OpenAI and Anthropic.**

## Features
- Cheaper than individual ChatGPT and Anthropic subscriptions.
- Saves all the chats and their respective responses in a local database.
- Data will not be used to train LLMs.
- Allows function calling.
- [Coming Soon] Allows model to produce interactive elements (graphs, maps, etc).
- [Coming Soon] Multimodal model support. 

## Models Available
| Model Name | Price per 1M Input Tokens | Price per 1M Output Tokens | Multimodal |
|------------|---------------------------|---------------------------|------------|
| gpt-3.5-turbo-0125 | $0.50 | $1.50 | ❌ |
| gpt-4-0613 | $30.00 | $60.00 | ❌ |
| gpt-4-0125-preview | $30.00 | $60.00 | ❌ |
| gpt-4-1106-vision-preview | $10.00 | $30.00 | ✅ |
| claude-3-opus-20240229 | $15.00 | $75.00 | ✅ |
| claude-3-sonnet-20240229 | $3.00 | $15.00 | ✅ |

## Installation

Python 3.7+ is required to run this project.

```bash
git clone https://github.com/saksham2001/St.ChatInterface
cd St.ChatInterface
pip install -r requirements.txt
```

## Setup

Setup the database to save all the chats and their respective responses.
    
```bash
mkdir data
python3 create_db.py
```

## Usage

Replace `<your_api_key>` with respective API keys for your OpenAI and Anthropic accounts.

```bash
export OPENAI_API_KEY='<your_api_key>'
export ANTHROPIC_API_KEY='<your_api_key>'

streamlit run app.py
```
