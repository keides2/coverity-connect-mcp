# Installation Guide - Coverity Connect MCP Server

## 🎯 Overview

This guide provides comprehensive installation instructions for the Coverity Connect MCP Server across different environments and platforms.

## 📋 Prerequisites

### System Requirements
- **Python**: 3.8 or higher
- **Operating System**: Windows 10/11, macOS 10.14+, or Linux (Ubuntu 18.04+, CentOS 7+)
- **Memory**: Minimum 512MB RAM, Recommended 1GB+
- **Disk Space**: 100MB for installation, 500MB for logs and data
- **Network**: Access to Coverity Connect server (typically port 8080/443)

### Required Software
- **Python Package Manager**: pip 21.0+
- **Git**: For source installation (optional)
- **Claude Desktop**: Latest version for MCP integration

### Access Requirements
- **Coverity Connect**: Valid user account with appropriate permissions
- **Authentication**: Auth key or username/password credentials
- **Network Access**: Connectivity to Coverity Connect server

## 🚀 Installation Methods

### Method 1: Package Installation (Recommended)

#### Using pip
```bash
# Install from source (current method)
git clone https://github.com/keides2/coverity-connect-mcp.git
cd coverity-connect-mcp
pip install -e .
```

#### Verify Installation
```bash
# Test import
python -c "import coverity_mcp_server; print('Installation successful')"

# Check version
python -m coverity_mcp_server --help
```

### Method 2: Source Installation

#### Clone Repository
```bash
git clone https://github.com/keides2/coverity-connect-mcp.git
cd coverity-connect-mcp
```

#### Create Virtual Environment
```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
# Windows:
venv\Scripts\activate
# macOS/Linux:
source venv/bin/activate
```

#### Install Dependencies
```bash
# Development installation
pip install -e .

# Development dependencies (optional)
pip install -e ".[dev]"
```

## 🔧 Claude Desktop Integration

### Configuration Location
Find your Claude Desktop configuration file:

**Windows:**
- `%APPDATA%\Claude\claude_desktop_config.json`
- `%LOCALAPPDATA%\Claude\claude_desktop_config.json`

**macOS:**
- `~/Library/Application Support/Claude/claude_desktop_config.json`

**Linux:**
- `~/.config/claude/claude_desktop_config.json`

### Configuration Setup
Add the following to your Claude Desktop configuration:

```json
{
  "mcpServers": {
    "coverity-connect": {
      "command": "python",
      "args": ["-m", "coverity_mcp_server"],
      "cwd": "/path/to/coverity-connect-mcp",
      "env": {
        "COVERITY_HOST": "your-coverity-server.com",
        "COVERITY_PORT": "8080",
        "COVERITY_SSL": "True",
        "COVAUTHUSER": "your-username",
        "COVAUTHKEY": "your-auth-key"
      }
    }
  }
}
```

## 🧪 Installation Verification

### Basic Tests
```bash
# Test import
python -c "import coverity_mcp_server; print('✅ Import successful')"

# Test server startup
python -m coverity_mcp_server --help

# Test configuration
python -c "from coverity_mcp_server.config import get_config; print('✅ Config loaded')"
```

### Development Environment Test
```bash
# Start mock server (in separate terminal)
python examples/development/mock_server.py

# Test MCP server with mock data
export COVERITY_HOST=localhost
export COVERITY_PORT=5000
export COVERITY_SSL=False
export COVAUTHUSER=dummy_user
export COVAUTHKEY=dummy_key

python -m coverity_mcp_server
```

## 🚨 Troubleshooting

### Common Installation Issues

#### Python Version Compatibility
```bash
# Check Python version
python --version

# Install compatible version if needed
pyenv install 3.10.0
pyenv local 3.10.0
```

#### Missing Dependencies
```bash
# Install build dependencies
# Ubuntu/Debian:
sudo apt install build-essential python3-dev

# CentOS/RHEL:
sudo yum groupinstall "Development Tools"
sudo yum install python3-devel

# macOS:
xcode-select --install
```

#### Network Connectivity Issues
```bash
# Test connectivity
telnet your-coverity-server 8080

# Check proxy settings if needed
export HTTP_PROXY=http://proxy:8080
export HTTPS_PROXY=http://proxy:8080
```

### Getting Help

#### Support Channels
- **GitHub Issues**: https://github.com/keides2/coverity-connect-mcp/issues
- **Documentation**: See SETUP_GUIDE.md for detailed instructions
- **Discussions**: https://github.com/keides2/coverity-connect-mcp/discussions

---

**Last Updated**: July 19, 2025  
**Version**: 1.0.0