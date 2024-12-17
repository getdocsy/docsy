from app.models import Template


def create_template(*, name: str, description: str, structure: dict) -> Template:
    return Template.objects.create(
        name=name,
        description=description,
        structure=structure
    )


def get_all_templates() -> list[Template]:
    return list(Template.objects.all().order_by('-created_at'))


def get_template_by_id(template_id: int) -> Template:
    return Template.objects.get(id=template_id)


def delete_template(*, template_id: int) -> None:
    template = get_template_by_id(template_id)
    template.delete() 