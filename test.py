from typing import Any
from uuid import UUID
from langchain_core.outputs import ChatGenerationChunk, GenerationChunk
from langchain_openai import ChatOpenAI
from langchain.prompts import ChatPromptTemplate
from langchain.chains import LLMChain
from langchain.callbacks.base import BaseCallbackHandler
from dotenv import load_dotenv
from queue import Queue
from threading import Thread

load_dotenv()

# No global queue 
# queue = Queue()

# Use a custom streamhanlder subclass to intercept incoming
# chunks from OAI and override the default stream behavior. Requires handler to be implemented
# in ChatOpenAI. Implement a queue between OAI and LLMChain
# to print out messages in chunks. Use concurrency to ensure
# call to LLMChain isn't blocked, avoiding full response message
# output. Lastly, implement per-instance queues and handlers vs.
# sharing these items globally across all user's chats.

class StreamingHandler(BaseCallbackHandler):
    def __init__(self,queue):
        self.queue=queue
    def on_llm_new_token(self, token, **kwargs):
        self.queue.put(token)
    def on_llm_end(self,repsonse,**kwargs):
        self.queue.put(None)
    def on_llm_error(self,error,**kwargs):
        self.queue.put(None)
        
# create subclass of LLMChain to override stream()
class StreamableChain:
    def stream(self, input):
        queue = Queue()
        handler = StreamingHandler(queue)
        
        def task():
            self(input,callbacks=[handler]) # LLMChain is blocking until full response completion
        
        Thread(target=task).start()
        
        while True: 
            token = queue.get()
            if token is None:
                break
            yield token

# Note: streaming=True controls how OAI responds to Langchain
chat = ChatOpenAI(
    streaming=True,
 # Do not initiate callbacks here, its global.    
 #   callbacks=[StreamingHandler()]
)

prompt = ChatPromptTemplate.from_messages([
    ("human","{content}")
])

# Use a mixin pattern to re-define StreamingChain that makes
# it easier to derive new chain and stream types with minimal
# coding effort
class StreamingChain(StreamableChain,LLMChain):
    pass
        
chain = StreamingChain(llm=chat, prompt=prompt)
for output in chain.stream(input={"content":"tell me a joke" }):
    print(output)

# chain.stream('hi')

# LLMChain wants the full repsonse from OAI prior to delivering to the client
# chain = LLMChain(llm=chat, prompt=prompt)

# Below chain call does not produce a streamed response
# output = chain("tell me a joke")

# Below revised chain.stream returns a generator but just has 1 value in it - the completed response
# Chains do not want to stream ?????
# for output in chain.stream(input={"content":"tell me a joke"} ):
#     print(output)
    
# Need to use callbacks to print chunks

    

# Reminder: No chains invovled below, just testing and figuring stuff out

# messages = prompt.format_messages(content="tell me a joke")

# How we invoke the method contorls how Langchain repsonds to the user AND
# how OAI responds to Langchain

# Below did not work, not streaming
# output = chat.invoke(messages)

# chat.stream*() returns a generator
# output = chat.stream(messages)

# iterate using generator
# Note: the method below seems to overrite the ChatOpenAI contructor when streaming=False
# for message in chat.stream(messages):
#    print(message.content)
