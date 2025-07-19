# Configuration Reference - Coverity Connect MCP Server

## 🎯 Overview

This guide provides comprehensive configuration options for the Coverity Connect MCP Server, including environment variables, configuration files, and advanced settings.

## 📋 Configuration Methods

The server supports multiple configuration methods, listed in order of precedence:

1. **Command Line Arguments** (highest priority)
2. **Environment Variables**
3. **Configuration Files**
4. **Default Values** (lowest priority)

## 🔧 Environment Variables

### Core Coverity Settings

#### COVERITY_HOST
- **Description**: Coverity Connect server hostname or IP address
- **Type**: String
- **Required**: Yes
- **Default**: None
- **Examples**: 
  - `coverity.company.com`
  - `192.168.1.100`
  - `localhost` (for development)

```bash
export COVERITY_HOST="coverity.company.com"
```

#### COVERITY_PORT
- **Description**: Coverity Connect server port
- **Type**: Integer
- **Required**: No
- **Default**: `8080`
- **Common Values**: `8080`, `443`, `8443`

```bash
export COVERITY_PORT="8080"
```

#### COVERITY_SSL
- **Description**: Enable SSL/TLS connection
- **Type**: Boolean (True/False)
- **Required**: No
- **Default**: `True`
- **Notes**: Set to `False` only for development/testing

```bash
export COVERITY_SSL="True"      # Production
export COVERITY_SSL="False"     # Development
```

### Authentication Settings

#### COVAUTHUSER
- **Description**: Coverity Connect username
- **Type**: String
- **Required**: Yes
- **Security**: Store securely, never in code

```bash
export COVAUTHUSER="your-username"
```

#### COVAUTHKEY
- **Description**: Coverity Connect authentication key or password
- **Type**: String
- **Required**: Yes
- **Security**: Highly sensitive - store in secure vault

```bash
export COVAUTHKEY="your-auth-key-here"
```

### MCP Server Settings

#### MCP_DEBUG
- **Description**: Enable MCP debug mode
- **Type**: Boolean (True/False)
- **Required**: No
- **Default**: `False`

```bash
export MCP_DEBUG="True"         # Development
export MCP_DEBUG="False"        # Production
```

#### LOG_LEVEL
- **Description**: Logging verbosity level
- **Type**: String
- **Required**: No
- **Default**: `INFO`
- **Values**: `DEBUG`, `INFO`, `WARNING`, `ERROR`, `CRITICAL`

```bash
export LOG_LEVEL="DEBUG"        # Development
export LOG_LEVEL="INFO"         # Production
export LOG_LEVEL="WARNING"      # Minimal logging
```

## 📄 Configuration Files

### .env File Format

Create `.env` file in the project root:

```bash
# Coverity Connect Settings
COVERITY_HOST=coverity.company.com
COVERITY_PORT=8080
COVERITY_SSL=True
COVAUTHUSER=your-username
COVAUTHKEY=your-auth-key

# MCP Settings
MCP_DEBUG=False
LOG_LEVEL=INFO

# Performance
TIMEOUT_SECONDS=30
MAX_CONNECTIONS=10
```

### Environment-Specific Files

#### Development (.env.development)
```bash
# Development Environment
COVERITY_HOST=localhost
COVERITY_PORT=5000
COVERITY_SSL=False
COVAUTHUSER=dummy_user
COVAUTHKEY=dummy_key
MCP_DEBUG=True
LOG_LEVEL=DEBUG
```

#### Production (.env.production)
```bash
# Production Environment
COVERITY_HOST=coverity.company.com
COVERITY_PORT=8080
COVERITY_SSL=True
COVAUTHUSER=${VAULT_USER}
COVAUTHKEY=${VAULT_KEY}
MCP_DEBUG=False
LOG_LEVEL=INFO
SSL_VERIFY=True
TIMEOUT_SECONDS=60
```

## ⚙️ Claude Desktop Configuration

