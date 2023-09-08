import secrets
from typing import Annotated

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBasicCredentials

import database
import mocked_parts

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
        credentials: Annotated[HTTPBasicCredentials, Depends(database.security)]
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
