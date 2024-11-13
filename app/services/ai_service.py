import json
import logging
import textwrap
from openai import OpenAI
from typing import Type, TypeVar
from pydantic import BaseModel

from app.services.local_repo_service import get_file_content

# Create a logger instance for this module
logger = logging.getLogger(__name__)

AI_MODEL = "gpt-4o-mini"
base_messages = [
    {
        "role": "system",
        "content": (
            "You are Docsy, a friendly AI coworker. "
            "Your are an expert in structuring, writing and styling software documentation for software companies. "
        ),
    },
]

T = TypeVar("T", bound=BaseModel)


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


def get_suggestion_str(message_list: list[dict]) -> str:
    client = OpenAI()

    complete_message_list = base_messages + message_list
    _log_messages(complete_message_list)

    completion = client.chat.completions.create(
        model=AI_MODEL, messages=complete_message_list
    )
    suggestion = completion.choices[0].message.content

    _log_response(suggestion)

    return suggestion


def get_suggestion_json(*, message_list: list, model: Type[T]) -> T:
    client = OpenAI()

    complete_message_list = base_messages + message_list + [
        {
            "role": "system",
            "content": f"Return your answer as JSON.",
        },
        {
            "role": "system",
            "content": f"Do not include any other text than the JSON object. No fencings or other text.",
        },
    ]
    _log_messages(complete_message_list)

    completion = client.beta.chat.completions.parse(
        model=AI_MODEL, messages=complete_message_list, response_format=model
    )
    suggestion = completion.choices[0].message.parsed

    _log_response(suggestion.model_dump_json())
    return suggestion


def get_suggestion_json_with_tools(*, message_list: list, model: Type[T]) -> T:
    client = OpenAI()

    complete_message_list = base_messages + message_list + [
        {
            "role": "system",
            "content": f"Return your answer as JSON.",
        },
        {
            "role": "system",
            "content": f"Do not include any other text than the JSON object. No fencings or other text.",
        },
    ]
    _log_messages(complete_message_list)

    tools = [
        {
            "type": "function",
            "function": {
                "name": "get_file_content",
                "description": "Call this whenever you need to know the content of a file",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "file_path": {
                            "type": "string",
                            "description": "The path to the file.",
                        },
                    },
                    "required": ["file_path"],
                    "additionalProperties": False,
                },
            },
        }
    ]
    response = client.chat.completions.create(
        model=AI_MODEL,
        messages=complete_message_list,
        tools=tools,
    )
    tool_call = response.choices[0].message.tool_calls[0]
    arguments = json.loads(tool_call["function"]["arguments"])

    relative_file_path = arguments.get("file_path")
    file_content = get_file_content(local_repo_path=local_repo_path, relative_file_path=relative_file_path)
    _log_response(suggestion)
