from django.views.generic import View
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from app.services import analysis_service


@method_decorator(login_required, name="dispatch")
class AnalysisResultsView(View):
    template_name = "analysis_results.html"

    def get(self, request):
        user = request.user
        is_authenticated = user.is_authenticated
        analysis_results = analysis_service.get_all_analysis()
        return render(
            request,
            self.template_name,
            {
                "is_authenticated": is_authenticated,
                "user": user,
                "analysis_results": analysis_results,
            },
        ) 