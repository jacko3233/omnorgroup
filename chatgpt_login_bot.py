# WARNING: This is a demonstration script. Do not share or hardcode your credentials in plain text. Use environment variables or other secure storage for any sensitive information.
#!/usr/bin/env python3
"""
Example script demonstrating how to log into a web service and allow
ChatGPT to interpret commands for further actions. Replace the login
URL and API endpoints with the real service you control.
"""

import os
import getpass
import requests
import openai

openai.api_key = os.getenv("OPENAI_API_KEY")

# Placeholder URLs. Update with the actual service URLs.
LOGIN_URL = "https://example.com/login"
API_ENDPOINT = "https://example.com/api"

session = requests.Session()

def login(username: str, password: str) -> bool:
    """Send a login request to the service."""
    payload = {"username": username, "password": password}
    resp = session.post(LOGIN_URL, data=payload)
    resp.raise_for_status()
    return "success" in resp.text.lower()

def perform_action(action: str):
    """Send an action to the service. This is a placeholder."""
    resp = session.post(API_ENDPOINT, json={"action": action})
    resp.raise_for_status()
    return resp.json()

def chatgpt_command(prompt: str) -> str:
    """Send the user's instruction to ChatGPT and return its reply."""
    messages = [
        {
            "role": "system",
            "content": (
                "You are an assistant that translates user instructions into simple "
                "actions for an online service."
            ),
        },
        {"role": "user", "content": prompt},
    ]
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=messages,
    )
    return response["choices"][0]["message"]["content"].strip()

def main():
    username = input("Username: ")
    password = getpass.getpass("Password: ")

    try:
        if not login(username, password):
            print("Login failed. Check your credentials.")
            return
    except Exception as exc:
        print(f"Login request failed: {exc}")
        return

    print("Logged in. Type commands for ChatGPT (or 'quit' to exit).")
    while True:
        user_input = input("> ").strip()
        if user_input.lower() in {"quit", "exit"}:
            break
        try:
            gpt_reply = chatgpt_command(user_input)
            print("ChatGPT reply:", gpt_reply)
            result = perform_action(gpt_reply)
            print("Service response:", result)
        except Exception as exc:
            print(f"Error performing action: {exc}")

if __name__ == "__main__":
    main()
