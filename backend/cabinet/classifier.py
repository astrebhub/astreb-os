from typing import Dict

from .pii import PiiResult


class DataClassifier:
    confidential_markers = ["password", "secret", "api key", "token", "iban", "passport", "medical", "salary"]
    internal_markers = ["client", "invoice", "contract", "crm", "internal", "roadmap"]
    github_markers = ["github", "pull request", "issue", "branch", "commit", "github workflow", "github actions", "repository", "repo", "merge", "push", "release"]
    github_external_action_markers = ["merge", "push", "release", "delete branch", "close issue", "repository settings", "repo settings", "secret"]
    action_markers = ["send", "delete", "execute", "transfer", "publish", "отправь", "удали", "оплати"]

    def classify(self, text: str, mode: str, pii: PiiResult) -> Dict[str, str]:
        lowered = text.lower()
        if pii.has_pii:
            data_class = "personal"
        elif any(marker in lowered for marker in self.confidential_markers):
            data_class = "confidential"
        elif any(marker in lowered for marker in self.internal_markers):
            data_class = "internal"
        else:
            data_class = "public"

        if data_class in ["personal", "confidential"] or any(marker in lowered for marker in self.action_markers) or any(marker in lowered for marker in self.github_external_action_markers):
            risk_level = "high"
        elif data_class == "internal" or mode.endswith("_draft") or mode == "github_ops" or any(marker in lowered for marker in self.github_markers):
            risk_level = "medium"
        else:
            risk_level = "low"

        return {"data_class": data_class, "risk_level": risk_level, "task_type": mode}
