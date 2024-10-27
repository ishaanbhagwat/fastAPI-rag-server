from sentence_transformers import SentenceTransformer
from pinecone import Index, initialize
import openai
from app.config import config

from langchain.document_loaders import PyPDFLoader
from langchain.indexes import VectorstoreIndexCreator
from langchain.chains import RetreivalQA
from langchain.embeddings import HuggingFaceBgeEmbeddings
from langchain.text_splitter import RecursiveCharacterTextSplitter

# Initialize HuggingFace embeddings
hf_embeddings = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")

# Initialize Pinecone
initialize(api_key=config.PINECONE_API_KEY, environment=config.PINECONE_ENVIRONMENT)
pinecone_index = Index(config.PINECONE_INDEX_NAME)

# Initialize OpenRouter Client for OpenAI-like API calls
openai.api_key = config.OPENROUTER_API_KEY
openai.api_base = "https://openrouter.ai/api/v1"

def load_pdf(file):
    loaders = [PyPDFLoader(file)]
    index = VectorstoreIndexCreator(
        embedding = HuggingFaceBgeEmbeddings(model_name="all-MiniLM-L12-v2"),
        text_splitter = RecursiveCharacterTextSplitter(chunk_size=100, chunk_overlap=0)
    ).from_loaders(loaders)
    return index



def ask_question(file):
    index = load_pdf(file)

    chain = RetreivalQA.from_chain_type(
        llm_model_name = "gpt2",
        index = index,
        retriever = index.vectorstore.as_retriever(),
        input_key = "query",
    )


    augmented_query = "<CONTEXT>\n" + "\n\n-------\n\n".join(contexts[:10]) + "\n-------\n</CONTEXT>\n\n\n\nMY QUESTION:\n" + query
    messages = [
        {"role": "system", "content": "You are a personal assistant. Answer any questions I have about the PDF file provided."},
        {"role": "user", "content": augmented_query}
    ]
    response = openai.ChatCompletion.create(model="gpt-4o", messages=messages)
    return response.choices[0].message['content']
