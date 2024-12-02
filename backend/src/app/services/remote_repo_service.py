import unicodedata

from app import custom_errors
from app.models import Repo
from github import Github, GithubException


async def get_public_repo_by_github_full_name(
    *, sanitized_github_full_name: str
) -> Repo:
    nfkc_github_full_name = unicodedata.normalize("NFKC", sanitized_github_full_name)

    g = Github()  # Uses unauthenticated API
    try:
        github_repo = g.get_repo(full_name_or_id=nfkc_github_full_name)
        nfkc_clone_url = unicodedata.normalize("NFKC", github_repo.clone_url)

        repo, _ = await Repo.objects.aget_or_create(
            nfkc_github_full_name=nfkc_github_full_name,
            nfkc_clone_url=nfkc_clone_url,
            is_public=True,
        )
        return repo
    except GithubException as e:
        if e.status == 404:
            raise custom_errors.PublicGithubRepoNotFoundError(
                f"Public GitHub repository not found: {nfkc_github_full_name}"
            )
        raise


# TODO: Ensure repo exists
async def get_repo_by_github_full_name(*, sanitized_github_full_name: str) -> Repo:
    return await Repo.objects.aget(nfkc_github_full_name=sanitized_github_full_name)
