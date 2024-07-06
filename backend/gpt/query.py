import argparse
# import params
from pymongo import MongoClient
import google.generativeai as genai
from langchain_community.vectorstores import MongoDBAtlasVectorSearch
from langchain.retrievers import ContextualCompressionRetriever
from langchain.retrievers.document_compressors import LLMChainExtractor
from langchain_google_genai import GoogleGenerativeAIEmbeddings, ChatGoogleGenerativeAI
from langchain_mongodb import MongoDBAtlasVectorSearch
from langchain.chains.question_answering import load_qa_chain
from langchain.prompts import PromptTemplate
import warnings
from dotenv import load_dotenv
load_dotenv()   
import os


genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))
mongodb_conn_string = os.getenv('MONGODB_CONN_STRING')
db_name = os.getenv('DB_NAME')
collection_name = os.getenv('COLLECTION_NAME')
index_name = os.getenv('INDEX_NAME')

def get_conversational_chain():
    # Define a prompt template for asking questions based on a given context
    prompt_template = """
    Answer the question in detail. you may need to use provided context to answer the question or maybe you can answer it without context.
    Context:\n {context}?\n
    Question: \n{question}\n

    Answer:
    """

    # Initialize a ChatGoogleGenerativeAI model for conversational AI
    model = ChatGoogleGenerativeAI(model="gemini-pro", temperature=0.3)

    # Create a prompt template with input variables "context" and "question"
    prompt = PromptTemplate(
        template=prompt_template, input_variables=["context", "question"]
    )

    # Load a question-answering chain with the specified model and prompt
    chain = load_qa_chain(model, chain_type="stuff", prompt=prompt)

    return chain

def perform_query_search(query):
    print("\nYour question:")
    print("-------------")
    print(query)

    # Initialize MongoDB python client
    mongodb_conn_string = os.getenv('MONGODB_CONN_STRING')
    db_name = os.getenv('DB_NAME')
    collection_name = os.getenv('COLLECTION_NAME')  # Renamed for clarity
    index_name = os.getenv('INDEX_NAME')

    client = MongoClient(mongodb_conn_string)  # Connect to MongoDB
    db = client[db_name]  # Access the database
    collection = db[collection_name]  # Access the collection

    embeddings = GoogleGenerativeAIEmbeddings(model="models/embedding-001")

    # Initialize vector store with the actual collection object, not the name
    vectorStore = MongoDBAtlasVectorSearch(
        collection, embeddings, index_name=index_name
    )

    print("---------------")
    docs = vectorStore.max_marginal_relevance_search(query, K=1)

    # print(docs[0].metadata['title'])
    print(docs[0].page_content)

    chain = get_conversational_chain()

    response = chain.invoke(
        {"input_documents": docs, "question": query}, return_only_outputs=True
    )
    return response["output_text"]

    # Print the response to the console
    # print(response)
    # print("=============================================")
    # Assuming 'st' is a Streamlit module, display the response in a Streamlit app
    # print(response["output_text"])

# if __name__ == "__main__":
#     parser = argparse.ArgumentParser(description='Atlas Vector Search Demo')
#     parser.add_argument('-q', '--question', required=True, help="The question to ask")
#     args = parser.parse_args()

#     perform_query_search(args.question)