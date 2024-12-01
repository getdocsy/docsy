

from app.services.github_auth_service import get_github_client


def comment_on_pull_request(*, app_installation_id: int, repo_name: str, pull_request_number: int, comment: str) -> None:
    github_client = get_github_client(app_installation_id=app_installation_id)
    repo = github_client.get_repo(repo_name)
    pr = repo.get_pull(pull_request_number)
    pr.create_issue_comment(comment)
