import secrets
from typing import Annotated

import openai
from fastapi import Depends, FastAPI, HTTPException, Request, status
from fastapi.security import HTTPBasic, HTTPBasicCredentials

import database
import mocked_parts

app = FastAPI()

security = HTTPBasic()

mock_db = mocked_parts.MessageDataBase()

message_data_base = database.PersistentDb()
rate_limit_database = database.RateLimitDb()


def format_new_person_message(message):
    """
    Formats a message from a new person to ChatGPT style
    :param message: Incoming message to format
    :return: Formatted message
    """
    return {"role": "user", "content": message}


def authenticate(
        credentials: Annotated[HTTPBasicCredentials, Depends(security)]
):
    """
    :param credentials: HTTPBasicCredentials (password and username) of the user
    """
    is_username_correct = secrets.compare_digest(
            credentials.username, "test_user"
    )
    is_password_correct = secrets.compare_digest(
            credentials.password, "test_password"
    )
    if not (is_username_correct and is_password_correct):
        raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED, detail="Incorrect password or username"
        )


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
