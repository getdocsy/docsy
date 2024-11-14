import os
from pathlib import Path
from textwrap import dedent
from app import custom_errors
from app.models import Analysis, Repo
from app.services import (
    ai_service,
    local_repo_service,
    remote_repo_service,
)
from pydantic import BaseModel


def get_latest_analysis_by_github_full_name(
    *, sanitized_github_full_name: str
) -> Analysis:
    return (
        Analysis.objects.filter(repo__nfkc_github_full_name=sanitized_github_full_name)
        .order_by("-created_at")
        .first()
    )


def analyze_remote_repo(*, sanitized_github_full_name: str) -> dict:
    repo = remote_repo_service.get_repo_by_github_full_name(
        sanitized_github_full_name=sanitized_github_full_name
    )
    return analyze_repo(repo=repo)


def analyze_repo(*, repo: Repo) -> dict:
    analysis_status = Analysis.STATUS_PENDING
    analysis = Analysis(repo=repo, status=analysis_status)
    analysis.save()
    with local_repo_service.temp_clone_repo(repo=repo) as local_repo_path:

        analysis_result = {}
        analysis_result["structure"] = analyze_structure(
            local_repo_path=local_repo_path
        )
        analysis_result["content"] = analyze_content(local_repo_path=local_repo_path)
        analysis_result["style"] = analyze_style(local_repo_path=local_repo_path)

        analysis = Analysis(
            repo=repo,
            result=analysis_result,
            status=Analysis.STATUS_COMPLETE,
        )
        analysis.save()

        return analysis_result


class FileClassification(BaseModel):
    path: str
    classification: str
    confidence_score: int


class StructureAnalysis(BaseModel):
    files: list[FileClassification]


def analyze_structure(*, local_repo_path: str) -> dict:
    relative_file_path_to_headings = (
        local_repo_service.get_relative_markdown_file_path_to_headings(
            local_repo_path=local_repo_path
        )
    )

    # classify each page based on divio documentation system with confidence score
    analyze_structure_prompt = """
        You are given a list of files of the documentation with their headings. 
        Please classify each file based on the divio documentation system as either Tutorial, How-to guide, Reference or Explanation. 
        You should also provide a confidence score for each classification. 
        The confidence score should be a number between 0 and 100, where 0 means you are not confident at all and 100 means you are absolutely certain.
    """
    message_list = [
        {
            "role": "system",
            "content": dedent(analyze_structure_prompt),
        }
    ]
    for relative_file_path, headings in relative_file_path_to_headings.items():
        message_list.append(
            {
                "role": "user",
                "content": f"file_path: {relative_file_path}\nheadings: {headings}",
            }
        )

    analysis_result = ai_service.get_suggestion_json(
        message_list=message_list, model=StructureAnalysis
    )
    return analysis_result.model_dump()


class ContentAnalysis(BaseModel):
    problem: str
    getting_started: str
    important_concepts: str


def analyze_content(*, local_repo_path: str) -> dict:
    relative_file_path_to_headings = (
        local_repo_service.get_relative_markdown_file_path_to_headings(
            local_repo_path=local_repo_path
        )
    )

    analyze_content_prompt = """
        You will be provided with the structure of a software product documentation.
        Your goal will be to answer three questions about the product.
        Here is a description of the parameters:
        - problem: Which problem does the product solve?
        - getting_started: How do I get started with the product?
        - important_concepts: What are the most important concepts?
    """

    message_list = [
        {"role": "system", "content": dedent(analyze_content_prompt)},
    ]
    for relative_file_path, headings in relative_file_path_to_headings.items():
        message_list.append(
            {
                "role": "user",
                "content": f"file_path: {relative_file_path}\nheadings: {headings}",
            }
        )

    analysis_result = ai_service.get_suggestion_json(
        message_list=message_list, model=ContentAnalysis
    )
    return analysis_result.model_dump()


class StyleAnalysis(BaseModel):
    has_conventions_file: bool
    language_consistency: str
    typos: str


def analyze_style(*, local_repo_path: str) -> dict:
    relative_file_path_to_headings = (
        local_repo_service.get_relative_markdown_file_path_to_headings(
            local_repo_path=local_repo_path
        )
    )

    analyze_style_prompt = """
        You will be provided with the structure of a software product documentation.
        Your goal will be to answer three questions about the product.
        Here is a description of the parameters:
        - has_conventions_file: Is there a conventions file?
        - language_consistency: Is the language consistent?
        - typos: Are there any obvious typos?
        To answer the questions, you should inspect up to 3 files.
    """
    message_list = [
        {"role": "system", "content": dedent(analyze_style_prompt)},
    ]
    for relative_file_path, headings in relative_file_path_to_headings.items():
        message_list.append(
            {
                "role": "user",
                "content": f"file_path: {relative_file_path}\nheadings: {headings}",
            }
        )

    analysis_result = ai_service.get_suggestion_json(
        message_list=message_list, model=StyleAnalysis
    )
    return analysis_result.model_dump()
