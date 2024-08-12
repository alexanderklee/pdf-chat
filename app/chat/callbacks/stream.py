from langchain.callbacks.base import BaseCallbackHandler

class StreamingHandler(BaseCallbackHandler):
    def __init__(self,queue):
        self.queue=queue
        # need to track with run_ids correlate to which llm
        self.streaming_run_ids = set()
        
    def on_chat_model_start(self, serialized, messages, run_id, **kwargs):
        if serialized["kwargs"]["streaming"]==True:
            print("This is a streaming model (CombineDocsChain), listen to events with a run_id of ", run_id)
            self.streaming_run_ids.add(run_id)
        elif serialized["kwargs"]["streaming"]==False:
            print("This is not a streaming model (CondenseQuestionChain), here is the run_id ", run_id)
        else:
            print("[kwarg][streaming] is not present!")
    def on_llm_new_token(self, token, **kwargs):
        self.queue.put(token)
        
    def on_llm_end(self,repsonse,run_id, **kwargs):
        if run_id in self.streaming_run_ids:
            self.queue.put(None)
            self.streaming_run_ids.remove(run_id)    
    def on_llm_error(self,error,**kwargs):
        self.queue.put(None)