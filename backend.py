from fastapi import Depends, FastAPI
from fastapi.security import HTTPBasicCredentials, HTTPBasic

app = FastAPI()

security = HTTPBasic()


@app.get("/messages")
async def get_messages():
    return {"messages": "Hello world"}
