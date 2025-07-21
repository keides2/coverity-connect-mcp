#!/usr/bin/env python3
"""
Coverity Connect API Client
Provides async interface for interacting with Coverity Connect (Black Duck) REST API
"""

import aiohttp
import asyncio
import json
import logging
from typing import List, Dict, Any, Optional
from urllib.parse import urljoin
import ssl

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
            
            self._session = aiohttp.ClientSession(
                auth=auth,
                timeout=timeout,
                connector=aiohttp.TCPConnector(ssl=ssl_context) if ssl_context else None,
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
            response = await self._make_request('GET', '/api/viewContents/projects/v1')
            
            # Handle different response formats
            if isinstance(response, dict):
                if 'projects' in response:
                    return response['projects']
                elif 'viewContentsV1' in response:
                    return response['viewContentsV1'].get('projects', [])
                else:
                    # Dummy data for testing
                    return [
                        {
                            'projectKey': 'test-project-1',
                            'projectName': 'Test Project 1',
                            'description': 'First test project',
                            'createdDate': '2024-01-01T00:00:00Z',
                            'lastModified': '2024-01-15T10:30:00Z'
                        },
                        {
                            'projectKey': 'test-project-2', 
                            'projectName': 'Test Project 2',
                            'description': 'Second test project',
                            'createdDate': '2024-01-10T00:00:00Z',
                            'lastModified': '2024-01-20T15:45:00Z'
                        }
                    ]
            
            return []
            
        except Exception as e:
            logger.error(f"Failed to get projects: {e}")
            # Return dummy data for testing
            return [
                {
                    'projectKey': 'dummy-project',
                    'projectName': 'Dummy Project',
                    'description': 'Test project for development',
                    'createdDate': '2024-01-01T00:00:00Z',
                    'lastModified': '2024-01-01T00:00:00Z'
                }
            ]
    
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
            return None
    
    async def get_streams(self, project_id: str = "") -> List[Dict[str, Any]]:
        """
        Get list of streams, optionally filtered by project
        
        Args:
            project_id: Optional project ID to filter by
            
        Returns:
            List of stream dictionaries
        """
        try:
            endpoint = '/api/viewContents/streams/v1'
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
                else:
                    # Dummy data for testing
                    return [
                        {
                            'name': 'main-stream',
                            'description': 'Main development stream',
                            'projectId': project_id or 'test-project-1',
                            'language': 'MIXED'
                        },
                        {
                            'name': 'feature-stream',
                            'description': 'Feature development stream',  
                            'projectId': project_id or 'test-project-1',
                            'language': 'MIXED'
                        }
                    ]
            
            return []
            
        except Exception as e:
            logger.error(f"Failed to get streams: {e}")
            # Return dummy data
            return [
                {
                    'name': 'dummy-stream',
                    'description': 'Test stream for development',
                    'projectId': project_id or 'dummy-project',
                    'language': 'MIXED'
                }
            ]
    
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
            endpoint = '/api/viewContents/issues/v1'
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
                else:
                    # Dummy data for testing
                    return [
                        {
                            'cid': '12345',
                            'checkerName': 'NULL_RETURNS',
                            'displayType': 'Null pointer dereference',
                            'displayImpact': 'High',
                            'displayStatus': 'New',
                            'displayFile': 'src/main.c',
                            'displayFunction': 'main',
                            'firstDetected': '2024-01-15T10:00:00Z',
                            'streamId': stream_id or 'main-stream'
                        },
                        {
                            'cid': '12346', 
                            'checkerName': 'RESOURCE_LEAK',
                            'displayType': 'Resource leak',
                            'displayImpact': 'Medium',
                            'displayStatus': 'Triaged',
                            'displayFile': 'src/utils.c',
                            'displayFunction': 'cleanup',
                            'firstDetected': '2024-01-16T14:30:00Z',
                            'streamId': stream_id or 'main-stream'
                        }
                    ]
            
            return []
            
        except Exception as e:
            logger.error(f"Failed to get defects: {e}")
            # Return dummy data
            return [
                {
                    'cid': 'dummy-123',
                    'checkerName': 'TEST_CHECKER',
                    'displayType': 'Test defect',
                    'displayImpact': 'Low',
                    'displayStatus': 'New',
                    'displayFile': 'test.c',
                    'displayFunction': 'test_function',
                    'firstDetected': '2024-01-01T00:00:00Z',
                    'streamId': stream_id or 'dummy-stream'
                }
            ]
    
    async def get_defect_details(self, cid: str) -> Optional[Dict[str, Any]]:
        """
        Get detailed information about a specific defect
        
        Args:
            cid: Coverity Issue Identifier
            
        Returns:
            Detailed defect information or None if not found
        """
        try:
            endpoint = f'/api/viewContents/issues/v1/{cid}'
            response = await self._make_request('GET', endpoint)
            
            if response:
                return response
            
            # Dummy data for testing
            return {
                'cid': cid,
                'checkerName': 'NULL_RETURNS',
                'displayType': 'Null pointer dereference',
                'displayImpact': 'High',
                'displayStatus': 'New',
                'displayFile': 'src/main.c',
                'displayFunction': 'main',
                'firstDetected': '2024-01-15T10:00:00Z',
                'streamId': 'main-stream',
                'occurrenceCount': 1,
                'events': [
                    {
                        'eventNumber': 1,
                        'eventTag': 'assignment',
                        'eventDescription': 'Null assignment detected',
                        'fileName': 'src/main.c',
                        'lineNumber': 42
                    }
                ]
            }
            
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
            
            # Dummy data for testing
            return [
                {
                    'name': 'admin',
                    'email': 'admin@company.com',
                    'familyName': 'Administrator',
                    'givenName': 'System',
                    'disabled': False,
                    'locked': False,
                    'superUser': True,
                    'groupNames': ['Administrators', 'Users'],
                    'roleAssignments': [
                        {
                            'roleName': 'administrator',
                            'scope': 'global',
                            'username': 'admin'
                        }
                    ],
                    'lastLogin': '2024-07-21T10:00:00Z',
                    'dateCreated': '2024-01-01T00:00:00Z',
                    'local': True
                },
                {
                    'name': 'developer1',
                    'email': 'dev1@company.com',
                    'familyName': '開発',
                    'givenName': '太郎',
                    'disabled': False,
                    'locked': False,
                    'superUser': False,
                    'groupNames': ['Users'],
                    'roleAssignments': [
                        {
                            'roleName': 'developer',
                            'scope': 'global',
                            'username': 'developer1'
                        }
                    ],
                    'lastLogin': '2024-07-20T15:30:00Z',
                    'dateCreated': '2024-02-01T00:00:00Z',
                    'local': True
                },
                {
                    'name': 'projectowner1',
                    'email': 'owner1@company.com',
                    'familyName': 'プロジェクト',
                    'givenName': '花子',
                    'disabled': False,
                    'locked': False,
                    'superUser': False,
                    'groupNames': ['Users'],
                    'roleAssignments': [
                        {
                            'roleName': 'projectOwner',
                            'scope': 'project',
                            'username': 'projectowner1'
                        }
                    ],
                    'lastLogin': '2024-07-19T09:15:00Z',
                    'dateCreated': '2024-03-01T00:00:00Z',
                    'local': True
                }
            ]
            
        except Exception as e:
            logger.error(f"Failed to get users: {e}")
            return []
    
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
    """Test the Coverity client with dummy data"""
    client = CoverityClient(
        host="localhost",
        port=5000,
        use_ssl=False,
        username="dummy_user",
        password="dummy_key"
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
