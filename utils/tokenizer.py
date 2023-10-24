import tiktoken

TOKENIZER_NAME = "cl100k_base"



def num_tokens_from_messages(messages, tokenizer=TOKENIZER_NAME):
    """Return the number of tokens used by a list of messages. no need to be accurate, just a rough estimation."""
    tokens_per_message = 3
    encoding = tiktoken.get_encoding(tokenizer)
    num_tokens = 0
    for message in messages:
        num_tokens += tokens_per_message
        for key, value in message.items():
            if key == "content" or key == "role":
                num_tokens += len(encoding.encode(value))
    num_tokens += 3  # every reply is primed with <|start|>assistant<|message|>
    return num_tokens