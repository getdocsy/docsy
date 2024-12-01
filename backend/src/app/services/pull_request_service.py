from app.services.analysis_service import analyze_patch
from app.services.github_auth_service import get_github_client


def comment_on_pull_request(
    *, app_installation_id: int, repo_name: str, pull_request_number: int, comment: str
) -> None:
    github_client = get_github_client(app_installation_id=app_installation_id)
    repo = github_client.get_repo(repo_name)
    pr = repo.get_pull(pull_request_number)
    pr.create_issue_comment(comment)


def analyze_pull_request(
    *, app_installation_id: int, repo_name: str, pull_request_number: int
) -> None:
    github_client = get_github_client(app_installation_id=app_installation_id)
    repo = github_client.get_repo(repo_name)
    pr = repo.get_pull(pull_request_number)

    files = pr.get_files()
    analysis_result_dicts = {}
    for file in files:
        analysis_result_dict = analyze_patch(filename=file.filename, patch=file.patch)
        analysis_result_dicts[file.filename] = analysis_result_dict
        pr.create_comment(
            body=f"## {file.filename}\n{analysis_result_dict}",
            commit=pr.get_commits()[0],
            path=file.filename,
            position=file.patch.count("\n"),
        )

    return analysis_result_dicts
