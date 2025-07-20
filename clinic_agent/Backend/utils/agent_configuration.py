import os
from dotenv import load_dotenv
from langchain_google_genai import GoogleGenerativeAIEmbeddings, ChatGoogleGenerativeAI
from langchain_ollama import ChatOllama, OllamaEmbeddings


load_dotenv(os.path.join(os.path.dirname(__file__), '..', '.env'))


## Option 1: Gemini Embeddings and LLM ---
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
llm = ChatGoogleGenerativeAI(model="gemini-1.5-pro-latest", google_api_key=GEMINI_API_KEY)
embedding_fn = GoogleGenerativeAIEmbeddings(model="models/embedding-001", google_api_key=GEMINI_API_KEY)


# Option 2: Ollama Embeddings and LLM
# llm = ChatOllama(model="llama3")
# embedding_fn = OllamaEmbeddings(model="llama3")