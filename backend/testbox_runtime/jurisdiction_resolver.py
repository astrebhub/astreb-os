from __future__ import annotations

from .models import LegalSource, OrientationClassification


NETHERLANDS_MARKERS = (
    "netherlands", "nederland", "amsterdam", "ind", "uwv", "gemeente",
    "belasting", "нидерланд", "голланд", "fiets", "fietser", "wegenverkeerswet",
)

NL_SOURCE_ROUTED_DOMAINS = {
    "business_formation",
    "battery_manufacturing",
    "social_housing",
    "employment_contract",
    "zzp_intermediary_contract",
    "consulting_services",
}


def detect_jurisdiction(text: str) -> str:
    value = text.casefold()
    if any(marker in value for marker in NETHERLANDS_MARKERS):
        return "Netherlands"
    return "unknown"


def infer_jurisdiction(
    detected: str,
    classification: OrientationClassification,
    sources: list[LegalSource],
) -> tuple[str, str]:
    if detected != "unknown":
        return detected, "explicit_user_context"
    candidates = set(classification.domain_candidates)
    if candidates.intersection(NL_SOURCE_ROUTED_DOMAINS) and sources:
        return "Netherlands (candidate)", "nl_eu_official_source_registry"
    return detected, "not_identified"
