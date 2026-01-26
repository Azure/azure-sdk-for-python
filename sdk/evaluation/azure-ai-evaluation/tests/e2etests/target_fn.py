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
        # Only include text in assistant response (matching the working imageurls test pattern)
        messages.append(
            {
                "role": "assistant",
                "content": [
                    {
                        "type": "text",
                        "text": "The image depicts a person with short, brown hair that appears to be styled neatly. "
                        "They are wearing a dark-colored, possibly navy blue, crew-neck shirt. "
                        "The background appears to be dark, possibly indicating an indoor setting with minimal lighting.",
                    },
                ],
            }
        )
        conversation["messages"] = messages
    return {"conversation": conversation}
