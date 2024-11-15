from pydantic import BaseModel

from app.models import RepoMap


class FirstPageAnalysis(BaseModel):
    pass


def analyze_first_page(*, repo_map: RepoMap) -> FirstPageAnalysis:
    pass


def score_components_first_page(*, analysis: FirstPageAnalysis) -> dict[str, int]:
    # Number of words describing the problem
    # Number of words describing the solution
    # Number of images / videos
    return {
        "number_of_words_describing_the_problem": 0,
        "number_of_words_describing_the_solution": 0,
        "number_of_images_or_videos": 0,
    }
