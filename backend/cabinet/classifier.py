from typing import Dict

from .pii import PiiResult


class DataClassifier:
    confidential_markers = ["password", "secret", "api key", "token", "iban", "passport", "medical", "salary"]
    internal_markers = ["client", "invoice", "contract", "crm", "internal", "roadmap"]
    github_markers = [
        "github",
        "pull request",
        "issue",
        "branch",
        "commit",
        "github workflow",
        "github actions",
        "repository",
        "repo",
        "merge",
        "push",
        "release",
    ]
    github_external_action_markers = [
        "merge",
        "push",
        "release",
        "delete branch",
        "close issue",
        "repository settings",
        "repo settings",
        "secret",
    ]
    computer_markers = [
        "computer",
        "pc",
        "windows",
        "powershell",
        "terminal",
        "shell",
        "process",
        "service",
        "startup",
        "disk",
        "file system",
        "registry",
        "install",
        "uninstall",
    ]
    computer_high_risk_markers = [
        "delete",
        "remove",
        "format",
        "registry",
        "shutdown",
        "reboot",
        "install",
        "uninstall",
        "kill process",
        "stop service",
        "credentials",
        "password",
    ]
    microsoft_markers = [
        "microsoft",
        "outlook",
        "calendar",
        "onedrive",
        "sharepoint",
        "teams",
        "planner",
        "microsoft graph",
        "office",
        "word",
        "excel",
        "powerpoint",
    ]
    microsoft_external_action_markers = [
        "send email",
        "send message",
        "post to teams",
        "create meeting",
        "delete file",
        "share file",
        "change permission",
        "invite",
        "upload",
        "download",
    ]
    jazekker_markers = [
        "jazekker",
        "orientation object",
        "orientation-native",
        "signal intake",
        "noise level",
        "impact horizon",
        "source confidence",
        "public intelligence hub",
        "agentic media runtime",
    ]
    sensitive_public_markers = [
        "political",
        "legal",
        "medical",
        "financial",
        "reputational",
        "privacy",
        "security",
        "investigation",
    ]
    action_markers = [
        "send",
        "delete",
        "execute",
        "transfer",
        "publish",
        "run command",
        "shell",
        "powershell",
        "terminal",
    ]

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

        if (
            data_class in ["personal", "confidential"]
            or mode == "computer_ops"
            or any(marker in lowered for marker in self.action_markers)
            or any(marker in lowered for marker in self.github_external_action_markers)
            or any(marker in lowered for marker in self.computer_high_risk_markers)
            or any(marker in lowered for marker in self.microsoft_external_action_markers)
        ):
            risk_level = "high"
        elif (
            data_class == "internal"
            or mode.endswith("_draft")
            or mode == "github_ops"
            or any(marker in lowered for marker in self.github_markers)
            or any(marker in lowered for marker in self.computer_markers)
            or mode == "microsoft_ops"
            or any(marker in lowered for marker in self.microsoft_markers)
            or mode in ["orientation_draft", "distribution_draft"]
            or any(marker in lowered for marker in self.jazekker_markers)
            or any(marker in lowered for marker in self.sensitive_public_markers)
        ):
            risk_level = "medium"
        else:
            risk_level = "low"

        return {"data_class": data_class, "risk_level": risk_level, "task_type": mode}
