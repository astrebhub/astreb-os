import re
from dataclasses import dataclass
from typing import Dict, List


@dataclass
class PiiResult:
    original_text: str
    masked_text: str
    findings: Dict[str, List[str]]

    @property
    def counts(self) -> Dict[str, int]:
        return {kind: len(values) for kind, values in self.findings.items()}

    @property
    def has_pii(self) -> bool:
        return any(self.findings.values())


class PiiDetector:
    patterns = {
        "EMAIL": re.compile(r"\b[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}\b", re.IGNORECASE),
        "PHONE": re.compile(r"(?<!\w)(?:\+?\d[\d\s().-]{7,}\d)(?!\w)"),
        "IBAN": re.compile(r"\b[A-Z]{2}\d{2}[A-Z0-9]{11,30}\b", re.IGNORECASE),
        "NAME": re.compile(
            r"\b(?:(?:Mr\.|Ms\.|Mrs\.|Dr\.)\s+)?[A-Z][a-z]{1,30}\s+[A-Z][a-z]{1,30}\b"
        ),
        "SECRET": re.compile(
            r"\b(?:sk-[A-Za-z0-9_-]{12,}|api[_-]?key\s*[:=]\s*[A-Za-z0-9_-]{8,}|token\s*[:=]\s*[A-Za-z0-9_.-]{8,})\b",
            re.IGNORECASE,
        ),
    }

    def detect_and_mask(self, text: str) -> PiiResult:
        findings: Dict[str, List[str]] = {kind: [] for kind in self.patterns}
        masked = text
        for kind, pattern in self.patterns.items():
            matches = list(dict.fromkeys(match.group(0) for match in pattern.finditer(masked)))
            findings[kind].extend(matches)
            for value in matches:
                masked = masked.replace(value, f"[MASKED_{kind}]")
        return PiiResult(original_text=text, masked_text=masked, findings=findings)

    def contains_raw_pii(self, text: str) -> Dict[str, int]:
        return self.detect_and_mask(text).counts
