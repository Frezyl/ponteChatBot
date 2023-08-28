from os import getenv

import psycopg2


class Database:

    def __init__(self):
        postgres_pw = getenv("POSTGRES_PASSWORD")

        self.conn = psycopg2.connect(
            database="postgres",
            user="postgres",
            password=postgres_pw,
            host="127.0.0.1",
            port="5432"
        )

        print("Database opened successfully")

    def new_user(self, data: tuple):
        """
        Adds a new user to the database
        :param data: name and password of the user
        """
        cur = self.conn.cursor()
        cur.execute(
            "INSERT INTO users (name,password) VALUES (%s, %s)",
            data
        )

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
            "INSERT INTO messages (username, text) VALUES (%s, %s)",
            (user, message,)
        )
        self.conn.commit()
