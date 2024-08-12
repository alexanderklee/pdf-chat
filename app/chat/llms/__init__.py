from functools import partial
from .chatopenai import build_llm

# Usability: use partial kwargs to fill in the model name rather than the user
# ie. builder(chat_args, model_name="gpt-4") <-- not very clean
# 'partial' will fill in the model_name value for you.
llm_map = {
    "gpt-4": partial(build_llm, model_name="gpt-4"),
    "gpt-3.5-turbo": partial(build_llm, model_name="gpt-3.5-turbo")
}