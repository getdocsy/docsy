from textwrap import dedent
from pydantic import BaseModel

from app.models import RepoMap
from app.services import ai_service
from app.services.repo_map_service import get_relative_file_path_to_headings


class FileAnalysis(BaseModel):
    file_path: str
    tutorial_subheadings: list[str]
    howto_subheadings: list[str]
    reference_subheadings: list[str]
    explanation_subheadings: list[str]


class SingleFunctionAnalysis(BaseModel):
    files: list[FileAnalysis]


class SingleFunctionAnalysisResult(BaseModel):
    analysis: SingleFunctionAnalysis
    score_components: dict[str, int]
    total_score: int


async def analyze_single_function(*, repo_map: RepoMap) -> SingleFunctionAnalysisResult:
    relative_file_path_to_headings = get_relative_file_path_to_headings(
        repo_map=repo_map
    )
    analyze_single_function_prompt = """
        You are given a list of files of the documentation with their headings. 
        Please classify each subheading in each file based on the divio documentation system as either Tutorial, How-to guide, Reference or Explanation. 
    """
    message_list = [
        {
            "role": "system",
            "content": dedent(analyze_single_function_prompt),
        }
    ]
    for relative_file_path, headings in relative_file_path_to_headings.items():
        message_list.append(
            {
                "role": "user",
                "content": f"file_path: {relative_file_path}\nheadings: {headings}",
            }
        )

    analysis = await ai_service.get_suggestion_json(
        message_list=message_list, model=SingleFunctionAnalysis
    )
    score_components = score_components_single_function(analysis=analysis)
    total_score = round(sum(score_components.values()) / len(score_components))

    return SingleFunctionAnalysisResult(
        analysis=analysis, score_components=score_components, total_score=total_score
    )


def score_components_single_function(
    *, analysis: SingleFunctionAnalysis
) -> dict[str, int]:
    score_components = {}
    for file in analysis.files:
        types_of_subheadings = 0
        if len(file.tutorial_subheadings) > 0:
            types_of_subheadings += 1
        if len(file.howto_subheadings) > 0:
            types_of_subheadings += 1
        if len(file.reference_subheadings) > 0:
            types_of_subheadings += 1
        if len(file.explanation_subheadings) > 0:
            types_of_subheadings += 1

        file_score = 0
        if types_of_subheadings == 1:
            file_score = 100
        elif types_of_subheadings == 2:
            file_score = 80
        elif types_of_subheadings == 3:
            file_score = 30
        elif types_of_subheadings == 4:
            file_score = 10
        score_components[f"{file.file_path} has {types_of_subheadings} {'type' if types_of_subheadings == 1 else 'types'} of subheadings"] = file_score

    return score_components
