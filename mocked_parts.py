import json
from typing import List


async def call_external_service(messages: List[str]):
    """
    Mock external AI provider
    :param messages: The messages to send to the AI provider
    :return: The response of the AI provider
    """
    response = json.loads(
        """{
        "id": "chatcmpl-7UkgnSDzlevZxiy0YjZcLYdUMz5yZ",
        "object": "chat.completion",
        "created": 1687563669,
        "model": "gpt-3.5-turbo-0301",
        "choices": [
            {
                "index": 0,
                "message": {
                    "role": "assistant",
                    "content": "Hello! How can I assist you today?"
                },
                "finish_reason": "stop"
            }
        ],
        "usage": {
            "prompt_tokens": 39,
            "completion_tokens": 3,
            "total_tokens": 42
        }
    }"""
        )
    return response