### Basic Configuration
```json
{
  "mcpServers": {
    "coverity-connect": {
      "command": "python",
      "args": ["-m", "coverity_mcp_server"],
      "cwd": "/path/to/coverity-connect-mcp",
      "env": {
        "COVERITY_HOST": "coverity.company.com",
        "COVERITY_PORT": "8080",
        "COVERITY_SSL": "True",
        "COVAUTHUSER": "your-username",
        "COVAUTHKEY": "your-auth-key"
      }
    }
  }
}
```

### Advanced Configuration
```json
{
  "mcpServers": {
    "coverity-connect": {
      "command": "python",
      "args": ["-m", "coverity_mcp_server"],
      "cwd": "/path/to/coverity-connect-mcp",
      "env": {
        "COVERITY_HOST": "coverity.company.com",
        "COVERITY_PORT": "8080",
        "COVERITY_SSL": "True",
        "COVAUTHUSER": "your-username",
        "COVAUTHKEY": "your-auth-key",
        "LOG_LEVEL": "INFO",
        "TIMEOUT_SECONDS": "60",
        "MAX_CONNECTIONS": "5"
      }
    }
  }
}
```

## 🔐 Security Configuration

### Secure Credential Storage

#### Using Environment Variables (Basic)
```bash
# Store in secure location
echo 'export COVAUTHKEY="your-key"' >> ~/.bashrc_secrets
chmod 600 ~/.bashrc_secrets
source ~/.bashrc_secrets
```

#### Using Vault (Recommended)
```bash
# Store in HashiCorp Vault
vault kv put secret/coverity-mcp \
  username=your-user \
  authkey=your-key

# Retrieve in application
export COVAUTHUSER=$(vault kv get -field=username secret/coverity-mcp)
export COVAUTHKEY=$(vault kv get -field=authkey secret/coverity-mcp)
```

## ⚠️ Configuration Validation

### Required Settings Check
```bash
# Validation script
python -c "
import os
required = ['COVERITY_HOST', 'COVAUTHUSER', 'COVAUTHKEY']
missing = [var for var in required if not os.getenv(var)]
if missing:
    print(f'❌ Missing required variables: {missing}')
    exit(1)
else:
    print('✅ All required variables set')
"
```

### Configuration Test
```bash
# Test configuration
python -c "
from coverity_mcp_server.config import get_config
try:
    config = get_config()
    print('✅ Configuration loaded successfully')
    print(f'Host: {config.host}')
    print(f'Port: {config.port}')
    print(f'SSL: {config.use_ssl}')
except Exception as e:
    print(f'❌ Configuration error: {e}')
"
```

## 🔧 Troubleshooting Configuration

### Common Issues

#### Authentication Failures
```bash
# Check credentials
echo "User: $COVAUTHUSER"
echo "Key length: ${#COVAUTHKEY}"

# Test authentication
curl -u "$COVAUTHUSER:$COVAUTHKEY" \
  "https://$COVERITY_HOST:$COVERITY_PORT/ws/v9/configurationservice?wsdl"
```

#### SSL Certificate Issues
```bash
# Check certificate
openssl s_client -connect $COVERITY_HOST:$COVERITY_PORT -showcerts

# Bypass SSL (temporary, insecure)
export SSL_VERIFY=False
```

#### Network Connectivity
```bash
# Test network connectivity
telnet $COVERITY_HOST $COVERITY_PORT

# Check proxy settings
export HTTP_PROXY=http://proxy:8080
export HTTPS_PROXY=http://proxy:8080
```

## 📚 Additional Resources

### Configuration Examples
- **Development**: `examples/development/.env.development`
- **Production**: `examples/production/.env.production`
- **Setup Guide**: `SETUP_GUIDE.md`

### Related Documentation
- **Installation Guide**: `docs/installation.md`
- **API Reference**: `docs/api.md`

---

**Last Updated**: July 19, 2025  
**Version**: 1.0.0