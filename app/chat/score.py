import random
from app.chat.redis import client

def random_component_by_score(component_type, component_map):
    # make sure component_type is 'llm' or 'retriever' or 'memory
    if component_type not in ["llm","retriever","memory"]:
        raise ValueError("Invalid component type")
    
    # from Redis, get the has containing the sum total socres for the given
    # component type (current score)
    values = client.hgetall(f"{component_type}_score_values")
    
    # From Redis, get the has containing the number of times each component
    # has been voted on (total votes)
    counts = client.hgetall(f"{component_type}_score_counts")
    
    # Debug/Note: Redis stores all values as strings, no numbers
    # print (values,counts)
    
    # Get all the valid component names from the component map
    names = component_map.keys()
    
    # Loop over the valid names and use them to calculate the average score
    # for each component type
    # & add average score to a dictionary
    avg_scores = {}
    for name in names:
        score = int(values.get(name, 1))
        count = int(counts.get(name,1))
        avg = score / count
        # Cover the first vote being a down vote
        avg_scores[name] = max(avg,0.1)

    # print(avg_scores)

    # Do a weighted random selection
    ## sum average scores
    sum_scores = sum(avg_scores.values())
    ## pick a random number
    random_val = random.uniform(0,sum_scores)
    cumulative = 0
    for name, score in avg_scores.items():
        cumulative += score
        if random_val <= cumulative:
            return name

def score_conversation(
    conversation_id: str, score: float, llm: str, retriever: str, memory: str
) -> None:
    
    # ensure score is within 0 or 1
    score = min(max(score,0), 1)
    
    # Note: Redis does not have an AVERAGE function so we must store
    #       total vote count and the score running count. 
    # Note: to manually review redis hashes, go into a shell and
    # run 'redis-cli' and enter: HGETALL <hashname> (ie: llm_score_values)
    
    # increment running total scores and total count for LLM,
    # retriever and memory scoring
    client.hincrby("llm_score_values", llm, score) 
    client.hincrby("llm_score_counts", llm, 1)
    
    client.hincrby("retriever_score_values", retriever, score) 
    client.hincrby("retriever_score_counts", retriever, 1)

    client.hincrby("memory_score_values", memory, score) 
    client.hincrby("memory_score_counts", memory, 1)

def get_scores():
    # initialize all the keys in the componennt map
    aggregate = {"llm": {}, "retriever": {}, "memory": {} }
    # iterate overa ll the component map keys
    for component_type in aggregate.keys():
        # pull the current score values and counts from redis
        values = client.hgetall(f"{component_type}_score_values")
        counts = client.hgetall(f"{component_type}_score_counts")
        
        # pull in all the score value keys so calculate only those keys and not
        # old ones
        names = values.keys()
        
        # for each score value name, get individual scores and counts
        # calculate the average and add these values into the aggregate
        # dictioary
        for name in names: 
            score = int(values.get(name,1))
            count = int(counts.get(name,1))
            avg = score / count
            aggregate[component_type][name] = [avg]
    
    return aggregate
        
