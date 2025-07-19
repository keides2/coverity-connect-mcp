"""
MCP Prompts for Coverity Connect integration
"""

async def coverity_security_analysis() -> str:
    """Coverity security analysis prompt template"""
    return """
Please analyze the Black Duck Coverity results for security vulnerabilities:

1. Use get_coverity_projects to list available projects
2. Select a project and use get_project_streams to see available streams  
3. Use get_stream_snapshots to find recent snapshots
4. Run analyze_snapshot_defects focusing on high-severity security issues
5. Use parse_coverity_issues with severity_filter="High" for detailed analysis

Focus on:
- Critical security vulnerabilities (CWE classifications)
- Authentication and authorization issues
- Input validation problems
- Memory safety issues
- Cryptographic vulnerabilities

Provide actionable remediation recommendations for each critical finding.
"""

async def coverity_pipeline_setup() -> str:
    """Coverity CI/CD pipeline setup prompt"""
    return """
Set up Black Duck Coverity automation pipeline for a project:

1. Use list_configured_projects resource to see existing configurations
2. Check project config with get_project_config resource
3. Run run_coverity_automation to execute the pipeline
4. Monitor results with parse_coverity_issues
5. Generate summary with generate_quality_report

Configuration steps:
- Verify project is listed in projects.cfg
- Ensure project-specific .cfg file exists with build commands
- Set up notification preferences
- Configure version control integration triggers

Pipeline includes:
- Git repository synchronization
- Build environment setup  
- Coverity static analysis
- Results parsing and filtering
- Automated reporting and notification
"""
