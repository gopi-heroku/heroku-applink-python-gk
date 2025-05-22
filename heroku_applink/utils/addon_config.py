import os
from functools import lru_cache

def _is_color(name: str) -> bool:
    """
    Check if the given name is a color.
    This is a simple check that could be expanded if needed.
    """
    common_colors = {
        'RED', 'GREEN', 'BLUE', 'YELLOW', 'PURPLE', 'ORANGE', 'PINK',
        'BROWN', 'BLACK', 'WHITE', 'GRAY', 'GREY', 'CYAN', 'MAGENTA'
    }
    return name.upper() in common_colors

@lru_cache(maxsize=None)
def resolve_addon_config_by_attachment_or_color(attachment_or_color: str) -> dict[str, str]:
    """
    For colors (like 'purple'):
    First try:
      HEROKU_APPLINK_{COLOR}_API_URL / _TOKEN
    Then fallback to:
      {COLOR}_API_URL / _TOKEN

    For non-color attachments:
    First try:
      {ATTACHMENT}_API_URL / _TOKEN
    Then fallback to:
      HEROKU_APPLINK_{ATTACHMENT}_API_URL / _TOKEN
    """
    addon_prefix = os.getenv("HEROKU_APPLINK_ADDON_NAME", "HEROKU_APPLINK")
    key = attachment_or_color.upper()

    if _is_color(key):
        # For colors, try HEROKU_APPLINK_{COLOR}_* first
        api_url = os.getenv(f"{addon_prefix}_{key}_API_URL")
        token = os.getenv(f"{addon_prefix}_{key}_TOKEN")

        if not api_url or not token:
            # Fallback to {COLOR}_*
            api_url = os.getenv(f"{key}_API_URL")
            token = os.getenv(f"{key}_TOKEN")
    else:
        # For non-colors, try {ATTACHMENT}_* first
        api_url = os.getenv(f"{key}_API_URL")
        token = os.getenv(f"{key}_TOKEN")

        if not api_url or not token:
            # Fallback to HEROKU_APPLINK_{ATTACHMENT}_*
            api_url = os.getenv(f"{addon_prefix}_{key}_API_URL")
            token = os.getenv(f"{addon_prefix}_{key}_TOKEN")

    if not api_url or not token:
        raise EnvironmentError(
            f"Heroku Applink config not found for '{attachment_or_color}'. "
            f"Looked for {key}_API_URL / {key}_TOKEN and "
            f"{addon_prefix}_{key}_API_URL / {addon_prefix}_{key}_TOKEN"
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
                raise EnvironmentError(f"Missing token for API URL: {url}")
            return {"api_url": val, "token": token}

    raise EnvironmentError(f"Heroku Applink config not found for API URL: {url}")
