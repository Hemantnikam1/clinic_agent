import os
import getpass

# --- Text Splitter ---
from langchain_text_splitters import RecursiveCharacterTextSplitter

# --- Vector Store ---
from langchain_chroma import Chroma

# --- LLM and Embedding Models ---
# Import the same embedding model classes as your main agent
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_ollama import OllamaEmbeddings


# --- Configuration ---


GEMINI_API_KEY = "AIzaSyBIeGseLcEpMd4S4TnLi8m4ECqKE_h8akQ"

# Set the API key in the environment for any library that might need it
os.environ["GEMINI_API_KEY"] = GEMINI_API_KEY


try:
    # This path assumes the script is in a 'utils' folder, and 'chroma' is in the parent 'Backend' folder.
    persist_directory = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'chroma'))
except NameError:
    # Fallback for environments where __file__ is not defined
    persist_directory = os.path.abspath(os.path.join(os.getcwd(), '..', 'chroma'))

print(f"[ChromaDB] Using directory: {persist_directory}")


# --- Select your Embedding Model ---
# Make sure this matches the model used in your main agent script.
# Currently set to Gemini as per your last agent file.

# Option 1: Gemini Embeddings
embedding_fn = GoogleGenerativeAIEmbeddings(model="models/embedding-001", google_api_key=GEMINI_API_KEY)

# Option 2: Ollama Embeddings
# embedding_fn = OllamaEmbeddings(model="llama3")


def setup_hospital_database():
    """
    A one-time function to load hospital information into ChromaDB.
    """
    print("\n--- Setting up hospital info database ---")

    hospital_info = """
    Unity General Hospital Information:
    - Address: 15, Marine Enclave, Juhu Tara Road, Juhu, Mumbai, Maharashtra 400049, India
    - Phone: +91 22 4567 8900
    - Email: contact@unityhospital.in
    - Website: www.unityhospitalmumbai.in
    - Established: 1998
    - About Us: Unity General Hospital has been a cornerstone of the Juhu community for over 25 years, providing compassionate and advanced medical care. We are a 250-bed multi-specialty facility known for our state-of-the-art technology and a patient-first approach.
    - Cardiology Department: Complete cardiac care, including angiography and bypass surgery.
    - Orthopedics Department: Specializes in joint replacement, sports medicine, and trauma care.
    - Neurology Department: Features a dedicated stroke unit, neurosurgery capabilities, and advanced epilepsy treatment.
    - Oncology Department: Provides comprehensive cancer care with chemotherapy and radiation services.
    - Pediatrics & Neonatology: Specialized care for children and newborns with a state-of-the-art NICU.
    - Gastroenterology Department: Offers advanced endoscopy and surgical procedures.
    - Emergency Services: We have a 24/7 Level 1 Trauma Center.
    - Hospital & Emergency Hours: Open 24 hours, 7 days a week.
    - Outpatient Department (OPD) Hours: Monday to Saturday, from 9:00 AM to 7:00 PM.
    - Pharmacy Hours: Open 24 hours, 7 days a week.
    """

    # Split the text into manageable chunks
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=50)
    documents = text_splitter.create_documents([hospital_info])
    print(f"Splitting text into {len(documents)} chunks.")

    # Create a new Chroma collection and add the documents
    # This will create the collection or overwrite it if it already exists.
    vector_store = Chroma.from_documents(
        documents,
        embedding_fn,
        persist_directory=persist_directory,
        collection_name="hospital_info" # The agent will search this collection later
    )

    print(f"--- Database setup complete. Data added to 'hospital_info' collection. ---")


if __name__ == "__main__":
    # This block allows you to run the script directly from your terminal
    # In your terminal, navigate to the `utils` directory and run: python setup_database.py
    setup_hospital_database()