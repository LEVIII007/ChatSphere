import os
from pymongo import MongoClient
import google.generativeai as genai
# from langchain_community.embeddings import OpenAIEmbeddings
from langchain_community.document_loaders import WebBaseLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import MongoDBAtlasVectorSearch
from langchain_google_genai import GoogleGenerativeAIEmbeddings, ChatGoogleGenerativeAI
import google.generativeai as genai
# from langchain.embeddings import GoogleGenerativeAIEmbeddings
import pymongo
from langchain_community.document_loaders import PDFMinerLoader
from dotenv import load_dotenv
load_dotenv()
import io
from PyPDF2 import PdfReader

def get_pdf_text(pages):
    text = ""
    for page in pages:
        text += page.extract_text() + "\n"  # Concatenate text from each page
    return text


def get_chunks(text):
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=10000, chunk_overlap=1000)
    chunks = text_splitter.split_text(text)
    return chunks

# from google.api_core import retry

def get_embeddings(text: str, model: str = 'models/embedding-001') -> list[float]:
    genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))
    # @Retry(timeout=300.0)
    def embed_fn(text: str) -> list[float]:
        # Set the task_type to CLASSIFICATION.
        embedding = genai.embed_content(model=model, content=text, task_type="classification")
        return embedding['embedding']

    try:
        embeddings = embed_fn(text)
        return embeddings
    except Exception as e:
        return []


def save_url_embeddings_to_database(url, doc_id):
    # user_id = user  # Assuming 'user' has a 'user_id' attribute
    genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))
    mongodb_conn_string = os.getenv('MONGODB_CONN_STRING')
    db_name = os.getenv('DB_NAME')
    collection_name = os.getenv('EMB_COLLECTION_NAME')
    index_name = os.getenv('INDEX_NAME')

    client = pymongo.MongoClient(mongodb_conn_string)
    db = client[db_name]
    collection = db[collection_name]

    loader = WebBaseLoader(url)
    data = loader.load()

    text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=0, separators=[
                                                   "\n\n", "\n", "(?<=\. )", " "], length_function=len)
    docs = text_splitter.split_documents(data)
    embeddings = [get_embeddings(text.page_content) for text in docs]
    flag = 0
    for text, embedding in zip(docs, embeddings):
        flag += 1
        document = {
            "doc_id": doc_id,
            "text": text.page_content,
            "embedding": embedding,
        }
        collection.insert_one(document)
        if flag == 15:
            break

    print(f"Embeddings for URL '{url}' saved to database under user ID '{user_id}' and chat name '{chat_name}'.")


from langchain_community.document_loaders import PyPDFLoader

def save_pdf_embeddings_to_database(doc_id, pdf_content):
    # user_id = user  # Assuming 'user' has a 'user_id' attribute
    genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))
    mongodb_conn_string = os.getenv('MONGODB_CONN_STRING')
    db_name = os.getenv('DB_NAME')
    collection_name = os.getenv('COLLECTION_NAME')

    client = pymongo.MongoClient(mongodb_conn_string)
    db = client[db_name]
    collection = db[collection_name]
    pdf_file = io.BytesIO(pdf_content)
    
    # Use PdfReader to read the PDF content
    reader = PdfReader(pdf_file)
    data = get_pdf_text(reader.pages)
    docs = get_chunks(data)
    print(type(docs))

    embeddings = [get_embeddings(str(text)) for text in docs]

    # collection.delete_many({})

    for text, embedding in zip(docs, embeddings):
        document = {
            "text": str(text),
            "embedding": embedding,
            "doc_id": user_id
        }
        collection.insert_one(document)

    print(f"Embeddings for URL ' saved to database under user ID '{user_id}' and chat name '{chat_name}'.")



# url = "https://en.wikipedia.org/wiki/AT%26T"
# save_url_embeddings_to_database(url,"668a9a784183c96dd2327c17")
# save_pdf_embeddings_to_database("pdf.pdf", {'user_id' : "abscefg"}, "chat_name")












# https://python.langchain.com/v0.1/docs/use_cases/chatbots/quickstart/

# https://python.langchain.com/v0.1/docs/use_cases/chatbots/tool_usage/