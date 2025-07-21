# Changelog

All notable changes to the Coverity Connect MCP Server project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- Initial MCP server implementation for Black Duck Coverity Connect
- Comprehensive REST API integration with 8 MCP tools
- Project and stream management tools
- Advanced defect search and analysis capabilities 
- ✨ **User Management Features**: Complete user administration system
  - `list_users`: List all users with filtering options
  - `get_user_details`: Get detailed user information
  - `get_user_roles`: Get user role and permission information with Japanese descriptions
- Security vulnerability analysis tools
- Quality reporting features
- Docker containerization support
- GitHub Actions CI/CD pipeline
- Comprehensive test suite
- Documentation and examples

### Security
- Secure authentication key handling
- Environment variable configuration
- Input validation and sanitization
- Proxy support for corporate environments

## [1.0.0] - 2025-01-XX

### Added
- First stable release
- Complete MCP protocol implementation
- Full Black Duck Coverity Connect integration
- Comprehensive documentation
- Testing suite with high coverage
- Multi-platform support (Windows/macOS/Linux)
- CLI interface with click
- Rich console output
- Configuration validation
- Error handling and logging

### Changed
- Updated branding from Synopsys Coverity to Black Duck Coverity
- Improved proxy configuration handling
- Enhanced security practices

### Technical Details
- Python 3.8+ support
- FastMCP framework integration
- aiohttp async HTTP client for REST API communication
- Type hints and mypy compatibility
- Black code formatting
- pytest test framework
- GitHub Actions automation

### MCP Tools Implemented
- `search_defects`: Advanced defect search with filtering
- `get_defect_details`: Detailed defect information retrieval
- `list_projects`: Project inventory management
- `list_streams`: Stream management by project
- `get_project_summary`: Comprehensive project analysis
- `list_users`: User inventory and management ✨
- `get_user_details`: Individual user profile access ✨
- `get_user_roles`: Role-based access control analysis ✨

### Dependencies
- mcp>=1.0.0
- fastmcp>=0.1.0
- aiohttp>=3.8.0
- suds-community>=1.1.2
- requests>=2.31.0
- pandas>=1.5.0
- click>=8.0.0
- rich>=13.0.0

---

## Release Process

1. Update version in `pyproject.toml`
2. Update version in `src/coverity_mcp_server/__init__.py`
3. Update this CHANGELOG.md
4. Create git tag: `git tag v1.0.0`
5. Push tag: `git push origin v1.0.0`
6. GitHub Actions will automatically build and publish to PyPI

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for development setup and contribution guidelines.