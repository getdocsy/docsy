from django.views.generic import View
from django.shortcuts import render


class IntegrationsView(View):
    template_name = "integrations.html"

    def get(self, request):
        user = request.user
        is_authenticated = user.is_authenticated
        return render(
            request,
            self.template_name,
            {"user": user, "is_authenticated": is_authenticated},
        )
