from app.models import Repo, Target


def create_target(*, description: str) -> Target:
    return Target.objects.create(description=description)
