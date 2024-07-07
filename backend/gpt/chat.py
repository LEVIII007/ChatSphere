from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.runnables.history import RunnableWithMessageHistory
from langchain_openai import ChatOpenAI
from langchain.agents import create_openai_functions_agent, AgentExecutor
from langchain_community.tools.tavily_search import TavilySearchResults
from langchain.tools.retriever import create_retriever_tool

from dotenv import load_dotenv
load_dotenv()
import os

from langchain_openai import ChatOpenAI
from langchain.memory import ConversationBufferMemory
from langchain.chains import LLMChain

from langchain_google_genai import GoogleGenerativeAIEmbeddings, ChatGoogleGenerativeAI
from langchain_mongodb.chat_message_histories import MongoDBChatMessageHistory
from langchain_mongodb import MongoDBAtlasVectorSearch
from pymongo import MongoClient


mongodb_conn_string = os.getenv('MONGODB_CONN_STRING')
db_name = os.getenv('DB_NAME')
collection_name = os.getenv('COLLECTION_NAME')  # Renamed for clarity
index_name = os.getenv('INDEX_NAME')
model = ChatGoogleGenerativeAI(model="gemini-pro", temperature=0.3)

from langchain.prompts import (
    ChatPromptTemplate,
    MessagesPlaceholder,
)

model = ChatOpenAI(     #chain 1
    model="gpt-3.5-turbo",
    temperature=0.6
)

client = MongoClient(mongodb_conn_string)  # Connect to MongoDB
db = client[db_name]  # Access the database
collection = db[collection_name]  # Access the collection

embeddings = GoogleGenerativeAIEmbeddings(model="models/embedding-001")
vectorStore = MongoDBAtlasVectorSearch(
    collection, embeddings, index_name=index_name
)
retriever = vectorStore.as_retriever(search_kwargs={"k": 3})

prompt = ChatPromptTemplate.from_messages([           #chain 2
        ("system", "You are a friendly AI assistant."),
        MessagesPlaceholder(variable_name="history"),
        ("human", "{question}"),
        MessagesPlaceholder(variable_name="agent_scratchpad")

    ])

search = TavilySearchResults()
retriever_tools = create_retriever_tool(
    retriever,
    "Document_search",
    "Use this tool to get infromation about the topic when user asks to refer documents, or contexts."
)
tools = [search, retriever_tools]

agent = create_openai_functions_agent(
    llm=model,
    prompt=prompt,
    tools=tools,
)

agentExecutor = AgentExecutor(
    agent=agent,
    tools=tools
)

chain = agentExecutor

chain_with_history = RunnableWithMessageHistory(
    chain,
    lambda session_id: MongoDBChatMessageHistory(
        session_id=session_id,
        connection_string= os.getenv("MONGODB_CONN_STRING"),
        database_name= os.getenv("DB_NAME"),
        collection_name= os.getenv("CHAT_COLLECTION_NAME"),
        
    ),
    input_messages_key="question",
    history_messages_key="history",
)

# This is where we configure the session id
config = {"configurable": {"session_id": "mongo_db_chat_test"}}

# Prompt 1
# q1 = { "input": "My name is Leon" }
# resp1 = chain.invoke({ 'question' q1, config = config)
# response = chain_with_history.invoke({"question": "Hi! I'm bob"}, config=config)
# print(response["output"])

# if __name__ == '__main__':
#     chat_history = []

#     while True:
#         user_input = input("You: ")
#         if user_input.lower() == 'exit':
#             break

#         response = chain_with_history.invoke({"question": user_input}, config=config)
#         print(response["output"])


def Response(user_message):
    response = chain_with_history.invoke({"question": user_message}, config=config)
    return response["output"]

