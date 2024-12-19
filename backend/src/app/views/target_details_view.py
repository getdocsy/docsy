from django.views.generic import View
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.urls import reverse
from app.models import Target
from app.services import target_service


@method_decorator(login_required, name="dispatch")
class TargetDetailsView(View):
    template_name = "target_details.html"

    def get(self, request, target_id):
        target = target_service.get_target_by_id(target_id)
        return render(
            request,
            self.template_name,
            {
                "target": target,
                "is_authenticated": request.user.is_authenticated,
                "user": request.user,
            },
        )

    def post(self, request, target_id):
        target = target_service.get_target_by_id(target_id)
        target_service.delete_target(target)
        return redirect(reverse('targets'))