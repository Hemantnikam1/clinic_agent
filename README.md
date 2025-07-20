# clinic_agent

# Clinic Agent Project
This project is a full-stack application featuring a conversational AI agent. It combines a React-based frontend with a powerful Python backend built using FastAPI. The agent can interact via text or voice, leveraging advanced speech-to-text, text-to-speech, and language model technologies to provide intelligent, persona-driven responses. A key feature is the shared context, allowing users to seamlessly switch between text and voice communication while the agent maintains the full conversation history.
# FEATURES
# Shared Context: 
The conversation history is maintained across both text and voice interactions within the same session, providing a seamless user experience.
# Dual Interaction Modes:  
Communicate with the AI agent via text chat or through a seamless voice-to-voice conversation.
# Speech-to-Text: 
Powered by OpenAI's Whisper model for accurate and fast transcription of user's voice input.
# Text-to-Speech: 
Utilizes a local, offline TTS engine (pyttsx3) for generating audio responses, ensuring privacy and speed.
# Configurable AI Agent: 
The core logic resides in backend/utils/agent_configuration.py. It's designed to be flexible, allowing you to easily switch between LLMs like Google Gemini or a locally-run Ollama model.
# Custom Personas:
 Dynamically change the agent's personality by providing a persona description with each request
# Responsive Frontend: 
 A clean and modern chat interface built with React and Bootstrap.
 
# TECH STACK
Frontend: Vite, React, TypeScript, Bootstrap, recorder-js
Backend: FastAPI, Python 3
AI Agent: LangGraph, LangChain (configurable for Google Gemini or Ollama)
STT/TTS: OpenAI Whisper, pyttsx3
Database: ChromaDB (for session context and vector storage)
Server: Uvicorn

# GETTING STARTED
Follow these instructions to set up and run the project locally.
# Prerequisites
Node.js (v16 or later)Python (v3.9 or later) and pip
# 1. Environment Setup
If you plan to use the Google Gemini LLM, you need to set up your API key.Navigate into the backend folder.Create a new file named .env.Open the .env file and add your Gemini API key as follows:GEMINI_API_KEY="YOUR_GEMINI_API_KEY_HERE"
Save the file. The application will automatically load this key.
# 2. Backend Setup
First, navigate into the backend directory and set up the Python environment.
# 1. Go to the backend folder
cd backend

# 2. Create a virtual environment
python -m venv venv

# 3. Activate the virtual environment
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate

# 4. Install the required Python packages
pip install -r requirements.txt
# 3. Frontend Setup
Now, set up the frontend from the project's root directory.# (If you are in the backend folder, go back to the root)
cd ..

# Install the required npm packages
npm install
# 4. Running the Application
You need to have two separate terminals open to run both the backend and frontend servers simultaneously.
# Terminal 1: 
Start the Backend ServerMake sure you are in the backend directory with the virtual environment activated.# In the /backend directory
uvicorn main:app --reload --port 8001
The backend API will now be running at http://localhost:8001.
# Terminal 2:
 Start the Frontend ServerIn the project's root directory, run the following command:# In the / (root) directory
npm start
The React application will open in your browser, usually at http://localhost:3000. You can now interact with the AI assistant.
