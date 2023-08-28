import threading
import time
import unittest
from concurrent.futures import ThreadPoolExecutor
from unittest.mock import patch, mock_open

import requests
import uvicorn

with open("../data/test_conversation_history.json") as f:
    data = f.read()
    m = mock_open(read_data=data)
    with patch("mocked_parts.open", m):
        import backend

with ThreadPoolExecutor(max_workers=1) as executor:
    thread = threading.Thread(
        target=uvicorn.run,
        args=(backend.app,),
        kwargs={"host": "localhost", "port": 8000}
    )
    thread.start()
    time.sleep(5)


class MyTestCase(unittest.TestCase):
    def test_authenticate(self):
        response = requests.post(
            "http://localhost:8000/mock_messages?message=First message",
            auth=("test_user", "test_password")
        )
        self.assertEqual(response.status_code, 200)

    def test_authenticate_wrong_pw(self):
        response = requests.post(
            "http://localhost:8000/mock_messages?message=First message",
            auth=("test_user", "wrong_password")
        )
        self.assertEqual(response.status_code, 401)

    def test_authenticate_wrong_username(self):
        response = requests.post(
            "http://localhost:8000/mock_messages?message=First message",
            auth=("wrong_user", "test_password")
        )
        self.assertEqual(response.status_code, 401)

    def test_get_messages(self):
        response = requests.get(
            "http://localhost:8000/mock_messages"
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.json()), 10)


if __name__ == '__main__':
    unittest.main()
