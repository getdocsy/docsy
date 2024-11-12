import logging
import textwrap
from openai import OpenAI

# Create a logger instance for this module
logger = logging.getLogger(__name__)

def _log_messages(message_list: list[dict]):
    logger.info("Querying AI")
    for message in message_list:
        content = (
            message["role"]
            + ": "
            + textwrap.shorten(message["content"], width=90, placeholder="...")
        )
        logger.debug(content)

def _log_response(response: str):
    logger.info("AI responsed")
    logger.debug(textwrap.shorten(response, width=100, placeholder="..."))

def get_suggestion(message_list: list[dict]) -> str:
    AI_MODEL = "gpt-4o-mini"

    client = OpenAI()
    base_messages = [
        {
            "role": "system",
            "content": (
                "You are Docsy, a friendly AI coworker. "
                "Your are an expert in structuring, writing and styling software documentation for software companies. "
            ),
        },
    ]
    complete_message_list = base_messages + message_list
    _log_messages(complete_message_list)

    completion = client.chat.completions.create(model=AI_MODEL, messages=complete_message_list)
    suggestion = completion.choices[0].message.content

    _log_response(suggestion)

    return suggestion