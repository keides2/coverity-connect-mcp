#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Coverity Connect MCP Server - Main Module
Enterprise-grade MCP server for Black Duck Coverity Connect static analysis platform

Features:
- cov_auto: CI/CD pipeline automation
- cov_snap: Snapshot management and CID detailed analysis
"""

import os
import sys
import json
import csv
import zipfile
from datetime import datetime
from typing import Dict, List, Optional, Any
import asyncio
from pathlib import Path
import click

# MCP Framework
from mcp.server.fastmcp import FastMCP
from mcp import (
    Context,
    Tool,
    Resource,
    Prompt,
    TextContent,
    LoggingLevel,
)

# Local imports
from .config import CoverityConfig
from .tools import (
    get_coverity_projects,
    get_project_streams, 
    get_stream_snapshots,
    analyze_snapshot_defects,
    run_coverity_automation,
    parse_coverity_issues,
    generate_quality_report
)
from .resources import (
    get_project_config,
    list_configured_projects
)
from .prompts import (
    coverity_security_analysis,
    coverity_pipeline_setup
)

# Global MCP server instance
mcp = None
config = None

def create_server() -> FastMCP:
    """Create and configure the MCP server instance"""
    global mcp, config
    
    # Initialize configuration
    config = CoverityConfig()
    
    # Initialize MCP server
    mcp = FastMCP(
        name="Coverity Connect Server",
        dependencies=["requests", "suds", "pandas"]
    )
    
    # Register tools
    mcp.add_tool(get_coverity_projects)
    mcp.add_tool(get_project_streams)
    mcp.add_tool(get_stream_snapshots)
    mcp.add_tool(analyze_snapshot_defects)
    mcp.add_tool(run_coverity_automation)
    mcp.add_tool(parse_coverity_issues)
    mcp.add_tool(generate_quality_report)
    
    # Register resources
    mcp.add_resource(get_project_config)
    mcp.add_resource(list_configured_projects)
    
    # Register prompts
    mcp.add_prompt(coverity_security_analysis)
    mcp.add_prompt(coverity_pipeline_setup)
    
    return mcp

def run_server():
    """Run the MCP server"""
    global mcp, config
    
    if mcp is None:
        mcp = create_server()
    
    # Environment variables check
    required_vars = ["COVAUTHUSER", "COVAUTHKEY"]
    missing_vars = [var for var in required_vars if not os.getenv(var)]
    
    if missing_vars:
        print(f"Warning: Missing environment variables: {missing_vars}")
        print("Some functionality may be limited.")
    
    # Check for covautolib availability
    try:
        from covautolib import covautolib_2, covautolib_3
        print("Info: covautolib available - full functionality enabled")
    except ImportError:
        print("Warning: covautolib not available. Running in limited mode.")
    
    # Start MCP server
    print(f"Starting Coverity Connect MCP Server...")
    print(f"Server: {config.host}:{config.port}")
    print(f"User: {config.username}")
    mcp.run()

@click.command()
@click.option('--host', default=None, help='Coverity Connect server host')
@click.option('--port', default=None, help='Coverity Connect server port')
@click.option('--user', default=None, help='Coverity Connect username')
@click.option('--debug', is_flag=True, help='Enable debug mode')
def cli(host, port, user, debug):
    """Coverity Connect MCP Server CLI"""
    
    # Override config with CLI options
    if host:
        os.environ['COVERITY_HOST'] = host
    if port:
        os.environ['COVERITY_PORT'] = str(port)
    if user:
        os.environ['COVAUTHUSER'] = user
    if debug:
        os.environ['LOG_LEVEL'] = 'DEBUG'
    
    # Run the server
    run_server()

if __name__ == "__main__":
    cli()
