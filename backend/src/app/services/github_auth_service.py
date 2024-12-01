from github import Auth, Github, GithubIntegration
from django.conf import settings

def get_github_client(*, app_installation_id: int) -> Github:
    appAuth = Auth.AppAuth(
        settings.GITHUB_APP_ID, settings.GITHUB_APP_PRIVATE_KEY.replace("\\n", "\n")
    )
    gi = GithubIntegration(auth=appAuth)
    return gi.get_github_for_installation(app_installation_id)
