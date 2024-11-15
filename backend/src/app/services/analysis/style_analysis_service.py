from textwrap import dedent

from pydantic import BaseModel

from app.models import RepoMap
from app.services import ai_service, local_repo_service
from app.services.repo_map_service import get_relative_file_path_to_headings


class StyleIssue(BaseModel):
    line_number: int
    quote: str
    issue_explanation: str
    suggested_fix: str | None


class DetailedStyleAnalysis(BaseModel):
    path: str
    style_issues: list[StyleIssue]


class StyleAnalysis(BaseModel):
    files: list[DetailedStyleAnalysis]


class StyleAnalysisResult(BaseModel):
    analysis: StyleAnalysis
    score_components: dict[str, int]
    total_score: int


def analyze_style(*, local_repo_path: str, repo_map: RepoMap) -> StyleAnalysisResult:
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

    analysis = ai_service.get_suggestion_json(
        message_list=message_list, model=StyleAnalysis
    )
    score_components = score_components_style(analysis=analysis)
    total_score = round(sum(score_components.values()) / len(score_components))

    return StyleAnalysisResult(
        analysis=analysis, score_components=score_components, total_score=total_score
    )


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


def score_components_style(*, analysis: StyleAnalysis) -> dict[str, int]:
    score_components = {}
    for file in analysis.files:
        file_score = 0
        if len(file.style_issues) == 0:
            file_score = 100
        elif len(file.style_issues) == 1:
            file_score = 90
        elif len(file.style_issues) == 2:
            file_score = 80
        elif len(file.style_issues) >= 3:
            # Leads to a score between 0 and 70
            file_score = max(100 - len(file.style_issues) * 10, 0)

        score_components[file.path] = file_score

    return score_components
