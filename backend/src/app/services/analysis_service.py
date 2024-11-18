import asyncio
from app import custom_errors
from app.models import Analysis, Repo
from app.services import (
    local_repo_service,
    remote_repo_service,
)
from app.services.analysis import (
    analyze_coherent_sitemap,
    analyze_single_function,
    analyze_style,
)
from app.services import repo_map_service


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

        coherent_sitemap_task = asyncio.create_task(
            analyze_coherent_sitemap(repo_map=repo_map)
        )
        single_function_task = asyncio.create_task(
            analyze_single_function(repo_map=repo_map)
        )
        # style_task = asyncio.create_task(
        #     analyze_style(local_repo_path=local_repo_path, repo_map=repo_map)
        # )

        single_function_result = await single_function_task
        coherent_sitemap_result = await coherent_sitemap_task
        # style_result = await style_task

        analysis_result_dict = {}
        analysis_result_dict["single_function"] = single_function_result.model_dump()
        analysis_result_dict["coherent_sitemap"] = coherent_sitemap_result.model_dump()
        # analysis_result_dict["style"] = style_result.model_dump()

        analysis = Analysis(
            repo=repo,
            result=analysis_result_dict,
        )
        await analysis.asave()

        return analysis_result_dict
