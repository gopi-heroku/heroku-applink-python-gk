import os
from functools import lru_cache

@lru_cache(maxsize=None)
def resolve_addon_config_by_attachment_or_color(attachment_or_color: str) -> dict[str, str]:
    """
    First try:
      HEROKU_APPLINK_{ATTACHMENT_OR_COLOR}_API_URL / _TOKEN
    Then fallback to:
      {ATTACHMENT_OR_COLOR}_API_URL / _TOKEN
    """
    addon_prefix = os.getenv("HEROKU_APPLINK_ADDON_NAME", "HEROKU_APPLINK")
    key = attachment_or_color.upper()

    # First try with HEROKU_APPLINK prefix
    api_url = os.getenv(f"{addon_prefix}_{key}_API_URL")
    token = os.getenv(f"{addon_prefix}_{key}_TOKEN")

    # If not found, try direct lookup
    if not api_url or not token:
        api_url = os.getenv(f"{key}_API_URL")
        token = os.getenv(f"{key}_TOKEN")

    if not api_url or not token:
        raise EnvironmentError(
            f"Heroku Applink config not found for '{attachment_or_color}'"
        )

    return {"api_url": api_url, "token": token}

@lru_cache(maxsize=None)
def resolve_addon_config_by_url(url: str) -> dict[str, str]:
    """
    Match an env var ending in _API_URL to the given URL, then
    pull the corresponding _TOKEN.
    """
    for var, val in os.environ.items():
        if var.endswith("_API_URL") and val.lower() == url.lower():
            prefix = var[: -len("_API_URL")]
            token = os.getenv(f"{prefix}_TOKEN")
            if not token:
                raise EnvironmentError(f"Heroku Applink token not found for API URL: {url}")
            return {"api_url": val, "token": token}

    raise EnvironmentError(f"Heroku Applink config not found for API URL: {url}")
