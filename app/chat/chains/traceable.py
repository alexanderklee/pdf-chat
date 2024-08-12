from langfuse.model import CreateTrace
from app.chat.tracing.langfuse import langfuse

class TraceableChain:
    # override __call__ function to add tracing to all calls using this method
    def __call__(self, *args, **kwargs):
        trace = langfuse.trace(
            CreateTrace(
                # Tell languse to use conversation_id to add or append new
                # spans based on this id (aka, a chat thread vs. new chat)
                id=self.metadata["conversation_id"],
                metadata=self.metadata
            )
        )
        
        # Need to identify a list of callbacks. No gaurantee that callbacks will exist,
        # if not, return empty list
        callbacks = kwargs.get("callbacks",[])
        # Append getNewHandler to that list
        callbacks.append(trace.getNewHandler())
        # reassign the list of callbacks to kwargs
        kwargs["callbacks"] = callbacks
        
        return super().__call__(*args, **kwargs)