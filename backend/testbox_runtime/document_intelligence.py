from __future__ import annotations

from .models import DocumentExtractionInput, DocumentProcessingState


EXTRACTION_FAILURE_MARKERS = (
    "text was not extractable",
    "ocr is not active",
    "could not read document",
    "text extraction is not supported",
    "text could not be found",
)


def assess_document_input(
    document_text: str | None,
    attachment_names: list[str],
    extraction: DocumentExtractionInput | None,
) -> DocumentProcessingState:
    """Normalize document input and state explicitly when OCR is still required."""
    page_text = ""
    if extraction and extraction.pages:
        page_text = "\n\n".join(
            page.text.strip() for page in extraction.pages if page.text.strip()
        )
    supplied_text = (page_text or (extraction.extracted_text if extraction else None) or document_text or "").strip()
    method = extraction.method if extraction else "browser_extraction"
    provenance = [
        {"filename": name, "source": method, "pages_seen": extraction.pages_seen if extraction else None}
        for name in attachment_names
    ]
    if not attachment_names and not supplied_text:
        return DocumentProcessingState(
            extraction_status="no_document",
            method="none",
            limitation_reason="document_not_received",
        )
    explicit_failure = bool(
        extraction and extraction.extraction_status in {"failed", "ocr_required", "unsupported"}
    )
    marker_failure = any(marker in supplied_text.casefold() for marker in EXTRACTION_FAILURE_MARKERS)
    if explicit_failure or marker_failure or (attachment_names and not supplied_text):
        return DocumentProcessingState(
            extraction_status="ocr_required",
            method=method,
            confidence=extraction.confidence if extraction else 0.0,
            pages_seen=extraction.pages_seen if extraction else None,
            provenance=provenance,
            ocr_required=True,
            limitation_reason=(
                extraction.limitation_reason
                if extraction and extraction.limitation_reason
                else "no_readable_document_text"
            ),
        )
    return DocumentProcessingState(
        extracted_text=supplied_text,
        extraction_status="readable_text_received",
        confidence=(extraction.confidence if extraction and extraction.confidence is not None else 0.75),
        pages_seen=extraction.pages_seen if extraction else None,
        method=method,
        provenance=provenance,
    )
