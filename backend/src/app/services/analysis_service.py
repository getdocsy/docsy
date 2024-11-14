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

from app.services import repo_map_service
from app.services.repo_map_service import RepoMap, get_relative_file_path_to_headings


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
    with local_repo_service.temp_clone_repo(repo=repo) as local_repo_path:
        repo_map = repo_map_service.create_repo_map(
            repo=repo, local_repo_path=local_repo_path
        )

        analysis_result = {}
        analysis_result["structure"] = analyze_structure(
            local_repo_path=local_repo_path, repo_map=repo_map
        )
        analysis_result["content"] = analyze_content(
            local_repo_path=local_repo_path, repo_map=repo_map
        )
        analysis_result["style"] = analyze_style(
            local_repo_path=local_repo_path, repo_map=repo_map
        )

        analysis = Analysis(
            repo=repo,
            result=analysis_result,
        )
        analysis.save()

        return analysis_result


class FileClassification(BaseModel):
    path: str
    classification: str
    confidence_score: int


class StructureAnalysis(BaseModel):
    files: list[FileClassification]
    what_is_good: str
    what_is_bad: str
    score: int


def analyze_structure(*, local_repo_path: str, repo_map: RepoMap) -> dict:
    relative_file_path_to_headings = get_relative_file_path_to_headings(
        repo_map=repo_map
    )

    # classify each page based on divio documentation system with confidence score
    analyze_structure_prompt = """
        You are given a list of files of the documentation with their headings. 
        Please classify each file based on the divio documentation system as either Tutorial, How-to guide, Reference or Explanation. 
        You should also provide a confidence score for each classification. 
        The confidence score should be a number between 0 and 100, where 0 means you are not confident at all and 100 means you are absolutely certain.

        Include an overall score for the structure of the documentation as a number between 0 and 100. 0 means the structure is completely incoherent and 100 means the structure is perfect.
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
    what_is_good: str
    what_is_bad: str
    score: int


def analyze_content(*, local_repo_path: str, repo_map: RepoMap) -> dict:
    relative_file_path_to_headings = get_relative_file_path_to_headings(
        repo_map=repo_map
    )

    analyze_content_prompt = """
        You will be provided with the structure of a software product documentation.
        Your goal will be to answer three questions about the product.
        Here is a description of the parameters:
        - problem: Which problem does the product solve?
        - getting_started: How do I get started with the product?
        - important_concepts: What are the most important concepts?
        - what_is_good: What is good about the content?
        - what_is_bad: What is bad about the content?
        - score: Include an overall score for the structure of the documentation as a number between 0 and 100. 0 means the structure is completely incoherent and 100 means the structure is perfect.
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


class StyleIssue(BaseModel):
    line_number: int
    quote: str
    explanation: str
    suggested_fix: str


class DetailedStyleAnalysis(BaseModel):
    path: str
    style_issues: list[StyleIssue]


class StyleAnalysis(BaseModel):
    files: list[DetailedStyleAnalysis]
    has_conventions_file: bool
    what_is_good: str
    what_is_bad: str
    score: int


def analyze_style(*, local_repo_path: str, repo_map: RepoMap) -> dict:
    first_three_relative_file_path_list = list(
        get_relative_file_path_to_headings(repo_map=repo_map).keys()
    )[:3]

    detailed_style_analysis_list = []
    for relative_file_path in first_three_relative_file_path_list:
        detailed_style_analysis = analyze_file_style(
            local_repo_path=local_repo_path, relative_file_path=relative_file_path
        )
        detailed_style_analysis_list.append(detailed_style_analysis)

    analyze_style_prompt = """
        You will be provided with detailed style analysis of files of a software product documentation.
        Here is a description of the parameters:
        - has_conventions_file: Does the documentation have a conventions.md file?
        - what_is_good: What is good about the style?
        - what_is_bad: What is bad about the style?
        - score: Include an overall score for the style of the documentation as a number between 0 and 100. 0 means bad, 100 means good.
    """
    message_list = [
        {"role": "system", "content": dedent(analyze_style_prompt)},
    ]
    for detailed_style_analysis in detailed_style_analysis_list:
        message_list.append(
            {
                "role": "user",
                "content": f"file_path: {detailed_style_analysis.path}\nstyle_issues: {str(detailed_style_analysis.style_issues)}",
            }
        )

    analysis_result = ai_service.get_suggestion_json(
        message_list=message_list, model=StyleAnalysis
    )
    return analysis_result.model_dump()


def analyze_file_style(
    *, local_repo_path: str, relative_file_path: str
) -> DetailedStyleAnalysis:
    analyze_file_style_prompt = """
        You will be provided with a file of a software product documentation. The file has line numbers.

        Here is the style guide for the documentation:
        - The primary language of the documentation is English.
        - Prefer active voice over passive voice.
        - Use tenses consistently. Prefer present tense over future or past tense.
        - Keep your texts concise and avoid wordiness.

        Review the file and point out examples of bad style with a short explanation and a suggested fix.
        If you are unsure about the style, do not point it out.
        If you find sentences that are hard to understand, point them out.

        Here is the file content:
    """

    file_content_with_line_numbers = (
        local_repo_service.get_file_content_with_line_numbers(
            local_repo_path=local_repo_path, relative_file_path=relative_file_path
        )
    )

    message_list = [
        {"role": "system", "content": dedent(analyze_file_style_prompt)},
        {"role": "user", "content": f"file_path: {relative_file_path}"},
        {"role": "user", "content": file_content_with_line_numbers},
    ]
    return ai_service.get_suggestion_json(
        message_list=message_list, model=DetailedStyleAnalysis
    )
