#!/usr/bin/env python3
"""
Coverity Connect MCP Server - Production Version
A Model Context Protocol server for interacting with Coverity Connect (Black Duck)
This version uses environment variables for configuration without hardcoded credentials.
"""

import os
import sys
import logging
from typing import List, Dict, Any, Optional
from urllib.parse import urlparse

import click
from mcp.server.fastmcp import FastMCP

from .coverity_client import CoverityClient

# Configure logging
import tempfile
from pathlib import Path

# Set log file to project directory
project_root = Path(__file__).parent.parent.parent
log_file = project_root / "logs" / "coverity_mcp_server.log"

# Create logs directory if it doesn't exist
log_file.parent.mkdir(exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(log_file),
        logging.StreamHandler()  # Also keep console output
    ]
)
logger = logging.getLogger(__name__)

# Global client instance
coverity_client: Optional[CoverityClient] = None

def initialize_client() -> CoverityClient:
    """Initialize Coverity client with environment variables"""
    global coverity_client
    
    if coverity_client is not None:
        return coverity_client
    
    # Get configuration from environment variables
    coverity_url = os.getenv('COVERITY_HOST')
    username = os.getenv('COVAUTHUSER')
    password = os.getenv('COVAUTHKEY')
    
    logger.info("=== Configuration Loading ===")
    logger.info(f"COVERITY_HOST: {coverity_url}")
    logger.info(f"COVAUTHUSER: {username}")
    logger.info(f"COVAUTHKEY: {'***' if password else 'None'}")
    
    # Set proxy environment variables if not already set
    if not os.getenv('HTTPS_PROXY') and not os.getenv('https_proxy'):
        proxy_host = os.getenv('PROXY_HOST')
        proxy_port = os.getenv('PROXY_PORT', '')
        if proxy_host:
            proxy_url = f'http://{proxy_host}:{proxy_port}'
            os.environ['HTTPS_PROXY'] = proxy_url
        os.environ['HTTP_PROXY'] = proxy_url
        logger.info(f"Set proxy: {proxy_url}")
    
    # Handle missing configuration gracefully
    if not coverity_url:
        logger.error("COVERITY_HOST environment variable is required")
        raise ValueError("COVERITY_HOST environment variable is not set")
    
    if not username:
        logger.error("COVAUTHUSER environment variable is required")
        raise ValueError("COVAUTHUSER environment variable is not set")
    
    if not password:
        logger.error("COVAUTHKEY environment variable is required")
        raise ValueError("COVAUTHKEY environment variable is not set")
    
    # Parse URL to extract host, port, and SSL setting
    try:
        parsed_url = urlparse(coverity_url)
        
        # Extract host (remove trailing slash if present)
        host = parsed_url.hostname or parsed_url.netloc.split(':')[0]
        
        # Handle cases where hostname is still empty
        if not host:
            logger.error(f"Could not parse hostname from URL: {coverity_url}")
            raise ValueError(f"Invalid COVERITY_HOST URL: {coverity_url}")
        
        # Extract port
        if parsed_url.port:
            port = parsed_url.port
        elif parsed_url.scheme == 'https':
            port = 443
        else:
            port = 8080
        
        # Determine SSL setting
        use_ssl = parsed_url.scheme == 'https'
        
        logger.info(f"Parsed URL - Host: {host}, Port: {port}, SSL: {use_ssl}")
        
    except Exception as e:
        logger.error(f"Error parsing URL {coverity_url}: {e}")
        raise ValueError(f"Invalid COVERITY_HOST URL format: {coverity_url}")
    
    coverity_client = CoverityClient(
        host=host,
        port=port,
        use_ssl=use_ssl,
        username=username,
        password=password
    )
    
    logger.info(f"Initialized Coverity client for {host}:{port} (SSL: {use_ssl})")
    return coverity_client

