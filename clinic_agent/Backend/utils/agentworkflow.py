from langgraph.graph import StateGraph, END
from typing import TypedDict
from langchain_core.runnables import RunnableLambda
from langchain_core.tools import tool

import chromadb
import asyncio
import uuid
import os
import json

# Corrected imports to use modern packages and avoid errors
from langchain_chroma import Chroma
from langchain_ollama import ChatOllama, OllamaEmbeddings
from langchain_google_genai import GoogleGenerativeAIEmbeddings, ChatGoogleGenerativeAI

# --- Configuration ---
try:
    persist_directory = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'chroma'))
except NameError:
    persist_directory = os.path.abspath(os.path.join(os.getcwd(), '..', 'chroma'))
print(f"[ChromaDB] Persist directory: {persist_directory}")


# --- Gemini LLM and Embeddings (Restored as per your original code) ---
# Uncomment below to use Gemini
# from langchain_google_genai import ChatGoogleGenerativeAI, GoogleGenerativeAIEmbeddings
#
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "AIzaSyBIeGseLcEpMd4S4TnLi8m4ECqKE_h8akQ") # Replace with your actual API key or set as env var
llm = ChatGoogleGenerativeAI(model="gemini-1.5-pro-latest", google_api_key=GEMINI_API_KEY)
embedding_fn = GoogleGenerativeAIEmbeddings(model="models/embedding-001", google_api_key=GEMINI_API_KEY)


# --- Ollama LLM and Embeddings (Active as per your original code) ---
# llm = ChatOllama(model="llama3")
# embedding_fn = OllamaEmbeddings(model="llama3")


# --- Graph State Definition (Unchanged) ---
class AgentState(TypedDict):
    message: str
    session_id: str
    session_context: list
    llm_response: str
    tool: str
    status: str
    details: str
    name: str
    date: str
    final_response: str

# --- Nodes and Functions (Unchanged) ---

async def load_context(input: dict):
    message = input["message"]
    session_id = input["session_id"]
    await upsert_chroma_session(session_id, [message], [])
    context = await get_context_by_session_id(session_id)
    return {"message": message, "session_id": session_id, "session_context": context}

async def userintend(input: AgentState):
    print(f"[userintend] input: {input}")
    message = input["message"]
    session_context = input["session_context"]
    session_id = input["session_id"]
    system_prompt = (
        "You are a helpful assistant for a clinic service. Users are messaging only to make enquiries or to perform tasks related to clinics. "
        "Based on the user's message and the conversation context, determine the user's intent. "
        "If the user wants to book an appointment, check if they provided their name and preferred date in the context. Important: Only check for name and date. "
        "If the name and date have already been provided, take them from the provided context. "
        "If the name is missing, ask for their name. If the date is missing, ask for their preferred date. "
        "We only need these two parameters for booking an appointment; do not check for anything else. "
        "If both name and date are provided, respond with JSON format: {\"action\": \"book_appointment\", \"name\": \"user_name\", \"date\": \"appointment_date\"}. "
        "If the user has a general question or enquiry, use the 'enquiry' tool. "
        "If you are not sure about the user's intent for booking an appointment or enquiry, then only ask the user to provide more information or clarify their request. "
        "Always be concise and clear in your responses. Keep responses crisp and to the point.\n"
    )
    context_str = "\n".join(session_context)
    prompt = f"{system_prompt}Context so far:\n{context_str}\n\nUser: {message}\nAssistant:"
    response = await llm.ainvoke(prompt)
    response_text = response.content if hasattr(response, 'content') else str(response)
    print(f"[userintend] LLM response: {response_text}")
    await upsert_chroma_session(session_id, [], [response_text])
    
    unclear_keywords = [
        "not sure", "uncertain", "unclear", "don't understand", "cannot determine", "need more information", "please clarify"
    ]
    if any(keyword in response_text.lower() for keyword in unclear_keywords):
        print("[userintend] LLM unclear intent")
        return {"llm_response": "I'm sorry, I couldn't determine your intent. Could you please provide more information or clarify your request?"}
    
    return {"llm_response": response_text}

@tool
def book_appointment(name: str, date: str):
    """Book an appointment for the user with name and date."""
    if not name or not date:
        return {"tool": "book_appointment", "status": "missing_data", "details": f"Missing data - Name received: '{name}', Date received: '{date}'"}
    try:
        # Correctly handle path for appointments directory
        base_dir = os.path.dirname(__file__) if '__file__' in locals() else os.getcwd()
        appointments_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'appointments')       
        os.makedirs(appointments_dir, exist_ok=True)
        appointments_file = os.path.join(appointments_dir, 'appointments.txt')
        print("HHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHH",appointments_file)
        appointment_entry = f"appointment {name} {date}\n"
        with open(appointments_file, 'a', encoding='utf-8') as f:
            f.write(appointment_entry)
        return {"tool": "book_appointment", "status": "success", "details": f"Appointment booked for {name} on {date}", "name": name, "date": date}
    except Exception as e:
        return {"tool": "book_appointment", "status": "error", "details": f"Error booking appointment: {str(e)}"}

@tool
def enquiry_tool(query: str):
    """
    Handles a general enquiry by performing a similarity search on the hospital's information database.
    """
    print(f"\n--- [Enquiry Tool] Searching for: '{query}' ---")
    try:
        # Connect to the existing collection
        vector_store = Chroma(
            embedding_function=embedding_fn,
            persist_directory=persist_directory,
            collection_name="hospital_info"
        )

        # Perform the similarity search
        results = vector_store.similarity_search(query, k=3)

        if not results:
            return {"tool": "enquiry_tool", "status": "success", "details": "I could not find specific information about that. Please ask about our services, hours, or location."}

        # Combine the content of the retrieved documents
        retrieved_docs = "\n\n".join([doc.page_content for doc in results])
        print(f"--- [Enquiry Tool] Found relevant info: ---\n{retrieved_docs}\n-----------------------------------------")
        
        return {"tool": "enquiry_tool", "status": "success", "details": retrieved_docs}
    except Exception as e:
        print(f"[Enquiry Tool] Error: {e}")
        return {"tool": "enquiry_tool", "status": "error", "details": f"An error occurred during the search: {e}"}

