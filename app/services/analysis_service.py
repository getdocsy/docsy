import os
from pathlib import Path
from app import custom_errors
from app.models import Analysis, Repo
from app.services import ai_service, local_repo_service, markdown_file_service, remote_repo_service

def get_latest_analysis_by_github_full_name(*, sanitized_github_full_name: str) -> Analysis:
    repo = remote_repo_service.get_repo_by_github_full_name(sanitized_github_full_name=sanitized_github_full_name)
    result = Analysis.objects.filter(repo=repo).order_by("-created_at").first()
    if not result:
        raise custom_errors.AnalysisNotFoundError(f"No analysis found for {sanitized_github_full_name}")
    return result


def analyze_remote_repo(*, sanitized_github_full_name: str) -> dict:
    repo = remote_repo_service.get_repo_by_github_full_name(sanitized_github_full_name=sanitized_github_full_name)
    return analyze_repo(repo=repo)


def analyze_repo(*, repo: Repo) -> dict:
    with local_repo_service.clone_repo(repo=repo) as local_repo_path:

        analysis_result = {}
        analysis_result["structure"] = analyze_structure(local_repo_path=local_repo_path)
        analysis_result["content"] = analyze_content(local_repo_path=local_repo_path)
        analysis_result["style"] = analyze_style(local_repo_path=local_repo_path)

        analysis = Analysis(repo=repo, analysis_result=analysis_result)
        analysis.save()

        return analysis_result


def analyze_structure(*, local_repo_path: str) -> dict:
    # list all markdown files and their headings
    file_path_to_headings = {}
    for path in Path(local_repo_path).rglob("*.md"):
        file_path_to_headings[os.path.relpath(path, local_repo_path)] = (
            markdown_file_service.get_headings(path=path)
        )

    # classify each page based on divio documentation system with confidence score
    message_list = [
        {
            "role": "system",
            "content": (
                "You are given a list of file paths with their headings. "
                "Please classify each page based on the divio documentation system as either Tutorial, How-to guide, Reference or Explanation. "
                "You should also provide a confidence score for each classification. "
                "The confidence score should be a number between 0 and 100, where 0 means you are not confident at all and 100 means you are absolutely certain."
                "Return your answer as JSON in the following format: "
                "{File path: str, Classification: str, Confidence score: int}"
            ),
        }
    ]
    for file_path, headings in file_path_to_headings.items():
        message_list.append({"role": "user", "content": f"File path: {file_path}\nHeadings: {headings}"})

    analysis_result = ai_service.get_suggestion(message_list)
    return analysis_result


def analyze_content(*, local_repo_path: str) -> dict:
    # Only look at first page and answer:
    # What is the product about?
    # How do I get started?
    # What are the most important terms?
    # Generate three questions based on first page
    # Try to answer them by looking at one page per question. List questions and answers
    pass


def analyze_style(*, local_repo_path: str) -> dict:
    # If there is a conventions file, is it ahdered to in the first 2 pages?
    # Pick three random pages and check if language is consistent.
    # Any obvious typos?
    pass
