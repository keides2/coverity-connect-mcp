"""
Configuration module for Coverity Connect MCP Server
"""

import os
from pathlib import Path
from typing import Dict, Optional


class CoverityConfig:
    """Coverity Connect connection configuration"""
    
    def __init__(self):
        # Required: Coverity Connect server details
        self.host = os.getenv("COVERITY_HOST", "your-coverity-server.com")
        self.port = os.getenv("COVERITY_PORT", "443")
        self.ssl = os.getenv("COVERITY_SSL", "True").lower() == "true"
        
        # Required: Authentication
        self.username = os.getenv("COVAUTHUSER", "")
        self.auth_key = os.getenv("COVAUTHKEY", "")
        
        # Optional: Local workspace
        self.base_dir = os.getenv("COVERITY_BASE_DIR", 
                                 os.path.expanduser("~/coverity_workspace"))
        
        # Optional: Proxy configuration for corporate environments
        self.proxies = self._setup_proxies()
        
        # Optional: Logging
        self.log_level = os.getenv("LOG_LEVEL", "INFO")
        
        # Optional: Development mode
        self.dev_mode = os.getenv("DEV_MODE", "false").lower() == "true"
    
    def _setup_proxies(self) -> Dict[str, str]:
        """Setup proxy configuration from environment variables"""
        proxy_host = os.getenv("PROXY_HOST", "")
        proxy_port = os.getenv("PROXY_PORT", "")
        proxy_user = os.getenv("PROXY_USER", "")
        proxy_pass = os.getenv("PROXY_PASS", "")
        
        if proxy_host and proxy_port:
            if proxy_user and proxy_pass:
                proxy_url = f"http://{proxy_user}:{proxy_pass}@{proxy_host}:{proxy_port}/"
            else:
                proxy_url = f"http://{proxy_host}:{proxy_port}/"
            
            return {
                "http": proxy_url,
                "https": proxy_url,
            }
        else:
            return {}
    
    @property
    def server_url(self) -> str:
        """Get the full server URL"""
        protocol = "https" if self.ssl else "http"
        return f"{protocol}://{self.host}:{self.port}"
    
    @property
    def is_configured(self) -> bool:
        """Check if minimum required configuration is present"""
        return bool(self.username and self.auth_key and self.host)
    
    def validate(self) -> Optional[str]:
        """Validate configuration and return error message if invalid"""
        if not self.username:
            return "COVAUTHUSER environment variable is required"
        if not self.auth_key:
            return "COVAUTHKEY environment variable is required"
        if not self.host or self.host == "your-coverity-server.com":
            return "COVERITY_HOST environment variable must be set to your actual server"
        return None
    
    def __repr__(self) -> str:
        return f"CoverityConfig(host={self.host}, port={self.port}, user={self.username})"