async def tool_caller(input: AgentState):
    llm_response = input["llm_response"]
    message = input["message"] # Get the original user message
    name = ""
    date = ""
    is_json_action = False
    
    try:
        json_start = llm_response.find('{')
        json_end = llm_response.rfind('}') + 1
        if json_start != -1 and json_end > json_start:
            json_str = llm_response[json_start:json_end]
            json_data = json.loads(json_str)
            if json_data.get("action") == "book_appointment":
                name = json_data.get("name", "")
                date = json_data.get("date", "")
                is_json_action = True
    except Exception as e:
        print(f"[tool_caller] Error parsing JSON: {e}")
        pass
    
    if is_json_action:
        return book_appointment.invoke({"name": name, "date": date})
    
    # Check for enquiry intent and pass the user's message as the query
    if "enquiry" in llm_response.lower():
        return enquiry_tool.invoke({"query": message})
    else:
        return {"tool": None, "status": "no_tool_called", "details": "No tool was called."}

async def tool_result_to_llm(input: AgentState):
    tool_result = input
    tool = tool_result.get("tool")
    status = tool_result.get("status")
    details = tool_result.get("details")
    session_id = input.get("session_id")
    session_context = await get_context_by_session_id(session_id)
    prompt = ""
    user_question = input.get("message")
    if tool == "book_appointment":
        if status == "success":
            name = tool_result.get("name", "")
            date = tool_result.get("date", "")
            prompt = (f"The user's appointment has been booked successfully for {name} on {date}. "
                      "Respond to the user with a confirmation message that includes their name and date. The message should be crisp and to the point.")
        elif status == "missing_data":
            prompt = ("The appointment booking failed because some required information is missing. "
                      "Generate a crisp, short, and on-point message. Ask the user to provide their name and preferred date.")
        else: # status == "error"
            prompt = (f"There was an error booking the appointment: {details}. Apologize to the user and ask them to try again.")
    elif tool == "enquiry_tool" and status == "success":
        prompt = (
                    "You are a helpful clinic assistant. Answer the user's question based *only* on the provided context below.\n"
                    "Keep the answer concise and directly address exactly what was asked.\n\n"
                    f"CONTEXT:\n{details}\n\n"
                    f"USER'S QUESTION:\n{user_question}\n\n"
                    "ANSWER:"
                )    
    else:
        prompt = (f"There was an issue with the tool call. Details: {details}. Respond to the user with an appropriate message.")
    
    response = await llm.ainvoke(prompt)
    response_text = response.content if hasattr(response, 'content') else str(response)
    print(f"[tool_result_to_llm] LLM response: {response_text}")
    await upsert_chroma_session(session_id, [], [response_text])
    return {"final_response": response_text}

async def upsert_chroma_session(session_id: str, user_messages: list, assistant_messages: list):
    collection_name = f"session_{session_id}"
    vector_store = Chroma(embedding_function=embedding_fn, persist_directory=persist_directory, collection_name=collection_name)
    docs = []
    metadatas = []
    for msg in user_messages:
        docs.append(str(msg))
        metadatas.append({"role": "user", "session_id": session_id})
    for msg in assistant_messages:
        docs.append(str(msg.content if hasattr(msg, 'content') else msg))
        metadatas.append({"role": "assistant", "session_id": session_id})
    if docs:
        vector_store.add_texts(texts=docs, metadatas=metadatas)

async def get_context_by_session_id(session_id: str):
    collection_name = f"session_{session_id}"
    try:
        vector_store = Chroma(embedding_function=embedding_fn, persist_directory=persist_directory, collection_name=collection_name)
        results = vector_store.get(where={"session_id": session_id})
        return results.get("documents", [])
    except Exception:
        return []

# --- Graph Definition ---
agent_workflow = StateGraph(AgentState)

agent_workflow.add_node("load_context", load_context)
agent_workflow.add_node("userintend", userintend)
agent_workflow.add_node("tool_caller", tool_caller)
agent_workflow.add_node("tool_result_to_llm", tool_result_to_llm)

agent_workflow.set_entry_point("load_context")
agent_workflow.add_edge("load_context", "userintend")
agent_workflow.add_edge("tool_caller", "tool_result_to_llm")

def route_tool_call(state: AgentState):
    llm_response = state.get("llm_response", "")
    llm_response_lower = llm_response.lower()
    try:
        json_start = llm_response.find('{')
        json_end = llm_response.rfind('}') + 1
        if json_start != -1 and json_end > json_start:
            json_str = llm_response[json_start:json_end]
            json_data = json.loads(json_str)
            if json_data.get("action") == "book_appointment":
                return "tool_caller"
    except Exception:
        pass
    if "book appointment" in llm_response_lower or "enquiry" in llm_response_lower:
        return "tool_caller"
    return END

agent_workflow.add_conditional_edges("userintend", route_tool_call, {"tool_caller": "tool_caller", END: END})

# Compile the base workflow
app_base = agent_workflow.compile()

def format_final_response(state: dict):
    """Extracts the final response from the graph's state."""
    response = state.get("final_response") or state.get("llm_response")
    return {"final_response": response}

# Create the final app by chaining the base graph with the formatting function
app = app_base | RunnableLambda(format_final_response)