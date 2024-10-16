import re
from info import API_KEY, ASSIST_ID
from openai import OpenAI
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from urllib.parse import quote



import time
from openai import OpenAI
import logging

logger = logging.getLogger(name='GPT_Service')


def pretty_print(messages):
    print("# Messages")
    for m in messages:
        print(f"{m.role}: {m.content[0].text.value}")
        answer = m.content[0].text.value
    print()
    return answer


class ChatGPTSession:
    def __init__(self, client, assistant_id, previous_rounds=[]):
        self.client = client
        self.assistant_id = assistant_id

        self.thread = client.beta.threads.create()
        self.thread_id = self.thread.id
            
        print(self.thread_id)

    def create_msg(self, user_msg):
        message_create = self.client.beta.threads.messages.create(
            role="user",
            thread_id=self.thread_id,
            content=f"{user_msg}"
        )
        print(f"Что создалось: {message_create}")

    def thread_running(self):
        run = self.client.beta.threads.runs.create(
            thread_id=self.thread_id,
            assistant_id=self.assistant_id
        )
        return run

    def get_response(self, thread_id):
        return self.client.beta.threads.messages.list(thread_id=thread_id, order="asc")
    
    
    def ask_assistant(self, user_msg):
        self.create_msg(user_msg)
        run = self.thread_running()
       
        while run.status == "queued" or run.status == "in_progress":
            run = self.client.beta.threads.runs.retrieve(
                thread_id=self.thread.id,
                run_id=run.id,
            )
            time.sleep(0.5)
        return run


