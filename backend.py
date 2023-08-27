import secrets
from typing import Annotated

from fastapi import Depends, FastAPI, HTTPException, status
from fastapi.security import HTTPBasicCredentials, HTTPBasic

import mocked_parts

app = FastAPI()

security = HTTPBasic()


def authenticate(
        credentials: Annotated[HTTPBasicCredentials, Depends(security)]
):
    """
    :param credentials: HTTPBasicCredentials (password and username) of the user
    """
    is_username_correct = secrets.compare_digest(
        credentials.username,
        "test_user"
    )
    is_password_correct = secrets.compare_digest(
        credentials.password,
        "test_password"
    )
    if not (is_username_correct and is_password_correct):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect password or username"
        )


@app.get("/messages")
async def get_messages(number_of_messages: int = 10):
    """
    Returns the last n messages
    :param number_of_messages: the number of messages to return
    :return: the last n messages
    """
    return {"messages": "Hello world"}


@app.post("/messages")
async def send_message(
        message: str,
        credentials: Annotated[HTTPBasicCredentials, Depends(security)]
):
    """
    Sends a message to the chatbot
    :param message: The message to send
    :param credentials: The credentials of the user
    :return: The response of the chatbot
    """
    authenticate(credentials)
    response = await mocked_parts.call_external_service([message])
    return response['choices'][0]['message']['content']
