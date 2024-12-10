from django.shortcuts import render
from django.views.generic import View
from django.contrib.auth.decorators import login_required


class DashboardView(View):
    template_name = "dashboard.html"

    def get(self, request):
        user = request.user
        is_authenticated = user.is_authenticated
        return render(
            request,
            self.template_name,
            {"user": user, "is_authenticated": is_authenticated},
        )
