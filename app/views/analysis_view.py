from django.http import HttpResponse

from app import custom_errors, sanitization_utils
from app.services import analysis_service


def index(request):
    missing_params = []
    if not request.GET.get("owner"):
        missing_params.append("owner")

    if not request.GET.get("repo"):
        missing_params.append("repo")

    if missing_params:
        return HttpResponse(f"Missing parameters: {', '.join(missing_params)}", status=400)

    unsafe_github_full_name = request.GET.get("owner") + "/" + request.GET.get("repo")

    sanitized_github_full_name = sanitization_utils.strip_xss(
        unsafe_github_full_name=unsafe_github_full_name
    )

    try:
        analysis_result = analysis_service.analyze_remote_repo(
            sanitized_github_full_name=sanitized_github_full_name
        )
    except custom_errors.PublicGithubRepoNotFoundError as e:
        return HttpResponse(e, status=404)

    return HttpResponse(analysis_result)