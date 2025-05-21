import os
from typing import Dict, Optional, Tuple

class AddonConfig:
    """Configuration for a Heroku AppLink addon."""
    def __init__(self, api_url: str, token: str):
        self.api_url = api_url
        self.token = token

def resolve_addon_config_by_attachment_or_color(attachment_or_color: str) -> AddonConfig:
    """Get stored Salesforce or Data Cloud org user credentials for given developer name or alias.
    
    Args:
        attachment_or_color: Either an attachment name (e.g. "HEROKU_APPLINK"), 
                           color (e.g. "purple" in "HEROKU_APPLINK_PURPLE")
    
    Returns:
        AddonConfig: The addon configuration
        
    Raises:
        ValueError: If the configuration is not found
    """
    addon = os.getenv("HEROKU_APPLINK_ADDON_NAME", "HEROKU_APPLINK")
    
    # Lookup by attachment
    api_url = os.getenv(f"{attachment_or_color.upper()}_API_URL")
    token = os.getenv(f"{attachment_or_color.upper()}_TOKEN")
    
    # If not found, lookup by color using HEROKU_APPLINK prefix for attachment name
    if not api_url or not token:
        api_url = os.getenv(f"{addon}_{attachment_or_color.upper()}_API_URL")
        token = os.getenv(f"{addon}_{attachment_or_color.upper()}_TOKEN")
    
    if not api_url or not token:
        raise ValueError(
            f"Heroku Applink config not found under attachment or color {attachment_or_color}"
        )
    
    return AddonConfig(api_url, token)

def resolve_addon_config_by_url(url: str) -> AddonConfig:
    """Get stored Salesforce or Data Cloud org user credentials for given API URL.
    
    Args:
        url: The API URL to look up
        
    Returns:
        AddonConfig: The addon configuration
        
    Raises:
        ValueError: If the configuration is not found
    """
    # Find the environment variable ending with _API_URL that matches the given URL
    env_vars = dict(os.environ)
    matching_api_url_entry = next(
        ((key, value) for key, value in env_vars.items() 
         if key.endswith("_API_URL") and value.lower() == url.lower()),
        None
    )
    
    if not matching_api_url_entry:
        raise ValueError(f"Heroku Applink config not found for API URL: {url}")
    
    # Extract the prefix from the API_URL environment variable name
    env_var_name = matching_api_url_entry[0]
    prefix = env_var_name[:-len("_API_URL")]  # Remove '_API_URL' suffix
    
    # Look for corresponding token
    token = os.getenv(f"{prefix}_TOKEN")
    if not token:
        raise ValueError(f"Heroku Applink token not found for API URL: {url}")
    
    return AddonConfig(matching_api_url_entry[1], token)
