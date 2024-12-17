from django.views.generic import View
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_protect
from app.services import template_service


@method_decorator(login_required, name="dispatch")
@method_decorator(csrf_protect, name="dispatch")
class TemplateDetailsView(View):
    template_name = "template_details.html"

    def get(self, request, template_id):
        template = template_service.get_template_by_id(template_id)
        return render(
            request,
            self.template_name,
            {
                "is_authenticated": request.user.is_authenticated,
                "user": request.user,
                "template": template,
            },
        )
    
    def post(self, request, template_id):
        if request.POST.get("action") == "delete":
            template_service.delete_template(template_id=template_id)
            return redirect("templates")
        return redirect("template_detail", template_id=template_id) 