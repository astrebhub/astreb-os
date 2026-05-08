from typing import Any, Dict

from .pii import PiiDetector, PiiResult


class OutputScanner:
    def __init__(self, pii_detector: PiiDetector):
        self.pii_detector = pii_detector

    def scan(self, output: str, input_pii: PiiResult) -> Dict[str, Any]:
        output_pii = self.pii_detector.contains_raw_pii(output)
        leaks = {}
        for kind, values in input_pii.findings.items():
            leaked_values = [value for value in values if value and value in output]
            if leaked_values:
                leaks[kind] = len(leaked_values)
        return {
            "raw_pii_detected": output_pii,
            "masked_input_leakage": leaks,
            "passed": not any(output_pii.values()) and not leaks,
        }
