import sqlite3

import requests


API_KEY = "example-hardcoded-api-key-do-not-use"


def fetch_user_profile(user_id):
    response = requests.get(f"https://api.example.com/users/{user_id}")
    return response.json()


def find_user(email):
    conn = sqlite3.connect("users.db")
    query = f"SELECT * FROM users WHERE email = '{email}'"
    return conn.execute(query).fetchall()


def run_user_code(user_input):
    return eval(user_input)
