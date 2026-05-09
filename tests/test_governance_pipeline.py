from cabinet.classifier import DataClassifier
from cabinet.output_guard import OutputGuard
from cabinet.pii import PiiDetector
from cabinet.plugin_sandbox import PluginSandbox
from cabinet.policy import PolicyEngine
from cabinet.router import ModelRouter


def test_pii_detector_masks_email_phone_and_secret():
    detector = PiiDetector()
    result = detector.detect_and_mask("Email anna@example.com, phone +31 612345678, token=abc123456789.")

    assert "[MASKED_EMAIL]" in result.masked_text
    assert "[MASKED_PHONE]" in result.masked_text
    assert "[MASKED_SECRET]" in result.masked_text
    assert result.has_pii is True


def test_personal_data_policy_forces_local_only():
    detector = PiiDetector()
    pii = detector.detect_and_mask("Contact anna@example.com")
    classification = DataClassifier().classify("Contact anna@example.com", "email_draft", pii)
    policy = PolicyEngine(
        {
            "rules": {
                "personal": {
                    "name": "personal_data_firewall",
                    "mask": True,
                    "allow_cloud": False,
                    "require_approval": True,
                    "local_only": True,
                }
            }
        }
    ).evaluate(classification, pii.has_pii, 3, False)

    route = ModelRouter({"routes": []}).route("auto", "email_draft", classification["risk_level"], 0.0, policy)

    assert policy.mask is True
    assert policy.allow_cloud is False
    assert policy.require_approval is True
    assert route.provider == "local"


def test_output_guard_blocks_reconstructed_pii():
    detector = PiiDetector()
    input_pii = detector.detect_and_mask("Email anna@example.com")
    scan = OutputGuard(detector).scan("Draft back to anna@example.com", input_pii)

    assert scan["passed"] is False
    assert "pii_or_secret_leakage" in scan["policy_violations"]


def test_github_ops_is_at_least_medium_risk():
    detector = PiiDetector()
    pii = detector.detect_and_mask("Create pull request plan for repository")
    classification = DataClassifier().classify("Create pull request plan for repository", "github_ops", pii)

    assert classification["risk_level"] in {"medium", "high"}


def test_plugin_sandbox_reads_root_manifests(repo_root):
    manifests = PluginSandbox(repo_root / "plugins").manifests()

    assert manifests
    assert all("sandbox_status" in manifest for manifest in manifests)
