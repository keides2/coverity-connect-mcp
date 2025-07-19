"""
MCP Resources for Coverity Connect integration
"""

from pathlib import Path
from typing import Optional

# Global configuration (will be set by main module)
config = None

def set_config(cfg):
    """Set the global configuration"""
    global config
    config = cfg

async def get_project_config(project_name: str) -> str:
    """
    Retrieve project configuration information
    
    Args:
        project_name: Name of the project
    """
    try:
        base_dir = Path(config.base_dir)
        config_file = base_dir / "config" / f"{project_name}.cfg"
        
        if not config_file.exists():
            return f"Configuration file not found: {config_file}"
        
        with open(config_file, 'r', encoding='utf-8') as f:
            config_content = f.read()
        
        return f"""
Project Configuration: {project_name}
=====================================

Configuration File: {config_file}

Content:
{config_content}

Usage:
This configuration file defines build commands and Coverity analysis 
settings for automated pipeline execution.
"""
    except Exception as e:
        return f"Error reading project config: {str(e)}"

async def list_configured_projects() -> str:
    """
    List all configured projects
    """
    try:
        base_dir = Path(config.base_dir)
        projects_file = base_dir / "config" / "projects.cfg"
        
        if not projects_file.exists():
            return "Projects configuration file not found"
        
        with open(projects_file, 'r', encoding='utf-8') as f:
            projects_content = f.read()
        
        # Parse project list
        configured_projects = []
        for line in projects_content.split('\n'):
            line = line.strip()
            if line and not line.startswith(';'):
                parts = line.split()
                if len(parts) >= 2:
                    configured_projects.append({
                        "group": parts[0],
                        "project": parts[1]
                    })
        
        return f"""
Configured Projects
==================
Total: {len(configured_projects)} projects

Projects:
{chr(10).join([f"- {p['group']}/{p['project']}" for p in configured_projects])}

Configuration File: {projects_file}
"""
    except Exception as e:
        return f"Error reading projects config: {str(e)}"
