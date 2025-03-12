# test_openai.py
import os
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI

load_dotenv()

api_key = os.getenv("OPENAI_API_KEY")
model = os.getenv("MODEL_NAME", "gpt-3.5-turbo")

print(f"Using model: {model}")
print(f"API key (first 5 chars): {api_key[:5]}...")

try:
    llm = ChatOpenAI(api_key=api_key, model=model)
    response = llm.invoke("Say hello!")
    print("Success! Response:", response.content)
except Exception as e:
    print(f"Error: {str(e)}")
    import traceback
    traceback.print_exc()