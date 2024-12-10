from django.shortcuts import render
from django.views.generic import View
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
import json
from datetime import datetime, timedelta

class DashboardView(View):
    template_name = "dashboard.html"

    def get(self, request):
        user = request.user
        
        # TODO: Replace with actual database queries
        # This is sample data - implement actual data retrieval
        sample_dates = [
            (datetime.now() - timedelta(days=x)).strftime('%Y-%m-%d')
            for x in range(10, -1, -1)
        ]
        
        # Sample scores - replace with actual data
        structure_scores = [75, 78, 80, 79, 82, 85, 84, 86, 88, 87, 90]
        sitemap_scores = [65, 68, 70, 72, 75, 74, 76, 78, 80, 82, 85]
        writing_scores = [80, 82, 81, 83, 85, 84, 86, 88, 89, 90, 92]

        context = {
            "user": user,
            "is_authenticated": user.is_authenticated,
            "dates": json.dumps(sample_dates),
            "structure_scores": json.dumps(structure_scores),
            "sitemap_scores": json.dumps(sitemap_scores),
            "writing_scores": json.dumps(writing_scores),
        }
        
        return render(request, self.template_name, context)
