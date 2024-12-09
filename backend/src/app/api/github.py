from app.services import pull_request_service, remote_repo_service
from ninja import NinjaAPI, Schema
from django.conf import settings
import hmac
import hashlib
import logging

logger = logging.getLogger(__name__)

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


@github_api.post("/events", auth=GitHubWebhookAuth())
async def github_webhook(request, payload: PRPayload):
    # We only analyze repos that have enabled pull request analysis
    repo = await remote_repo_service.get_repo_by_github_full_name(
        sanitized_github_full_name=payload.repository["full_name"]
    )
    if not repo.enable_pull_request_analysis:
        logger.info(
            f"Event ignored because pull request analysis is disabled for repo: {payload.repository['full_name']}, pr: {payload.pull_request['number']}"
        )
        return {"message": "Event ignored because pull request analysis is disabled"}

    # We only analyze opened PRs
    if payload.action not in ["opened"]:
        logger.info(
            f"Event ignored based on action: {payload.action}; repo: {payload.repository['full_name']}, pr: {payload.pull_request['number']}"
        )
        return {"message": "Event ignored"}

    # Ignore PRs opened by the GitHub app itself
    if payload.pull_request["user"]["type"] == "Bot":
        logger.info(
            f"Event ignored because it was opened by a bot; repo: {payload.repository['full_name']}, pr: {payload.pull_request['number']}"
        )
        return {"message": "Event ignored because it was opened by a bot"}

    # Analyze changes
    summary = await pull_request_service.analyze_pull_request(
        app_installation_id=payload.installation["id"],
        repo_name=payload.repository["full_name"],
        pull_request_number=payload.pull_request["number"],
    )

    # Post summary as PR comment
    await pull_request_service.comment_on_pull_request(
        app_installation_id=payload.installation["id"],
        repo_name=payload.repository["full_name"],
        pull_request_number=payload.pull_request["number"],
        comment=summary,
    )

    return {"message": "Processed successfully"}
