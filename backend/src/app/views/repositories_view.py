from django.views.generic import View
from django.shortcuts import render
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required
from app.services import repository_service


@method_decorator(login_required, name="dispatch")
class RepositoriesView(View):
    template_name = "repositories.html"

    def get(self, request):
        user = request.user
        is_authenticated = user.is_authenticated
        repositories = repository_service.get_all_repositories_for_owner(user.username)
        return render(
            request,
            self.template_name,
            {
                "is_authenticated": is_authenticated,
                "user": user,
                "repositories": repositories,
            },
        )
