"""LMS API client.

Makes HTTP calls to the LMS backend with proper authentication.
Returns structured data (dicts/lists) that handlers can format.
"""

import httpx
from config import load_config


class APIError(Exception):
    """Raised when the API call fails."""

    pass


def _get_client() -> tuple[httpx.Client, str]:
    """Create an authenticated HTTP client.

    Returns:
        Tuple of (httpx.Client, base_url)
    """
    config = load_config()
    base_url = config.get("LMS_API_BASE_URL", "http://localhost:42002")
    api_key = config.get("LMS_API_KEY", "")

    client = httpx.Client(
        base_url=base_url,
        headers={"Authorization": f"Bearer {api_key}"},
        timeout=10.0,
    )
    return client, base_url


def get_items() -> list[dict]:
    """Fetch all items (labs and tasks) from the backend.

    Returns:
        List of item dictionaries.

    Raises:
        APIError: If the API call fails.
    """
    client, base_url = _get_client()
    try:
        response = client.get("/items/")
        response.raise_for_status()
        return response.json()
    except httpx.ConnectError as e:
        raise APIError(f"connection refused ({base_url.replace('http://', '').replace('https://', '').rstrip('/')}). Check that the services are running.") from e
    except httpx.HTTPStatusError as e:
        raise APIError(f"HTTP {e.response.status_code} {e.response.reason_phrase}. The backend service may be down.") from e
    except httpx.HTTPError as e:
        raise APIError(f"HTTP error: {str(e)}") from e
    finally:
        client.close()


def get_pass_rates(lab: str) -> list[dict]:
    """Fetch pass rates for a specific lab.

    Args:
        lab: The lab identifier (e.g., "lab-04").

    Returns:
        List of pass rate dictionaries with task names and percentages.

    Raises:
        APIError: If the API call fails.
    """
    client, base_url = _get_client()
    try:
        response = client.get("/analytics/pass-rates", params={"lab": lab})
        response.raise_for_status()
        return response.json()
    except httpx.ConnectError as e:
        raise APIError(f"connection refused ({base_url.replace('http://', '').replace('https://', '').rstrip('/')}). Check that the services are running.") from e
    except httpx.HTTPStatusError as e:
        raise APIError(f"HTTP {e.response.status_code} {e.response.reason_phrase}. The backend service may be down.") from e
    except httpx.HTTPError as e:
        raise APIError(f"HTTP error: {str(e)}") from e
    finally:
        client.close()
