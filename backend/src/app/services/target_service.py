from app.models import Target


def create_target(*, description: str) -> Target:
    return Target.objects.create(description=description)


def get_all_targets() -> list[Target]:
    return list(Target.objects.all().order_by("-created_at"))


def get_target_by_id(target_id: int) -> Target:
    return Target.objects.get(id=target_id)


def delete_target(target: Target) -> None:
    target.delete()
