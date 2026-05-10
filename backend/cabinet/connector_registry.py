from pathlib import Path
from typing import Any, Dict, List

import yaml


class ConnectorRegistry:
    """Registry for ASTI connector hands behind AI Cabinet governance.

    This does not execute external actions. It records which connector manifests
    exist, whether they are signed/approved, and what execution level is allowed.
    """

    def __init__(self, plugin_root: Path):
        self.plugin_root = plugin_root

    def connectors(self) -> List[Dict[str, Any]]:
        records = []
        if not self.plugin_root.exists():
            return records
        for path in sorted(self.plugin_root.glob("*/manifest.yaml")):
            manifest = self._load(path)
            records.append(self._connector_record(path, manifest))
        return records

    def capabilities(self) -> Dict[str, Any]:
        records = self.connectors()
        return {
            "philosophy": "control_before_autonomy",
            "real_world_execution": "disabled_until_signed_connector_and_approval",
            "connectors_total": len(records),
            "signed_connectors": [item["name"] for item in records if item["signed"]],
            "draft_only_connectors": [item["name"] for item in records if item["execution_mode"] != "external_execution_enabled"],
            "connectors": records,
        }

    def get(self, name: str) -> Dict[str, Any]:
        for connector in self.connectors():
            if connector["name"] == name:
                return connector
        return {}

    def dry_run(self, name: str, action: str, data_class: str, access_level: int) -> Dict[str, Any]:
        connector = self.get(name)
        if not connector:
            return {"allowed": False, "reason": "connector_not_found"}
        if data_class not in connector["allowed_data_classes"]:
            return {"allowed": False, "reason": "data_class_not_allowed", "connector": connector}
        if access_level > connector["max_autonomous_level"]:
            return {
                "allowed": False,
                "reason": "approval_required_for_requested_access_level",
                "connector": connector,
            }
        if action in connector["requires_approval"]:
            return {"allowed": False, "reason": "action_requires_approval", "connector": connector}
        if not connector["signed"]:
            return {"allowed": False, "reason": "connector_not_signed", "connector": connector}
        return {"allowed": True, "reason": "signed_connector_policy_allows_action", "connector": connector}

    def _load(self, path: Path) -> Dict[str, Any]:
        with path.open("r", encoding="utf-8") as handle:
            return yaml.safe_load(handle) or {}

    def _connector_record(self, path: Path, manifest: Dict[str, Any]) -> Dict[str, Any]:
        signed_connector = manifest.get("signed_connector", {})
        signature = signed_connector.get("signature", "")
        signer = signed_connector.get("signer", "")
        signed = bool(signature and signer and signed_connector.get("status") == "signed")
        sandbox = manifest.get("sandbox", {})
        execution_mode = "external_execution_enabled" if signed else sandbox.get("execution", "no_direct_execution")
        return {
            "name": manifest.get("name", path.parent.name),
            "path": str(path),
            "risk_level": manifest.get("risk_level", "medium"),
            "permissions": manifest.get("permissions", []),
            "forbidden": manifest.get("forbidden", []),
            "requires_approval": manifest.get("requires_approval", []),
            "allowed_data_classes": manifest.get("allowed_data_classes", ["public"]),
            "max_autonomous_level": int(manifest.get("max_autonomous_level", 0)),
            "signed": signed,
            "signer": signer,
            "signature_status": signed_connector.get("status", "unsigned"),
            "execution_mode": execution_mode,
            "network": sandbox.get("network", "deny_until_connector_approved"),
            "filesystem": sandbox.get("filesystem", "deny"),
            "governance_gate": "policy_plus_approval_plus_audit",
        }
