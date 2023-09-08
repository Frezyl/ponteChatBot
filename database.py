import time
from os import getenv
from typing import Annotated

import psycopg2
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBasic, HTTPBasicCredentials

security = HTTPBasic()


class PersistentDb:
    """
    Class for interacting with the persistent database
    """

    def __init__(self):
        postgres_pw = getenv("POSTGRES_PASSWORD")

        self.conn = psycopg2.connect(
                database="postgres", user="postgres", password=postgres_pw, host="127.0.0.1", port="5432"
        )

        print("Database opened successfully")

    def new_user(self, data: tuple):
        """
        Adds a new user to the database
        :param data: name and password of the user
        """
        cur = self.conn.cursor()
        cur.execute("INSERT INTO users (name,password) VALUES (%s, %s)", data)

        self.conn.commit()

    def get_user(self, name: str):
        """
        Gets a user from the database
        :param name: name of the user
        :return: user data
        """
        cur = self.conn.cursor()
        cur.execute("SELECT * FROM users WHERE username = %s", (name,))
        return cur.fetchall()

    def query_all_history(self):
        """
        Gets the conversation history of all user's
        :return: conversation history of all users
        """
        cur = self.conn.cursor()
        cur.execute("SELECT * FROM messages")
        return cur.fetchall()

    def query_user_history(self, user):
        """
        Gets the conversation history of a user
        :param user: name of the user
        :return: conversation history of the user
        """
        cur = self.conn.cursor()
        cur.execute("SELECT * FROM messages WHERE username = %s", (user,))
        return cur.fetchall()

    def add_message_to_user(self, message, user):
        """
        Adds a message to a user's conversation history
        :param message: message to add
        :param user: the name of the user
        """
        cur = self.conn.cursor()
        message = str(message)
        cur.execute(
                "INSERT INTO messages (username, text) VALUES (%s, %s)", (user, message,)
        )
        self.conn.commit()


class RateLimitDb:
    """
    Class for interacting with the in memory rate limit database
    """

    def __init__(self):
        self.limit_info = {}

    def check_user(self, user):
        """
        Checks if a user is in the rate limit database
        :param user: name of the user
        :return: True if the user is in the database, False otherwise
        """
        return user in self.limit_info

    def add_event(self, user):
        """
        Adds an event to the rate limit database
        :param user:
        """
        if self.check_user(user) is False:
            self.limit_info[user] = [time.time()]
        else:
            self.limit_info[user].append(time.time())

    def check_rate_limit(
            self,
            credentials: Annotated[HTTPBasicCredentials, Depends(security)]
    ) -> bool:
        """
        Checks if a user has exceeded the rate limit
        :param credentials: user credentials
        :return: True if the user has not exceeded the rate limit, False otherwise
        """
        user = credentials.username
        if user not in self.limit_info:
            self.limit_info[user] = [time.time()]
            return True
        request_times = self.limit_info[user]
        while request_times and time.time() - request_times[0] > 60:
            request_times.pop(0)
        if len(request_times) < 3:
            request_times.append(time.time())
            return True
        else:
            raise HTTPException(
                    status_code=status.HTTP_429_TOO_MANY_REQUESTS, detail="Rate limit exceeded"
            )
