from app.models import Repo


def get_all_repositories_for_owner(owner: str) -> list[Repo]:
    return list(Repo.objects.filter(nfkc_github_full_name="getdocsy/docs"))