def create_server() -> FastMCP:
    """Create and configure the MCP server"""
    # Initialize the server
    mcp = FastMCP("Coverity Connect MCP Server")
    
    # Initialize Coverity client
    try:
        initialize_client()
        logger.info("Coverity client initialized successfully")
    except Exception as e:
        logger.error(f"Failed to initialize Coverity client: {e}")
        raise
    
    # Register resources using decorators
    @mcp.resource("coverity://projects/{project_id}/config")
    async def get_project_config(project_id: str) -> str:
        """Get project configuration"""
        try:
            client = initialize_client()
            project = await client.get_project(project_id)
            if not project:
                return f"Project {project_id} not found"
            
            config_info = {
                "project_id": project.get('projectKey'),
                "project_name": project.get('projectName'),
                "description": project.get('description', 'No description'),
                "created_date": project.get('createdDate'),
                "last_modified": project.get('lastModified'),
                "streams": project.get('streams', [])
            }
            
            return f"Project Configuration:\n{config_info}"
            
        except Exception as e:
            logger.error(f"Failed to get project config: {e}")
            return f"Error getting project configuration: {e}"
    
    @mcp.resource("coverity://streams/{stream_id}/status")
    async def get_stream_status(stream_id: str) -> str:
        """Get stream status and recent defects"""
        try:
            client = initialize_client()
            
            # Get stream details
            streams = await client.get_streams()
            stream = next((s for s in streams if s.get('name') == stream_id), None)
            
            if not stream:
                return f"Stream {stream_id} not found"
            
            # Get recent defects for this stream
            defects = await client.get_defects(stream_id=stream_id, limit=10)
            
            status_info = {
                "stream_id": stream.get('name'),
                "description": stream.get('description', 'No description'),
                "project_id": stream.get('projectId'),
                "language": stream.get('language'),
                "total_defects": len(defects),
                "recent_defects": [
                    {
                        "cid": d.get('cid'),
                        "checker": d.get('checkerName'),
                        "impact": d.get('displayImpact'),
                        "status": d.get('displayStatus')
                    }
                    for d in defects[:5]  # Top 5 recent defects
                ]
            }
            
            return f"Stream Status:\n{status_info}"
            
        except Exception as e:
            logger.error(f"Failed to get stream status: {e}")
            return f"Error getting stream status: {e}"
    
    # Register tools using decorators
    @mcp.tool()
    async def list_projects() -> List[Dict[str, Any]]:
        """
        List all projects in Coverity Connect
        
        Returns:
            List of projects with their basic information
        """
        try:
            client = initialize_client()
            projects = await client.get_projects()
            
            logger.info(f"Retrieved {len(projects)} projects")
            return projects
            
        except Exception as e:
            logger.error(f"Failed to list projects: {e}")
            raise RuntimeError(f"Error listing projects: {e}")
    
    @mcp.tool()
    async def list_streams(project_id: str = "") -> List[Dict[str, Any]]:
        """
        List streams, optionally filtered by project
        
        Args:
            project_id: Optional project ID to filter streams
        
        Returns:
            List of streams
        """
        try:
            client = initialize_client()
            streams = await client.get_streams(project_id=project_id)
            
            logger.info(f"Retrieved {len(streams)} streams" + 
                       (f" for project {project_id}" if project_id else ""))
            return streams
            
        except Exception as e:
            logger.error(f"Failed to list streams: {e}")
            raise RuntimeError(f"Error listing streams: {e}")
    
    @mcp.tool()
    async def get_project_summary(project_id: str) -> Dict[str, Any]:
        """
        Get summary information for a project including defect counts
        
        Args:
            project_id: Project identifier
        
        Returns:
            Project summary with defect statistics
        """
        try:
            client = initialize_client()
            
            # Get project details
            project = await client.get_project(project_id)
            if not project:
                raise ValueError(f"Project {project_id} not found")
            
            # Get streams for this project
            streams = await client.get_streams(project_id=project_id)
            
            # Get defect counts for each stream
            total_defects = 0
            stream_summaries = []
            
            for stream in streams:
                stream_name = stream.get('name', '')
                defects = await client.get_defects(stream_id=stream_name, limit=1000)
                defect_count = len(defects)
                total_defects += defect_count
                
                stream_summaries.append({
                    "stream_name": stream_name,
                    "defect_count": defect_count,
                    "description": stream.get('description', '')
                })
            
            summary = {
                "project_key": project.get('projectKey'),
                "project_name": project.get('projectName'),
                "description": project.get('description', ''),
                "created_date": project.get('createdDate'),
                "last_modified": project.get('lastModified'),
                "total_streams": len(streams),
                "total_defects": total_defects,
                "streams": stream_summaries
            }
            
            logger.info(f"Generated summary for project {project_id}")
            return summary
            
        except Exception as e:
            logger.error(f"Failed to get project summary: {e}")
            raise RuntimeError(f"Error getting project summary: {e}")
    
    @mcp.tool()
    async def search_defects(query: str = "", stream_id: str = "", 
                           checker: str = "", severity: str = "", 
                           status: str = "", limit: int = 50) -> List[Dict[str, Any]]:
        """
        Search for defects in Coverity Connect
        
        Args:
            query: General search query
            stream_id: Filter by stream ID
            checker: Filter by checker name
            severity: Filter by severity (High, Medium, Low)
            status: Filter by status (New, Triaged, Fixed, etc.)
            limit: Maximum number of results to return
        
        Returns:
            List of defects matching the search criteria
        """
        try:
            client = initialize_client()
            
            # Build filters dictionary
            filters = {}
            if checker:
                filters['checker'] = checker
            if severity:
                filters['severity'] = severity
            if status:
                filters['status'] = status
            
            defects = await client.get_defects(
                stream_id=stream_id,
                query=query,
                filters=filters,
                limit=limit
            )
            
            logger.info(f"Found {len(defects)} defects matching search criteria")
            return defects
            
        except Exception as e:
            logger.error(f"Failed to search defects: {e}")
            raise RuntimeError(f"Error searching defects: {e}")
    
    @mcp.tool()
    async def get_defect_details(cid: str) -> Optional[Dict[str, Any]]:
        """
        Get detailed information about a specific defect
        
        Args:
            cid: Coverity Issue Identifier
        
        Returns:
            Detailed defect information or None if not found
        """
        try:
            client = initialize_client()
            defect = await client.get_defect_details(cid)
            
            if defect:
                logger.info(f"Retrieved details for defect {cid}")
            else:
                logger.warning(f"Defect {cid} not found")
            
            return defect
            
        except Exception as e:
            logger.error(f"Failed to get defect details: {e}")
            raise RuntimeError(f"Error getting defect details: {e}")
    
    @mcp.tool()
    async def list_users(include_disabled: bool = False, limit: int = 200) -> List[Dict[str, Any]]:
        """
        List all users in Coverity Connect
        
        Args:
            include_disabled: Include disabled users (default: False)
            limit: Maximum number of users to return (default: 200)
        
        Returns:
            List of users with their information
        """
        try:
            client = initialize_client()
            users = await client.get_users(
                disabled=include_disabled,
                limit=limit
            )
            
            logger.info(f"Retrieved {len(users)} users")
            return users
            
        except Exception as e:
            logger.error(f"Failed to list users: {e}")
            raise RuntimeError(f"Error listing users: {e}")
    
    @mcp.tool()
    async def get_user_details(username: str) -> Optional[Dict[str, Any]]:
        """
        Get detailed information about a specific user
        
        Args:
            username: Username to lookup
        
        Returns:
            User details or None if not found
        """
        try:
            client = initialize_client()
            user = await client.get_user_details(username)
            
            if user:
                logger.info(f"Retrieved details for user {username}")
            else:
                logger.warning(f"User {username} not found")
            
            return user
            
        except Exception as e:
            logger.error(f"Failed to get user details: {e}")
            raise RuntimeError(f"Error getting user details: {e}")
    
    @mcp.tool()
    async def get_user_roles(username: str) -> Dict[str, Any]:
        """
        Get role and permission information for a specific user
        
        Args:
            username: Username to lookup roles for
        
        Returns:
            User role information
        """
        try:
            client = initialize_client()
            user = await client.get_user_details(username)
            
            if not user:
                raise ValueError(f"User {username} not found")
            
            role_info = {
                "username": user.get('name'),
                "email": user.get('email'),
                "groups": user.get('groupNames', []),
                "roles": user.get('roleAssignments', []),
                "super_user": user.get('superUser', False),
                "disabled": user.get('disabled', False),
                "locked": user.get('locked', False)
            }
            
            logger.info(f"Retrieved role information for user {username}")
            return role_info
            
        except Exception as e:
            logger.error(f"Failed to get user roles: {e}")
            raise RuntimeError(f"Error getting user roles: {e}")
    
    return mcp

