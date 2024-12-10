from app.models import Target


def create_target(*, description: str) -> Target:
    return Target.objects.create(description=description)


def get_all_targets() -> list[Target]:
    return list(Target.objects.all().order_by('-created_at'))



