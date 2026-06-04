from __future__ import annotations

import logging
import os
import secrets

from fastapi import HTTPException


LOGGER = logging.getLogger(__name__)
TRUTHY_VALUES = {"1", "true", "yes", "on"}


def validate_privileged_runtime_configuration() -> None:
    environment = os.getenv("AI_CABINET_ENV", "dev").casefold()
    if environment not in {"dev", "prod"}:
        raise RuntimeError("invalid_ai_cabinet_env")
    if environment == "prod" and not os.getenv("ADMIN_API_TOKEN"):
        raise RuntimeError("admin_api_token_required_in_prod")
    if (
        environment == "prod"
        and os.getenv("ASTI_EXTERNAL_EXECUTION_ENABLED", "").casefold() in TRUTHY_VALUES
    ):
        raise RuntimeError("external_execution_forbidden_in_production_preview")
    if not os.getenv("ADMIN_API_TOKEN"):
        LOGGER.warning(
            "Privileged runtime endpoints are disabled until ADMIN_API_TOKEN is configured."
        )


def require_admin_token(token: str | None) -> None:
    configured_token = os.getenv("ADMIN_API_TOKEN")
    if not configured_token:
        LOGGER.warning("privileged_auth_denied reason=admin_api_token_not_configured")
        raise HTTPException(status_code=503, detail="admin_api_token_not_configured")
    if token is None or not secrets.compare_digest(token, configured_token):
        LOGGER.warning("privileged_auth_denied reason=invalid_admin_token")
        raise HTTPException(status_code=401, detail="invalid_admin_token")
