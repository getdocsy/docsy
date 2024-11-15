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

        analysis_result_dict = {}
        analysis_result_dict["coherent_sitemap"] = analyze_coherent_sitemap(
            repo_map=repo_map
        ).model_dump()
        analysis_result_dict["single_function"] = analyze_single_function(
            repo_map=repo_map
        ).model_dump()
        # Style analysis checks contents of files, so we need to pass the local repo path
        analysis_result_dict["style"] = analyze_style(
            local_repo_path=local_repo_path, repo_map=repo_map
        ).model_dump()

        analysis = Analysis(
            repo=repo,
            result=analysis_result_dict,
        )
        analysis.save()

        return analysis_result_dict
