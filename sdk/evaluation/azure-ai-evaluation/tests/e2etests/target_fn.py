def target_fn(query: str) -> str:
    """An example target function."""
    if "LV-426" in query:
        return {"response": "There is nothing good there."}
    if "central heating" in query:
        return {"response": "There is no central heating on the streets today, but it will be, I promise."}
    if "strange" in query:
        return {"response": "The life is strange..."}


def target_fn2(query: str) -> str:
    response = target_fn(query)["response"]
    return {"response": response}


def target_fn3(query: str) -> str:
    response = target_fn(query)
    response["query"] = f"The query is as follows: {query}"
    return response


def target_multimodal_fn1(conversation) -> str:
    if conversation is not None and "messages" in conversation:
        messages = conversation["messages"]
        messages.append(
            {
                "role": "assistant",
                "content": [
                    {
                        "type": "image_url",
                        "image_url": {"url": "https://cdn.britannica.com/68/178268-050-5B4E7FB6/Tom-Cruise-2013.jpg"},
                    }
                ],
            }
        )
        conversation["messages"] = messages
    return {"conversation": conversation}
