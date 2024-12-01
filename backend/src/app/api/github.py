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
    if payload.action not in ["opened", "synchronize"]:
        return {"message": "Event ignored"}

    # Initialize GitHub client
    # gh_auth = GitHubAppAuth()
    # gh_client = gh_auth.get_installation_client(payload.installation["id"])

    # Analyze PR changes
    # analysis_results = analyze_pr_changes(gh_client, payload.pull_request)

    # Post results as PR comment
    # repo = gh_client.get_repo(payload.repository["full_name"])
    # pr_number = payload.pull_request["number"]
    # repo.get_issue(pr_number).create_comment(analysis_results)

    return {"message": "Processed successfully"} 