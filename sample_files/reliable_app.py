from __future__ import annotations

import os
from typing import Any

import requests


class ProfileLookupError(RuntimeError):
    """Raised when a profile cannot be fetched safely."""


def fetch_user_profile(user_id: str, timeout_seconds: int = 5) -> dict[str, Any]:
    if not user_id:
        raise ValueError("user_id is required")

    api_base_url = os.environ.get("PROFILE_API_BASE_URL")
    if not api_base_url:
        raise ProfileLookupError("PROFILE_API_BASE_URL is not configured")

    try:
        response = requests.get(
            f"{api_base_url}/users/{user_id}",
            timeout=timeout_seconds,
        )
        response.raise_for_status()
        payload = response.json()
    except requests.Timeout as exc:
        raise ProfileLookupError("Profile API timed out") from exc
    except requests.RequestException as exc:
        raise ProfileLookupError("Profile API request failed") from exc
    except ValueError as exc:
        raise ProfileLookupError("Profile API returned invalid JSON") from exc

    if not isinstance(payload, dict):
        raise ProfileLookupError("Profile API response must be an object")

    return payload

