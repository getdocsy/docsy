from app.services.analysis_service import analyze_patch
from app.services.github_auth_service import get_github_client
from django.conf import settings


async def comment_on_pull_request(
    *, app_installation_id: int, repo_name: str, pull_request_number: int, comment: str
) -> None:
    github_client = get_github_client(app_installation_id=app_installation_id)
    repo = github_client.get_repo(repo_name)
    pr = repo.get_pull(pull_request_number)
    pr.create_issue_comment(comment)


async def analyze_pull_request(
    *, app_installation_id: int, repo_name: str, pull_request_number: int
) -> str:
    github_client = get_github_client(app_installation_id=app_installation_id)
    repo = github_client.get_repo(repo_name)
    pr = repo.get_pull(pull_request_number)

    files = pr.get_files()

    # We analyze patches for each file
    for file in files:
        comments = await analyze_patch(filename=file.filename, patch=file.patch)
        if comments:
            api_comments = [
                {
                    "path": comment.path,
                    "body": comment.body,
                    "line": comment.line,
                    "side": "RIGHT",  # Required by GitHub API
                }
                for comment in comments
            ]
            pr.create_review(
                commit=pr.get_commits().reversed[0],  # We only review the final result, not the intermediate commits
                event="COMMENT",
                comments=api_comments,
            )

    # Extract owner and repo name from the full repo name (format: "owner/repo")
    owner, name = repo_name.split("/")
    return f"Overall well done! Check out [the full repo analysis]({settings.BASE_URL}/analysis/result/?owner={owner}&name={name}) for more information."
