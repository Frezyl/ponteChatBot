from typing import Annotated

import openai
from fastapi import Depends, FastAPI, HTTPException
from fastapi.security import HTTPBasicCredentials
from starlette import status
from starlette.requests import Request

import mocked_parts
from backend import authenticate, format_new_person_message, message_data_base, mock_db, rate_limit_database, security

app = FastAPI()


@app.get("/mock_messages")
async def get_messages(number_of_messages: int = 10):
    """
    Returns the last n messages
    :param number_of_messages: the number of messages to return
    :return: the last n messages
    """
    return mock_db.get_messages(number_of_messages)


@app.post("/mock_messages")
async def send_message(
        request: Request, credentials: Annotated[HTTPBasicCredentials, Depends(security)]
):
    """
    Sends a message to the mock chatbot
    :param request: The request object containing the message
    :param credentials: The credentials of the user
    :return: The response of the chatbot
    """
    body = await request.json()
    message = body['message']

    authenticate(credentials)
    user_exists = rate_limit_database.check_user(credentials.username)
    if user_exists is False:
        rate_limit_database.add_event(credentials.username)
    else:
        if rate_limit_database.check_rate_limit(
                credentials.username, 3
        ) is False:
            raise HTTPException(
                    status_code=status.HTTP_429_TOO_MANY_REQUESTS, detail="Too many requests"
            )
        else:
            rate_limit_database.add_event(credentials.username)
    message = format_new_person_message(message)
    messages = mock_db.get_messages()
    messages.append(message)
    response = await mocked_parts.call_external_service(messages)
    mock_db.add_message(message)
    mock_db.add_message(response['choices'][0]['message'])
    return response['choices'][0]['message']['content']


@app.post("/GPTmessages")
async def send_GPT_message(
        request: Request, credentials: Annotated[HTTPBasicCredentials, Depends(security)]
):
    """
    Sends a message to the real chatbot (ChatGPT 3.5)
    :param request: The request object containing the message
    :param credentials: The credentials of the user (username and password)
    :return: The response of the chatbot
    """

    body = await request.json()
    message = body['message']
    authenticate(credentials)
    user_exists = rate_limit_database.check_user(credentials.username)
    if user_exists is False:
        rate_limit_database.add_event(credentials.username)
    else:
        if rate_limit_database.check_rate_limit(
                credentials.username, 3
        ) is False:
            raise HTTPException(
                    status_code=status.HTTP_429_TOO_MANY_REQUESTS, detail="Too many requests"
            )
        else:
            rate_limit_database.add_event(credentials.username)
    message = format_new_person_message(message)
    messages = message_data_base.query_user_history(credentials.username)
    messages = messages.append(message)
    response = await openai.ChatCompletion.create(
            model="gpt-3.5-turbo", messages=messages
    )
    message_data_base.add_message_to_user(message, credentials.username)
    message_data_base.add_message_to_user(
            response['choices'][0]['message'], credentials.username
    )
    return response['choices'][0]['message']['content']
