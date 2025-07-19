"""
Coverity Connect MCP Server

A Model Context Protocol server for Black Duck Coverity Connect static analysis platform.
Provides seamless integration between AI assistants and Coverity through natural language commands.
"""

__version__ = "1.0.0"
__author__ = "Your Name"
__email__ = "your.email@example.com"
__description__ = "Model Context Protocol server for Black Duck Coverity Connect static analysis platform"

from .main import create_server, run_server

__all__ = ["create_server", "run_server", "__version__"]
