import os
from dotenv import load_dotenv


class Settings:
    def __init__(self):
        self.openai_api_key = os.getenv("OPENAI_API_KEY")


def get_settings() -> Settings:
    return Settings()


# Load .env at import time (app startup)
load_dotenv()
