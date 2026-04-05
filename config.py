import os
from dotenv import load_dotenv
load_dotenv()

# Environment variables
ENV = {
    "openai_api_key": os.getenv("OPENAI_API_KEY"),
    "model": os.getenv("MODEL"),
    "assistant_id": os.getenv("ASSISTANT_ID"),
    "port": os.getenv("PORT"),
    "host": os.getenv("HOST"),
}