from pathlib import Path
from typing import Any, Dict, List

import yaml


class PluginSandbox:
    def __init__(self, plugin_root: Path):
        self.plugin_root = plugin_root

    def manifests(self) -> List[Dict[str, Any]]:
        manifests = []
        if not self.plugin_root.exists():
            return manifests
        for path in self.plugin_root.glob("*/manifest.yaml"):
            with path.open("r", encoding="utf-8") as handle:
                manifest = yaml.safe_load(handle) or {}
                manifest["sandbox_status"] = self.validate(manifest)
                manifests.append(manifest)
        return manifests

    def validate(self, manifest: Dict[str, Any]) -> Dict[str, Any]:
        required = ["name", "permissions", "forbidden", "risk_level", "requires_approval"]
        missing = [key for key in required if key not in manifest]
        allowed_data_classes = manifest.get("allowed_data_classes", ["public"])
        return {
            "valid": not missing,
            "missing": missing,
            "isolated": True,
            "network_default": "deny_until_connector_approved",
            "allowed_data_classes": allowed_data_classes,
        }
