import secrets
from typing import Annotated

from fastapi import Depends, FastAPI, HTTPException, status
from fastapi.security import HTTPBasicCredentials, HTTPBasic

app = FastAPI()

security = HTTPBasic()


def authenticate(
        credentials: Annotated[HTTPBasicCredentials, Depends(security)]
):
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
async def get_messages():
    return {"messages": "Hello world"}


@app.post("/messages")
async def send_message(
        message: str,
        credentials: Annotated[HTTPBasicCredentials, Depends(security)]
):
    authenticate(credentials)
    return {"messages": "Successful authentication"}