@click.command()
@click.option("--host", default="localhost", help="Host to bind to")
@click.option("--port", default=3000, help="Port to bind to")
@click.option("--log-level", default="INFO", help="Logging level")
def main(host: str, port: int, log_level: str):
    """Start the Coverity Connect MCP server"""
    
    # Set logging level
    logging.getLogger().setLevel(getattr(logging, log_level.upper()))
    
    # Check required environment variables
    required_vars = ['COVERITY_HOST', 'COVAUTHUSER', 'COVAUTHKEY']
    missing_vars = [var for var in required_vars if not os.getenv(var)]
    
    if missing_vars:
        logger.error(f"Missing required environment variables: {', '.join(missing_vars)}")
        logger.error("Please set the following environment variables:")
        logger.error("  COVERITY_HOST - Coverity Connect server URL (e.g., https://coverity.company.com)")
        logger.error("  COVAUTHUSER - Coverity Connect username")
        logger.error("  COVAUTHKEY - Coverity Connect password/token")
        logger.error("Optional environment variables:")
        logger.error("  PROXY_HOST - Proxy hostname (if proxy is required)")
        logger.error("  PROXY_PORT - Proxy port (if proxy is required)")
        sys.exit(1)
    
    try:
        logger.info("Starting Coverity Connect MCP Server...")
        
        # Create and configure server
        server = create_server()
        
        # Run the server
        server.run(host=host, port=port)
        
    except KeyboardInterrupt:
        logger.info("Server stopped by user")
    except Exception as e:
        logger.error(f"Server error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
