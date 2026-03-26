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
        raise APIError(
            f"connection refused ({base_url.replace('http://', '').replace('https://', '').rstrip('/')}). Check that the services are running."
        ) from e
    except httpx.HTTPStatusError as e:
        raise APIError(
            f"HTTP {e.response.status_code} {e.response.reason_phrase}. The backend service may be down."
        ) from e
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
        raise APIError(
            f"connection refused ({base_url.replace('http://', '').replace('https://', '').rstrip('/')}). Check that the services are running."
        ) from e
    except httpx.HTTPStatusError as e:
        raise APIError(
            f"HTTP {e.response.status_code} {e.response.reason_phrase}. The backend service may be down."
        ) from e
    except httpx.HTTPError as e:
        raise APIError(f"HTTP error: {str(e)}") from e
    finally:
        client.close()


def get_learners() -> list[dict]:
    """Fetch all enrolled learners and their groups.

    Returns:
        List of learner dictionaries.

    Raises:
        APIError: If the API call fails.
    """
    client, base_url = _get_client()
    try:
        response = client.get("/learners/")
        response.raise_for_status()
        return response.json()
    except httpx.ConnectError as e:
        raise APIError(
            f"connection refused ({base_url.replace('http://', '').replace('https://', '').rstrip('/')}). Check that the services are running."
        ) from e
    except httpx.HTTPStatusError as e:
        raise APIError(
            f"HTTP {e.response.status_code} {e.response.reason_phrase}. The backend service may be down."
        ) from e
    except httpx.HTTPError as e:
        raise APIError(f"HTTP error: {str(e)}") from e
    finally:
        client.close()


def get_scores(lab: str) -> list[dict]:
    """Fetch score distribution (4 buckets) for a specific lab.

    Args:
        lab: The lab identifier (e.g., "lab-04").

    Returns:
        List of score distribution dictionaries.

    Raises:
        APIError: If the API call fails.
    """
    client, base_url = _get_client()
    try:
        response = client.get("/analytics/scores", params={"lab": lab})
        response.raise_for_status()
        return response.json()
    except httpx.ConnectError as e:
        raise APIError(
            f"connection refused ({base_url.replace('http://', '').replace('https://', '').rstrip('/')}). Check that the services are running."
        ) from e
    except httpx.HTTPStatusError as e:
        raise APIError(
            f"HTTP {e.response.status_code} {e.response.reason_phrase}. The backend service may be down."
        ) from e
    except httpx.HTTPError as e:
        raise APIError(f"HTTP error: {str(e)}") from e
    finally:
        client.close()


def get_timeline(lab: str) -> list[dict]:
    """Fetch submission timeline data (submissions per day) for a lab.

    Args:
        lab: The lab identifier (e.g., "lab-04").

    Returns:
        List of timeline dictionaries with dates and submission counts.

    Raises:
        APIError: If the API call fails.
    """
    client, base_url = _get_client()
    try:
        response = client.get("/analytics/timeline", params={"lab": lab})
        response.raise_for_status()
        return response.json()
    except httpx.ConnectError as e:
        raise APIError(
            f"connection refused ({base_url.replace('http://', '').replace('https://', '').rstrip('/')}). Check that the services are running."
        ) from e
    except httpx.HTTPStatusError as e:
        raise APIError(
            f"HTTP {e.response.status_code} {e.response.reason_phrase}. The backend service may be down."
        ) from e
    except httpx.HTTPError as e:
        raise APIError(f"HTTP error: {str(e)}") from e
    finally:
        client.close()


def get_groups(lab: str) -> list[dict]:
    """Fetch per-group scores and student counts for a lab.

    Args:
        lab: The lab identifier (e.g., "lab-04").

    Returns:
        List of group dictionaries with scores and student counts.

    Raises:
        APIError: If the API call fails.
    """
    client, base_url = _get_client()
    try:
        response = client.get("/analytics/groups", params={"lab": lab})
        response.raise_for_status()
        return response.json()
    except httpx.ConnectError as e:
        raise APIError(
            f"connection refused ({base_url.replace('http://', '').replace('https://', '').rstrip('/')}). Check that the services are running."
        ) from e
    except httpx.HTTPStatusError as e:
        raise APIError(
            f"HTTP {e.response.status_code} {e.response.reason_phrase}. The backend service may be down."
        ) from e
    except httpx.HTTPError as e:
        raise APIError(f"HTTP error: {str(e)}") from e
    finally:
        client.close()


def get_top_learners(lab: str, limit: int = 10) -> list[dict]:
    """Fetch top N learners by score for a specific lab.

    Args:
        lab: The lab identifier (e.g., "lab-04").
        limit: Number of top learners to return (default 10).

    Returns:
        List of top learner dictionaries with names and scores.

    Raises:
        APIError: If the API call fails.
    """
    client, base_url = _get_client()
    try:
        response = client.get("/analytics/top-learners", params={"lab": lab, "limit": limit})
        response.raise_for_status()
        return response.json()
    except httpx.ConnectError as e:
        raise APIError(
            f"connection refused ({base_url.replace('http://', '').replace('https://', '').rstrip('/')}). Check that the services are running."
        ) from e
    except httpx.HTTPStatusError as e:
        raise APIError(
            f"HTTP {e.response.status_code} {e.response.reason_phrase}. The backend service may be down."
        ) from e
    except httpx.HTTPError as e:
        raise APIError(f"HTTP error: {str(e)}") from e
    finally:
        client.close()


def get_completion_rate(lab: str) -> dict:
    """Fetch the completion rate percentage for a specific lab.

    Args:
        lab: The lab identifier (e.g., "lab-04").

    Returns:
        Dictionary with completion rate percentage.

    Raises:
        APIError: If the API call fails.
    """
    client, base_url = _get_client()
    try:
        response = client.get("/analytics/completion-rate", params={"lab": lab})
        response.raise_for_status()
        return response.json()
    except httpx.ConnectError as e:
        raise APIError(
            f"connection refused ({base_url.replace('http://', '').replace('https://', '').rstrip('/')}). Check that the services are running."
        ) from e
    except httpx.HTTPStatusError as e:
        raise APIError(
            f"HTTP {e.response.status_code} {e.response.reason_phrase}. The backend service may be down."
        ) from e
    except httpx.HTTPError as e:
        raise APIError(f"HTTP error: {str(e)}") from e
    finally:
        client.close()


def trigger_sync() -> dict:
    """Trigger a data sync from the autochecker.

    Returns:
        Dictionary with sync result.

    Raises:
        APIError: If the API call fails.
    """
    client, base_url = _get_client()
    try:
        response = client.post("/pipeline/sync")
        response.raise_for_status()
        return response.json()
    except httpx.ConnectError as e:
        raise APIError(
            f"connection refused ({base_url.replace('http://', '').replace('https://', '').rstrip('/')}). Check that the services are running."
        ) from e
    except httpx.HTTPStatusError as e:
        raise APIError(
            f"HTTP {e.response.status_code} {e.response.reason_phrase}. The backend service may be down."
        ) from e
    except httpx.HTTPError as e:
        raise APIError(f"HTTP error: {str(e)}") from e
    finally:
        client.close()
