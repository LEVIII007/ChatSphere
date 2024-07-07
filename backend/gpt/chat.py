from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.runnables.history import RunnableWithMessageHistory
from langchain_openai import ChatOpenAI


from dotenv import load_dotenv
load_dotenv()
import os

from langchain_openai import ChatOpenAI
from langchain.memory import ConversationBufferMemory
from langchain.chains import LLMChain


from langchain_mongodb.chat_message_histories import MongoDBChatMessageHistory


from langchain.prompts import (
    ChatPromptTemplate,
    MessagesPlaceholder,
)

model = ChatOpenAI(     #chain 1
    model="gpt-3.5-turbo",
    temperature=0.6
)

prompt = ChatPromptTemplate.from_messages([           #chain 2
        ("system", "You are a friendly AI assistant."),
        MessagesPlaceholder(variable_name="history"),
        ("human", "{question}")
    ])

chain = prompt | model

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
print(chain_with_history.invoke({"question": "Hi! I'm bob"}, config=config))

# # Prompt 2
# q2 = { "input": "What is my name?" }
# resp2 = chain.invoke(q2, config = config)
# print(resp2["text"])