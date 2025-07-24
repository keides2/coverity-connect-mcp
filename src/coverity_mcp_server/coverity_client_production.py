#!/usr/bin/env python3
"""
Coverity Connect API Client - Production Version
Provides async interface for interacting with Coverity Connect (Black Duck) REST API
This version uses environment variables for proxy configuration without hardcoded values.
"""

import aiohttp
import asyncio
import json
import logging
from typing import List, Dict, Any, Optional
from urllib.parse import urljoin
import ssl
import os

logger = logging.getLogger(__name__)

class CoverityClient:
    """Async client for Coverity Connect REST API"""
    
    def __init__(self, host: str, port: int = 8080, use_ssl: bool = True, 
                 username: str = "", password: str = ""):
        """
        Initialize Coverity Connect client
        
        Args:
            host: Coverity Connect server hostname
            port: Server port (default: 8080)
            use_ssl: Use HTTPS connection (default: True)
            username: Authentication username
            password: Authentication password/token
        """
        self.host = host
        self.port = port
        self.use_ssl = use_ssl
        self.username = username
        self.password = password
        
        # Build base URL
        protocol = "https" if use_ssl else "http"
        self.base_url = f"{protocol}://{host}:{port}"
        
        # Session will be created when needed
        self._session: Optional[aiohttp.ClientSession] = None
        
        logger.info(f"Initialized Coverity client for {self.base_url}")
    
    async def _get_session(self) -> aiohttp.ClientSession:
        """Get or create HTTP session"""
        if self._session is None or self._session.closed:
            # Create SSL context
            ssl_context = None
            if self.use_ssl:
                ssl_context = ssl.create_default_context()
                # For testing with self-signed certificates
                ssl_context.check_hostname = False
                ssl_context.verify_mode = ssl.CERT_NONE
            
            # Create auth header
            auth = aiohttp.BasicAuth(self.username, self.password)
            
            # Create session with timeout
            timeout = aiohttp.ClientTimeout(total=30)
            
            # Configure proxy from environment variables
            proxy = None
            
            # Check for proxy settings from environment
            http_proxy = os.getenv('HTTP_PROXY') or os.getenv('http_proxy')
            https_proxy = os.getenv('HTTPS_PROXY') or os.getenv('https_proxy')
            
            # If no standard proxy environment variables are set, check for custom ones
            if not http_proxy and not https_proxy:
                proxy_host = os.getenv('PROXY_HOST')
                proxy_port = os.getenv('PROXY_PORT')
                if proxy_host and proxy_port:
                    proxy_url = f'http://{proxy_host}:{proxy_port}'
                    if self.use_ssl:
                        https_proxy = proxy_url
                    else:
                        http_proxy = proxy_url
                    logger.info(f"Using custom proxy configuration: {proxy_url}")
            
            if self.use_ssl and https_proxy:
                proxy = https_proxy
                logger.info(f"Using HTTPS proxy: {proxy}")
            elif not self.use_ssl and http_proxy:
                proxy = http_proxy
                logger.info(f"Using HTTP proxy: {proxy}")
            
            connector = aiohttp.TCPConnector(ssl=ssl_context) if ssl_context else None
            
            self._session = aiohttp.ClientSession(
                auth=auth,
                timeout=timeout,
                connector=connector,
                headers={
                    'Accept': 'application/json',
                    'Content-Type': 'application/json'
                }
            )
        
        return self._session
    
    async def close(self):
        """Close HTTP session"""
        if self._session and not self._session.closed:
            await self._session.close()
    
    async def _make_request(self, method: str, endpoint: str, 
                           params: Dict[str, Any] = None, 
                           data: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Make HTTP request to Coverity Connect API
        
        Args:
            method: HTTP method (GET, POST, etc.)
            endpoint: API endpoint path
            params: Query parameters
            data: Request body data
            
        Returns:
            JSON response data
        """
        session = await self._get_session()
        url = urljoin(self.base_url, endpoint)
        
        try:
            logger.debug(f"Making {method} request to {url}")
            
            kwargs = {}
            if params:
                kwargs['params'] = params
            if data:
                kwargs['json'] = data
            
            # Configure proxy for this request from environment variables
            http_proxy = os.getenv('HTTP_PROXY') or os.getenv('http_proxy')
            https_proxy = os.getenv('HTTPS_PROXY') or os.getenv('https_proxy')
            
            # If no standard proxy environment variables, check custom ones
            if not http_proxy and not https_proxy:
                proxy_host = os.getenv('PROXY_HOST')
                proxy_port = os.getenv('PROXY_PORT')
                if proxy_host and proxy_port:
                    proxy_url = f'http://{proxy_host}:{proxy_port}'
                    if self.use_ssl:
                        https_proxy = proxy_url
                    else:
                        http_proxy = proxy_url
            
            if self.use_ssl and https_proxy:
                kwargs['proxy'] = https_proxy
                logger.debug(f"Using HTTPS proxy: {https_proxy}")
            elif not self.use_ssl and http_proxy:
                kwargs['proxy'] = http_proxy
                logger.debug(f"Using HTTP proxy: {http_proxy}")
            
            async with session.request(method, url, **kwargs) as response:
                logger.debug(f"Response status: {response.status}")
                
                if response.status == 200:
                    try:
                        return await response.json()
                    except json.JSONDecodeError:
                        # Return text response if not JSON
                        text = await response.text()
                        return {"response": text}
                elif response.status == 401:
                    raise Exception("Authentication failed - check credentials")
                elif response.status == 404:
                    logger.warning(f"Resource not found: {url}")
                    return {}
                else:
                    text = await response.text()
                    raise Exception(f"HTTP {response.status}: {text}")
                    
        except aiohttp.ClientError as e:
            logger.error(f"Request failed: {e}")
            raise Exception(f"Connection error: {e}")
    
    async def get_projects(self) -> List[Dict[str, Any]]:
        """
        Get list of projects
        
        Returns:
            List of project dictionaries
        """
        try:
            response = await self._make_request('GET', '/api/v2/projects')
            
            # Handle different response formats
            if isinstance(response, dict):
                if 'projects' in response:
                    return response['projects']
                elif 'viewContentsV1' in response:
                    return response['viewContentsV1'].get('projects', [])
            
            return []
            
        except Exception as e:
            logger.error(f"Failed to get projects: {e}")
            raise
    
    async def get_project(self, project_id: str) -> Optional[Dict[str, Any]]:
        """
        Get specific project details
        
        Args:
            project_id: Project identifier
            
        Returns:
            Project dictionary or None if not found
        """
        try:
            projects = await self.get_projects()
            for project in projects:
                if (project.get('projectKey') == project_id or 
                    project.get('projectName') == project_id):
                    return project
            
            return None
            
        except Exception as e:
            logger.error(f"Failed to get project {project_id}: {e}")
            raise
    
    async def get_streams(self, project_id: str = "") -> List[Dict[str, Any]]:
        """
        Get list of streams, optionally filtered by project
        
        Args:
            project_id: Optional project ID to filter by
            
        Returns:
            List of stream dictionaries
        """
        try:
            endpoint = '/api/v2/streams'
            params = {}
            if project_id:
                params['projectId'] = project_id
            
            response = await self._make_request('GET', endpoint, params=params)
            
            # Handle different response formats
            if isinstance(response, dict):
                if 'streams' in response:
                    return response['streams']
                elif 'viewContentsV1' in response:
                    return response['viewContentsV1'].get('streams', [])
            
            return []
            
        except Exception as e:
            logger.error(f"Failed to get streams: {e}")
            raise
    
    async def get_defects(self, stream_id: str = "", query: str = "", 
                         filters: Dict[str, str] = None, 
                         limit: int = 100) -> List[Dict[str, Any]]:
        """
        Get defects from Coverity Connect
        
        Args:
            stream_id: Stream identifier to filter by
            query: Search query
            filters: Additional filters (checker, severity, status, etc.)
            limit: Maximum number of results
            
        Returns:
            List of defect dictionaries
        """
        try:
            endpoint = '/api/v2/issues/search'
            params = {'rowCount': limit}
            
            if stream_id:
                params['streamId'] = stream_id
            if query:
                params['query'] = query
                
            # Add filters
            if filters:
                params.update(filters)
            
            response = await self._make_request('GET', endpoint, params=params)
            
            # Handle different response formats
            if isinstance(response, dict):
                if 'issues' in response:
                    return response['issues']
                elif 'viewContentsV1' in response:
                    return response['viewContentsV1'].get('issues', [])
            
            return []
            
        except Exception as e:
            logger.error(f"Failed to get defects: {e}")
            raise
    
    async def get_defect_details(self, cid: str) -> Optional[Dict[str, Any]]:
        """
        Get detailed information about a specific defect
        
        Args:
            cid: Coverity Issue Identifier
            
        Returns:
            Detailed defect information or None if not found
        """
        try:
            endpoint = f'/api/v2/issues/{cid}'
            response = await self._make_request('GET', endpoint)
            
            if response:
                return response
            return None
            
        except Exception as e:
            logger.error(f"Failed to get defect details for {cid}: {e}")
            return None
    
    async def get_users(self, disabled: bool = False, include_details: bool = True, 
                       locked: bool = False, limit: int = 200) -> List[Dict[str, Any]]:
        """
        Get all users from Coverity Connect
        
        Args:
            disabled: Include disabled users (default: False)
            include_details: Include detailed user information (default: True)
            locked: Include locked users (default: False)
            limit: Maximum number of users to return (default: 200)
            
        Returns:
            List of user dictionaries
        """
        try:
            params = {
                'disabled': str(disabled).lower(),
                'includeDetails': str(include_details).lower(),
                'locked': str(locked).lower(),
                'offset': '0',
                'rowCount': str(limit),
                'sortColumn': 'name',
                'sortOrder': 'asc'
            }
            
            response = await self._make_request('GET', '/api/v2/users', params=params)
            
            if response and 'users' in response:
                return response['users']
            
            return []
            
        except Exception as e:
            logger.error(f"Failed to get users: {e}")
            raise
    
    async def get_user_details(self, username: str) -> Optional[Dict[str, Any]]:
        """
        Get detailed information about a specific user
        
        Args:
            username: Username to lookup
            
        Returns:
            User details dictionary or None if not found
        """
        try:
            response = await self._make_request('GET', f'/api/v2/users/{username}')
            
            if response and 'users' in response and response['users']:
                return response['users'][0]
            
            # Try to find user in all users list
            users = await self.get_users()
            for user in users:
                if user.get('name') == username:
                    return user
            
            return None
            
        except Exception as e:
            logger.error(f"Failed to get user details for {username}: {e}")
            return None

    async def __aenter__(self):
        """Async context manager entry"""
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit"""
        await self.close()

# Utility functions for testing
async def test_client():
    """Test the Coverity client"""
    # Get configuration from environment
    host = os.getenv('COVERITY_HOST', 'localhost')
    username = os.getenv('COVAUTHUSER', 'test_user')
    password = os.getenv('COVAUTHKEY', 'test_password')
    
    if host.startswith('http'):
        from urllib.parse import urlparse
        parsed = urlparse(host)
        actual_host = parsed.hostname or 'localhost'
        port = parsed.port or (443 if parsed.scheme == 'https' else 8080)
        use_ssl = parsed.scheme == 'https'
    else:
        actual_host = host
        port = 8080
        use_ssl = False
    
    client = CoverityClient(
        host=actual_host,
        port=port,
        use_ssl=use_ssl,
        username=username,
        password=password
    )
    
    try:
        print("Testing Coverity client...")
        
        # Test projects
        projects = await client.get_projects()
        print(f"Found {len(projects)} projects")
        
        # Test streams
        streams = await client.get_streams()
        print(f"Found {len(streams)} streams")
        
        # Test defects
        defects = await client.get_defects(limit=5)
        print(f"Found {len(defects)} defects")
        
        print("Client test completed successfully!")
        
    except Exception as e:
        print(f"Client test failed: {e}")
    finally:
        await client.close()

if __name__ == "__main__":
    # Run test
    asyncio.run(test_client())
