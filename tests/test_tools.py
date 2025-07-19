"""
Tests for Coverity MCP Server tools
"""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch

from coverity_mcp_server.tools import (
    get_coverity_projects,
    get_project_streams,
    set_config
)
from coverity_mcp_server.config import CoverityConfig


@pytest.fixture
def mock_config():
    """Create a mock configuration for testing"""
    config = CoverityConfig()
    config.host = "test-server.com"
    config.port = "443"
    config.ssl = True
    config.username = "testuser"
    config.auth_key = "testkey"
    config.proxies = {}
    set_config(config)
    return config


class TestCoverityTools:
    """Test cases for Coverity MCP tools"""
    
    @pytest.mark.asyncio
    async def test_get_coverity_projects_no_covautolib(self, mock_config):
        """Test get_coverity_projects when covautolib is not available"""
        with patch('coverity_mcp_server.tools.covautolib', side_effect=ImportError):
            result = await get_coverity_projects()
            assert "covautolib not available" in result
    
    @pytest.mark.asyncio
    async def test_get_project_streams_no_covautolib(self, mock_config):
        """Test get_project_streams when covautolib is not available"""
        with patch('coverity_mcp_server.tools.covautolib', side_effect=ImportError):
            result = await get_project_streams("test_project")
            assert "covautolib not available" in result
    
    @pytest.mark.asyncio
    @patch('coverity_mcp_server.tools.Client')
    async def test_get_coverity_projects_success(self, mock_client, mock_config):
        """Test successful get_coverity_projects call"""
        # Mock SOAP client and response
        mock_service = MagicMock()
        mock_project = MagicMock()
        mock_project.projectKey = "TEST_KEY"
        mock_project.id.name = "Test Project"
        mock_project.dateCreated = "2024-01-01"
        mock_project.userCreated = "testuser"
        
        mock_service.getProjects.return_value = [mock_project]
        mock_client_instance = MagicMock()
        mock_client_instance.service = mock_service
        mock_client.return_value = mock_client_instance
        
        with patch('builtins.__import__'):
            result = await get_coverity_projects()
            
        assert "Found 1 Coverity projects" in result
        assert "Test Project" in result
    
    @pytest.mark.asyncio
    @patch('coverity_mcp_server.tools.Client')
    async def test_get_project_streams_not_found(self, mock_client, mock_config):
        """Test get_project_streams when project is not found"""
        # Mock SOAP client to return empty results
        mock_service = MagicMock()
        mock_service.getProjects.return_value = []
        mock_client_instance = MagicMock()
        mock_client_instance.service = mock_service
        mock_client.return_value = mock_client_instance
        
        with patch('builtins.__import__'):
            result = await get_project_streams("nonexistent_project")
            
        assert "not found" in result
