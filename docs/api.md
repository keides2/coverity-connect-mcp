# API Documentation - Coverity Connect MCP Server

## 🎯 Overview

This document provides comprehensive API documentation for the Coverity Connect MCP Server, including all available tools, resources, and their usage patterns.

## 📋 API Schema

The Coverity Connect MCP Server implements the Model Context Protocol (MCP) specification and provides the following capabilities:

- **Tools**: 5 available tools for Coverity operations
- **Resources**: 2 available resources for configuration and data access
- **Prompts**: Built-in prompts for common workflows

## 🛠️ Available Tools

### 1. search_defects

Search for defects in Coverity Connect with advanced filtering capabilities.

#### Signature
```python
async def search_defects(
    query: str = "",
    stream_id: str = "",
    checker: str = "",
    severity: str = "",
    status: str = "",
    limit: int = 50
) -> List[Dict[str, Any]]
```

#### Parameters

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `query` | string | No | `""` | General search query for defect content |
| `stream_id` | string | No | `""` | Filter by specific stream ID |
| `checker` | string | No | `""` | Filter by checker name (e.g., "NULL_RETURNS") |
| `severity` | string | No | `""` | Filter by severity (High, Medium, Low) |
| `status` | string | No | `""` | Filter by status (New, Triaged, Fixed, etc.) |
| `limit` | integer | No | `50` | Maximum number of results to return |

#### Response Format
```json
[
  {
    "cid": "12345",
    "checkerName": "NULL_RETURNS",
    "displayType": "Null pointer dereference",
    "displayImpact": "High",
    "displayStatus": "New",
    "displayFile": "src/main.c",
    "displayFunction": "main",
    "firstDetected": "2024-01-15T10:00:00Z",
    "streamId": "main-stream"
  }
]
```

#### Usage Examples

**Basic Search:**
```
Search for defects in the main stream
```

**Filtered Search:**
```
Find all high-severity NULL_RETURNS defects that are still New
```

**Advanced Search:**
```
Show me all memory leaks in the user authentication module that haven't been fixed
```

### 2. get_defect_details

Get detailed information about a specific defect by CID (Coverity Issue Identifier).

#### Signature
```python
async def get_defect_details(cid: str) -> Dict[str, Any]
```

#### Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `cid` | string | Yes | Coverity Issue Identifier (CID) |

#### Response Format
```json
{
  "cid": "12345",
  "checkerName": "NULL_RETURNS",
  "displayType": "Null pointer dereference",
  "displayImpact": "High",
  "displayStatus": "New",
  "displayFile": "src/main.c",
  "displayFunction": "main",
  "firstDetected": "2024-01-15T10:00:00Z",
  "streamId": "main-stream",
  "occurrenceCount": 1,
  "events": [
    {
      "eventNumber": 1,
      "eventTag": "assignment",
      "eventDescription": "Null assignment detected",
      "fileName": "src/main.c",
      "lineNumber": 42
    }
  ]
}
```

### 3. list_projects

List all projects available in Coverity Connect.

#### Signature
```python
async def list_projects() -> List[Dict[str, Any]]
```

#### Parameters
None

#### Response Format
```json
[
  {
    "projectKey": "PROJ001",
    "projectName": "WebApplication",
    "description": "Main web application project",
    "dateCreated": "2024-01-15T10:30:00Z",
    "userCreated": "developer1",
    "streams": ["main", "develop", "release"]
  }
]
```

### 4. list_streams

List streams, optionally filtered by project.

#### Signature
```python
async def list_streams(project_id: str = "") -> List[Dict[str, Any]]
```

#### Parameters

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `project_id` | string | No | `""` | Optional project ID to filter streams |

#### Response Format
```json
[
  {
    "name": "main-stream",
    "description": "Main development stream",
    "projectId": "WebApplication",
    "language": "MIXED"
  }
]
```

### 5. get_project_summary

Get comprehensive summary information for a project including defect statistics.

#### Signature
```python
async def get_project_summary(project_id: str) -> Dict[str, Any]
```

#### Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `project_id` | string | Yes | Project identifier |

#### Response Format
```json
{
  "project": {
    "projectKey": "PROJ001",
    "projectName": "WebApplication",
    "description": "Main web application project",
    "dateCreated": "2024-01-15T10:30:00Z"
  },
  "streams": [
    {
      "stream_name": "main-stream",
      "total_defects": 15,
      "severity_breakdown": {
        "High": 3,
        "Medium": 8,
        "Low": 4
      },
      "status_breakdown": {
        "New": 10,
        "Triaged": 3,
        "Fixed": 2
      }
    }
  ],
  "total_streams": 3
}
```

## 📊 Available Resources

### 1. Project Configuration

Access project configuration information.

#### URI Pattern
```
coverity://projects/{project_id}/config
```

### 2. Stream Defects

Access defects for a specific stream.

#### URI Pattern
```
coverity://streams/{stream_id}/defects
```

## 🔧 Authentication

### Environment Variables

All API calls require proper authentication through environment variables:

```bash
export COVERITY_HOST="your-coverity-server.com"
export COVERITY_PORT="8080"
export COVERITY_SSL="True"
export COVAUTHUSER="your-username"
export COVAUTHKEY="your-auth-key"
```

### Error Codes

| Code | Message | Description |
|------|---------|-------------|
| 401 | Authentication failed | Invalid credentials |
| 404 | Resource not found | Invalid project/stream ID |
| 500 | Server error | Internal Coverity Connect error |
| 503 | Service unavailable | Coverity Connect unreachable |

## 🧪 Testing the API

### Using Claude Desktop

#### Basic Test
```
Test the Coverity MCP connection and list available tools
```

#### Functional Test
```
Search for high-severity defects and show me the top 5 results
```

#### Integration Test
```
Give me a complete analysis of project WebApplication including:
1. Project summary
2. Stream list
3. Top 10 high-severity defects
4. Recommendations for fixes
```

### Using Python (Development)

```python
import asyncio
from coverity_mcp_server.coverity_client import CoverityClient

async def test_api():
    client = CoverityClient(
        host="localhost",
        port=5000,
        use_ssl=False,
        username="dummy_user",
        password="dummy_key"
    )
    
    try:
        # Test all endpoints
        projects = await client.get_projects()
        print(f"Projects: {len(projects)}")
        
        streams = await client.get_streams()
        print(f"Streams: {len(streams)}")
        
        defects = await client.get_defects(limit=5)
        print(f"Defects: {len(defects)}")
        
    finally:
        await client.close()

# Run test
asyncio.run(test_api())
```

## 🔄 API Versioning

### Current Version
- **API Version**: 1.0
- **MCP Protocol**: 1.0
- **Compatibility**: Coverity Connect 2023.x+

---

**Last Updated**: July 19, 2025  
**API Version**: 1.0  
**MCP Protocol Version**: 1.0