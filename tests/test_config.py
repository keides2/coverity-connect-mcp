"""
Tests for Coverity MCP Server configuration
"""

import os
import pytest
from unittest.mock import patch

from coverity_mcp_server.config import CoverityConfig


class TestCoverityConfig:
    """Test cases for CoverityConfig class"""
    
    def test_default_config(self):
        """Test default configuration values"""
        config = CoverityConfig()
        
        assert config.host == "your-coverity-server.com"
        assert config.port == "443"
        assert config.ssl == True
        assert config.proxies == {}
    
    @patch.dict(os.environ, {
        'COVERITY_HOST': 'test-server.com',
        'COVERITY_PORT': '8080',
        'COVERITY_SSL': 'false',
        'COVAUTHUSER': 'testuser',
        'COVAUTHKEY': 'testkey'
    })
    def test_environment_config(self):
        """Test configuration from environment variables"""
        config = CoverityConfig()
        
        assert config.host == "test-server.com"
        assert config.port == "8080"
        assert config.ssl == False
        assert config.username == "testuser"
        assert config.auth_key == "testkey"
    
    @patch.dict(os.environ, {
        'PROXY_HOST': 'proxy.example.com',
        'PROXY_PORT': '3128',
        'PROXY_USER': 'proxyuser',
        'PROXY_PASS': 'proxypass'
    })
    def test_proxy_config(self):
        """Test proxy configuration"""
        config = CoverityConfig()
        
        expected_proxy = "http://proxyuser:proxypass@proxy.example.com:3128/"
        assert config.proxies['http'] == expected_proxy
        assert config.proxies['https'] == expected_proxy
    
    @patch.dict(os.environ, {
        'COVAUTHUSER': 'testuser',
        'COVAUTHKEY': 'testkey',
        'COVERITY_HOST': 'server.com'
    })
    def test_is_configured_true(self):
        """Test configuration validation - valid config"""
        config = CoverityConfig()
        assert config.is_configured == True
        assert config.validate() is None
    
    def test_is_configured_false(self):
        """Test configuration validation - invalid config"""
        config = CoverityConfig()
        assert config.is_configured == False
        assert config.validate() is not None
    
    def test_server_url_https(self):
        """Test server URL generation with HTTPS"""
        config = CoverityConfig()
        config.host = "server.com"
        config.port = "443"
        config.ssl = True
        
        assert config.server_url == "https://server.com:443"
    
    def test_server_url_http(self):
        """Test server URL generation with HTTP"""
        config = CoverityConfig()
        config.host = "server.com"
        config.port = "8080"
        config.ssl = False
        
        assert config.server_url == "http://server.com:8080"
