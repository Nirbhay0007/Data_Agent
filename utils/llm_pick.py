


# pyrefly: ignore [missing-import]
from dotenv import load_dotenv


# pyrefly: ignore [missing-import]
from langchain_groq import ChatGroq

load_dotenv()

def pick_llm(level: str):
    if level.lower() == "high":
        return ChatGroq(model_name="openai/gpt-oss-120b", temperature=0.1,max_tokens=500)
    elif level.lower() == "medium":
        return ChatGroq(model_name="meta-llama/llama-4-scout-17b-16e-instruct", temperature=0.1,max_tokens=500)
    elif level.lower() == "low":
        return ChatGroq(model_name="qwen/qwen3.8-27b", temperature=0.1,max_tokens=50)
    else:
        raise ValueError(f"Invalid level: {level}. Choose from Beginner, Intermediate, or Advanced.")
 

# llm_obj = pick_llm(level="high")
# response = llm_obj.invoke("Hello, who are you?")
# print(response.content)