from textwrap import dedent
from pydantic import BaseModel

from app.models import RepoMap
from app.services import ai_service
from app.services.repo_map_service import get_relative_file_path_to_headings


class FileClassification(BaseModel):
    path: str
    classification: str
    confidence_score: int


class CoherentSitemapAnalysis(BaseModel):
    files: list[FileClassification]


class CoherentSitemapAnalysisResult(BaseModel):
    analysis: CoherentSitemapAnalysis
    score_components: dict[str, int]
    total_score: int


def analyze_coherent_sitemap(*, repo_map: RepoMap) -> CoherentSitemapAnalysisResult:
    relative_file_path_to_headings = get_relative_file_path_to_headings(
        repo_map=repo_map
    )

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

    analysis = ai_service.get_suggestion_json(
        message_list=message_list, model=CoherentSitemapAnalysis
    )
    score_components = score_components_coherent_sitemap(analysis=analysis)
    total_score = round(sum(score_components.values()) / len(score_components))

    return CoherentSitemapAnalysisResult(
        analysis=analysis,
        score_components=score_components,
        total_score=total_score,
    )


def score_components_coherent_sitemap(*, analysis: CoherentSitemapAnalysis) -> dict[str, int]:
    # average the confidence scores of the classifications
    confidence_scores = [file.confidence_score for file in analysis.files]
    average_confidence_score = round(sum(confidence_scores) / len(confidence_scores))
    return {
        "coherent_sitemap": int(average_confidence_score),
    }
