from app.services import pull_request_service
from ninja import NinjaAPI, Schema
from django.conf import settings
import hmac
import hashlib

# Create a separate router for GitHub webhooks
github_api = NinjaAPI(title="GitHub Webhooks", version="1.0.0", urls_namespace="github")


class GitHubWebhookAuth:
    def __call__(self, request):
        signature = request.headers.get("X-Hub-Signature-256")
        if not signature:
            return None

        expected_signature = hmac.new(
            settings.GITHUB_WEBHOOK_SECRET.encode(), request.body, hashlib.sha256
        ).hexdigest()

        if hmac.compare_digest(f"sha256={expected_signature}", signature):
            return True
        return None


# Schema for PR webhook payload
class PRPayload(Schema):
    action: str
    pull_request: dict
    repository: dict
    installation: dict


@github_api.post("/github/events", auth=GitHubWebhookAuth())
def github_webhook(request, payload: PRPayload):
    # if payload.action not in ["opened", "synchronize"]:
    #     return {"message": "Event ignored"}

    # Read changes from PR

    # Analyze changes

    # Post results as PR comment
    pull_request_service.comment_on_pull_request(
        app_installation_id=payload.installation["id"],
        repo_name=payload.repository["full_name"],
        pull_request_number=payload.pull_request["number"],
        comment="Hello",
    )

    return {"message": "Processed successfully"}
