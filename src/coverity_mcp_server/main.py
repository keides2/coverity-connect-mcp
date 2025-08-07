#!/usr/bin/env python3
"""
Coverity Connect MCP Server
A Model Context Protocol server for interacting with Coverity Connect (Black Duck)
"""

import os
import sys
import logging
from typing import List, Dict, Any, Optional
from urllib.parse import urlparse
from pathlib import Path

import click
from mcp.server.fastmcp import FastMCP

# .envファイルを読み込む（重要：最初に実行）
try:
    from dotenv import load_dotenv
    env_path = Path(__file__).parent.parent.parent / '.env'
    if env_path.exists():
        load_dotenv(env_path)
        # Windows環境対応: Unicode文字を使わない
        print(f"[OK] Loaded .env from {env_path}")
except ImportError:
    pass  # python-dotenvがない場合は環境変数を使用

from .coverity_client import CoverityClient

# Configure logging
import tempfile

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
    
    # 既存のクライアントがあれば再利用
    if coverity_client is not None:
        logger.info("Using existing Coverity client instance")
        return coverity_client
    
    # 環境変数から設定を取得
    coverity_url = os.getenv('COVERITY_HOST', '').strip()
    username = os.getenv('COVAUTHUSER', '').strip()
    password = os.getenv('COVAUTHKEY', '').strip()
    
    # プロキシ設定を取得（.envファイルから）
    proxy_host = os.getenv('PROXY_HOST', 'bypsproxy.daikin.co.jp').strip()
    proxy_port = os.getenv('PROXY_PORT', '3128').strip()
    
    # プロキシを環境変数に設定（aiohttpが使用）
    if proxy_host and proxy_port:
        proxy_url = f"http://{proxy_host}:{proxy_port}"
        os.environ['HTTP_PROXY'] = proxy_url
        os.environ['HTTPS_PROXY'] = proxy_url
        os.environ['http_proxy'] = proxy_url
        os.environ['https_proxy'] = proxy_url
        logger.info(f"Proxy configured: {proxy_url}")
    
    # デバッグ情報の出力（パスワードは隠す）
    logger.info("=== Coverity Client Initialization ===")
    logger.info(f"COVERITY_HOST: {coverity_url}")
    logger.info(f"COVAUTHUSER: {username}")
    logger.info(f"COVAUTHKEY: {'*' * 8 if password else 'NOT SET'}")
    logger.info(f"Proxy: {proxy_host}:{proxy_port}")
    logger.info(f"Working Directory: {os.getcwd()}")
    
    # 必須パラメータのチェック
    if not coverity_url:
        logger.error("COVERITY_HOST environment variable is missing")
        raise ValueError(
            "COVERITY_HOST environment variable is required. "
            "Please set it in your .env file or environment."
        )
    
    if not username:
        logger.error("COVAUTHUSER environment variable is missing")
        raise ValueError(
            "COVAUTHUSER environment variable is required. "
            "Please set your Coverity username."
        )
    
    if not password:
        logger.error("COVAUTHKEY environment variable is missing")
        raise ValueError(
            "COVAUTHKEY environment variable is required. "
            "Please set your Coverity authentication key."
        )
    
    # URLを正規化（末尾のスラッシュを削除）
    coverity_url = coverity_url.rstrip('/')
    
    # URLをパースして設定を抽出
    try:
        # URLに適切なスキームがない場合は追加
        if not coverity_url.startswith(('http://', 'https://')):
            logger.warning(f"No scheme in URL: {coverity_url}, assuming https://")
            coverity_url = f"https://{coverity_url}"
        
        parsed_url = urlparse(coverity_url)
        
        # ホスト名の抽出
        host = parsed_url.hostname
        if not host:
            # hostnameが取得できない場合はnetlocから取得
            host = parsed_url.netloc.split(':')[0]
        
        if not host:
            raise ValueError(f"Cannot extract hostname from URL: {coverity_url}")
        
        # ポート番号の抽出（テスト成功時と同じ設定）
        if parsed_url.port:
            port = parsed_url.port
        elif parsed_url.scheme == 'https':
            port = 443  # HTTPS標準ポート
        else:
            port = 8080  # Coverity Connect標準ポート
        
        # SSL設定の判定
        use_ssl = parsed_url.scheme == 'https'
        
        logger.info(f"Parsed configuration:")
        logger.info(f"  Host: {host}")
        logger.info(f"  Port: {port}")
        logger.info(f"  SSL: {use_ssl}")
        logger.info(f"  Full URL: {parsed_url.scheme}://{host}:{port}")
        
    except Exception as e:
        logger.error(f"Error parsing URL {coverity_url}: {e}")
        raise ValueError(f"Invalid COVERITY_HOST URL: {coverity_url}")
    
    # Coverityクライアントの作成
    try:
        coverity_client = CoverityClient(
            host=host,
            port=port,
            use_ssl=use_ssl,
            username=username,
            password=password
        )
        
        # Windows環境対応: Unicode文字を使わない
        logger.info(f"[OK] Successfully initialized Coverity client")
        logger.info(f"  Server: {host}:{port}")
        logger.info(f"  User: {username}")
        logger.info(f"  SSL: {use_ssl}")
        logger.info(f"  Proxy: {proxy_url if proxy_host else 'None'}")
        
        return coverity_client
        
    except Exception as e:
        logger.error(f"Failed to create Coverity client: {e}")
        logger.error("Please check:")
        logger.error("  1. Network connectivity to Coverity server")
        logger.error("  2. Proxy settings (if behind corporate firewall)")
        logger.error("  3. Authentication credentials")
        logger.error("  4. Server URL and port")
        raise

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
            logger.error(f"Error getting project config: {e}")
            return f"Error: {str(e)}"
    
    @mcp.resource("coverity://streams/{stream_id}/defects")
    async def get_stream_defects(stream_id: str) -> str:
        """Get defects for a stream"""
        try:
            client = initialize_client()
            defects = await client.get_defects(stream_id=stream_id)
            
            if not defects:
                return f"No defects found for stream {stream_id}"
            
            defect_summary = []
            for defect in defects[:10]:  # Limit to first 10 for readability
                defect_summary.append({
                    "cid": defect.get('cid'),
                    "checker": defect.get('checkerName'),
                    "type": defect.get('displayType'),
                    "severity": defect.get('displayImpact'),
                    "status": defect.get('displayStatus'),
                    "file": defect.get('displayFile'),
                    "function": defect.get('displayFunction')
                })
            
            return f"Stream {stream_id} Defects (showing first 10):\n{defect_summary}"
            
        except Exception as e:
            logger.error(f"Error getting stream defects: {e}")
            return f"Error: {str(e)}"
    
    # Register tools
    @mcp.tool()
    async def search_defects(
        query: str = "",
        stream_id: str = "",
        checker: str = "",
        severity: str = "",
        status: str = "",
        limit: int = 50
    ) -> List[Dict[str, Any]]:
        """
        Search for defects in Coverity Connect
        
        Args:
            query: General search query
            stream_id: Filter by stream ID
            checker: Filter by checker name
            severity: Filter by severity (High, Medium, Low)
            status: Filter by status (New, Triaged, Fixed, etc.)
            limit: Maximum number of results to return
        """
        try:
            client = initialize_client()
            
            # Build filter parameters
            filters = {}
            if stream_id:
                filters['streamId'] = stream_id
            if checker:
                filters['checker'] = checker
            if severity:
                filters['severity'] = severity
            if status:
                filters['status'] = status
            
            defects = await client.get_defects(
                query=query,
                filters=filters,
                limit=limit
            )
            
            return defects if defects else []
            
        except Exception as e:
            logger.error(f"Error searching defects: {e}")
            return [{"error": str(e)}]
    
    @mcp.tool()
    async def get_defect_details(cid: str) -> Dict[str, Any]:
        """
        Get detailed information about a specific defect
        
        Args:
            cid: Coverity Issue Identifier
        """
        try:
            client = initialize_client()
            defect = await client.get_defect_details(cid)
            
            if not defect:
                return {"error": f"Defect {cid} not found"}
            
            return defect
            
        except Exception as e:
            logger.error(f"Error getting defect details: {e}")
            return {"error": str(e)}
    
    @mcp.tool()
    async def list_projects() -> List[Dict[str, Any]]:
        """List all projects in Coverity Connect"""
        try:
            client = initialize_client()
            projects = await client.get_projects()
            
            return projects if projects else []
            
        except Exception as e:
            logger.error(f"Error listing projects: {e}")
            return [{"error": str(e)}]
    
    @mcp.tool()
    async def list_streams(project_id: str = "") -> List[Dict[str, Any]]:
        """
        List streams, optionally filtered by project
        
        Args:
            project_id: Optional project ID to filter streams
        """
        try:
            client = initialize_client()
            streams = await client.get_streams(project_id=project_id)
            
            return streams if streams else []
            
        except Exception as e:
            logger.error(f"Error listing streams: {e}")
            return [{"error": str(e)}]
    
    @mcp.tool()
    async def get_project_summary(project_id: str) -> Dict[str, Any]:
        """
        Get summary information for a project including defect counts
        
        Args:
            project_id: Project identifier
        """
        try:
            client = initialize_client()
            
            # Get project details
            project = await client.get_project(project_id)
            if not project:
                return {"error": f"Project {project_id} not found"}
            
            # Get streams for this project
            streams = await client.get_streams(project_id=project_id)
            
            # Get defect summary for each stream
            stream_summaries = []
            for stream in streams or []:
                stream_id = stream.get('name', '')
                defects = await client.get_defects(stream_id=stream_id, limit=1000)
                
                # Count defects by severity
                severity_counts = {'High': 0, 'Medium': 0, 'Low': 0}
                status_counts = {}
                
                for defect in defects or []:
                    severity = defect.get('displayImpact', 'Unknown')
                    status = defect.get('displayStatus', 'Unknown')
                    
                    if severity in severity_counts:
                        severity_counts[severity] += 1
                    
                    status_counts[status] = status_counts.get(status, 0) + 1
                
                stream_summaries.append({
                    'stream_name': stream_id,
                    'total_defects': len(defects or []),
                    'severity_breakdown': severity_counts,
                    'status_breakdown': status_counts
                })
            
            return {
                'project': project,
                'streams': stream_summaries,
                'total_streams': len(streams or [])
            }
            
        except Exception as e:
            logger.error(f"Error getting project summary: {e}")
            return {"error": str(e)}
    
    @mcp.tool()
    async def list_users(
        include_disabled: bool = False,
        limit: int = 200
    ) -> List[Dict[str, Any]]:
        """
        List all users in Coverity Connect
        
        Args:
            include_disabled: Include disabled users (default: False)
            limit: Maximum number of users to return (default: 200)
        """
        try:
            client = initialize_client()
            users = await client.get_users(
                disabled=include_disabled,
                include_details=True,
                locked=False,
                limit=limit
            )
            
            return users if users else []
            
        except Exception as e:
            logger.error(f"Error listing users: {e}")
            return [{"error": str(e)}]
    
    @mcp.tool()
    async def get_user_details(username: str) -> Dict[str, Any]:
        """
        Get detailed information about a specific user
        
        Args:
            username: Username to lookup
        """
        try:
            client = initialize_client()
            user = await client.get_user_details(username)
            
            if not user:
                return {"error": f"User {username} not found"}
            
            return user
            
        except Exception as e:
            logger.error(f"Error getting user details: {e}")
            return {"error": str(e)}
    
    @mcp.tool()
    async def get_user_roles(username: str) -> Dict[str, Any]:
        """
        Get role and permission information for a specific user
        
        Args:
            username: Username to lookup roles for
        """
        try:
            client = initialize_client()
            user = await client.get_user_details(username)
            
            if not user:
                return {"error": f"User {username} not found"}
            
            # Extract role information
            roles_info = {
                "username": user.get('name'),
                "superUser": user.get('superUser', False),
                "groups": user.get('groupNames', []),
                "roles": [],
                "status": {
                    "disabled": user.get('disabled', False),
                    "locked": user.get('locked', False),
                    "local": user.get('local', True)
                },
                "lastLogin": user.get('lastLogin'),
                "dateCreated": user.get('dateCreated')
            }
            
            # Process role assignments
            for role in user.get('roleAssignments', []):
                role_info = {
                    "roleName": role.get('roleName'),
                    "scope": role.get('scope'),
                    "roleAssignmentType": role.get('roleAssignmentType', 'user')
                }
                
                # Add description based on role name
                role_descriptions = {
                    "administrator": "システム全体の管理権限",
                    "projectOwner": "プロジェクトの所有者権限", 
                    "developer": "開発者権限",
                    "analyst": "分析者権限",
                    "viewer": "閲覧権限"
                }
                
                role_info["description"] = role_descriptions.get(
                    role.get('roleName'), 
                    f"{role.get('roleName')} 権限"
                )
                
                roles_info["roles"].append(role_info)
            
            return roles_info
            
        except Exception as e:
            logger.error(f"Error getting user roles: {e}")
            return {"error": str(e)}

    return mcp

def run_server():
    """Run the MCP server"""
    try:
        mcp = create_server()
        mcp.run()
    except Exception as e:
        logger.error(f"Failed to start server: {e}")
        sys.exit(1)

@click.command()
@click.option('--host', default='localhost', help='Coverity Connect host')
@click.option('--port', default=8080, help='Coverity Connect port')
@click.option('--ssl/--no-ssl', default=True, help='Use SSL connection')
@click.option('--username', help='Coverity username (or set COVAUTHUSER env var)')
@click.option('--password', help='Coverity password (or set COVAUTHKEY env var)')
def cli(host, port, ssl, username, password):
    """Start the Coverity Connect MCP Server"""
    
    # Set environment variables if provided via CLI
    if host:
        os.environ['COVERITY_HOST'] = host
    if port:
        os.environ['COVERITY_PORT'] = str(port)
    if ssl is not None:
        os.environ['COVERITY_SSL'] = str(ssl)
    if username:
        os.environ['COVAUTHUSER'] = username
    if password:
        os.environ['COVAUTHKEY'] = password
    
    run_server()

if __name__ == "__main__":
    cli()
