import asyncio
from typing import List
from app import custom_errors
from app.models import Analysis, Repo
from app.services import (
    ai_service,
    local_repo_service,
    remote_repo_service,
)
from app.services.analysis import (
    analyze_coherent_sitemap,
    analyze_single_function,
    analyze_vale,
)
from app.services import repo_map_service
from app.services.analysis.vale_analysis_service import analyze_patch_vale
from pydantic import BaseModel


def get_latest_analysis_by_github_full_name(
    *, sanitized_github_full_name: str
) -> Analysis:
    return (
        Analysis.objects.filter(repo__nfkc_github_full_name=sanitized_github_full_name)
        .order_by("-created_at")
        .first()
    )


async def analyze_remote_repo(*, sanitized_github_full_name: str) -> dict:
    repo = await remote_repo_service.get_repo_by_github_full_name(
        sanitized_github_full_name=sanitized_github_full_name
    )
    return await analyze_repo(repo=repo)


async def analyze_repo(*, repo: Repo) -> dict:
    with local_repo_service.temp_clone_repo(repo=repo) as local_repo_path:
        repo_map = await repo_map_service.create_repo_map(
            repo=repo, local_repo_path=local_repo_path
        )

        tasks = [
            analyze_coherent_sitemap(repo_map=repo_map),
            analyze_single_function(repo_map=repo_map),
            analyze_vale(local_repo_path=local_repo_path, repo_map=repo_map),
        ]

        results = await asyncio.gather(*tasks)

        coherent_sitemap_result, single_function_result, vale_result = results

        analysis_result_dict = {
            "single_function": single_function_result.model_dump(),
            "coherent_sitemap": coherent_sitemap_result.model_dump(),
            "vale": vale_result.model_dump(),
        }

        analysis = Analysis(
            repo=repo,
            result=analysis_result_dict,
        )
        await analysis.asave()

        return analysis_result_dict


class ReviewComment(BaseModel):
    path: str
    body: str
    line: int


class ReviewComments(BaseModel):
    comments: List[ReviewComment]


async def analyze_patch(*, filename: str, patch: str) -> List[ReviewComment]:
    if filename.endswith(".md"):
        result = await ai_service.get_suggestion_json(
            message_list=[
                {
                    "role": "system",
                    "content": f"The following is a patch to markdown file {filename}. Please review the patch and provide a comment on the changes. The comments will be posted as a review on GitHub.",
                },
                {"role": "user", "content": patch},
            ],
            model=ReviewComments,
        )
        return result.comments
    return []
