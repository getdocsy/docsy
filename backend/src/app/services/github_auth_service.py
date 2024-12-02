from github import Auth, Github, GithubIntegration
from django.conf import settings

# We use a PAT here. Not ideal, but we want to lookup repos without signing in as any installation and GitHub Apps can't do that.
def get_github_client_for_pat() -> Github:
    token = str(settings.GITHUB_REPO_LOOKUP_PAT)
    return Github(auth=Auth.Token(token))

def get_github_client(*, app_installation_id: int) -> Github:
    appAuth = Auth.AppAuth(
        settings.GITHUB_APP_ID, settings.GITHUB_APP_PRIVATE_KEY.replace("\\n", "\n")
    )
    gi = GithubIntegration(auth=appAuth)
    return gi.get_github_for_installation(app_installation_id)
