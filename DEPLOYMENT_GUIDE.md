# PyAirbyte MCP Server - Local Development Guide

## Overview

This document outlines how to set up and run the PyAirbyte MCP Server locally. The server now requires local MCP configuration only and does not support remote deployment.

## Local Development Setup

### Prerequisites
- Python 3.8 or higher
- pip or uv for package management
- OpenAI API key

### Installation Steps

1. **Clone the repository:**
   ```bash
   git clone <repository-url>
   cd airbyte-mcp
   ```

2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```
   
   Or using uv:
   ```bash
   uv pip install -r requirements.txt
   ```

3. **Configure MCP settings:**
   Add the server configuration to your MCP client settings (see [MCP_CONFIGURATION.md](./MCP_CONFIGURATION.md))

## File Structure

```
/
├── main.py                          # Complete MCP server implementation
├── requirements.txt                 # Python dependencies
├── README.md                        # Project documentation
├── MCP_CONFIGURATION.md             # MCP configuration guide
├── DEPLOYMENT_GUIDE.md             # This file
└── airbyte-connector-catalog.json  # Connector definitions
```

## Key Configuration Files

### main.py
- Complete MCP server implementation in a single file
- Requires OpenAI API key from MCP environment variables
- Graceful handling of missing OpenAI credentials
- Uses FastMCP for MCP protocol handling

### requirements.txt
- Python dependencies required for the server
- Includes openai, python-dotenv, and fastmcp

### airbyte-connector-catalog.json
- Connector definitions for source and destination configuration
- Used to determine configuration keys for different connectors

## Testing Locally

1. **Configure your MCP client** with the server settings (see MCP_CONFIGURATION.md)

2. **Start your MCP client** (Cline, Cursor, etc.)

3. **Verify the server is running** by checking the MCP client interface for available tools

4. **Test the tool** by asking your AI assistant to generate a PyAirbyte pipeline

## Troubleshooting

### Common Issues

1. **Import Errors**: Ensure all dependencies are installed correctly
2. **OpenAI Errors**: Verify your OPENAI_API_KEY is set in MCP configuration
3. **File Search**: VECTOR_STORE_ID is optional but recommended for full functionality
4. **Path Issues**: Ensure the path in MCP configuration points to the correct main.py location

### Debugging

Check the MCP client logs for error messages:
- Look for connection errors
- Verify the OpenAI client initialization
- Check for missing dependencies

## Security Notes

- Never commit API keys to version control
- Keep your OpenAI API key secure and rotate it regularly
- The API key is only used for generating PyAirbyte pipeline code
- File search functionality is optional and fails gracefully

## Next Steps

After successful setup:
1. Test the MCP server with your client
2. Generate some PyAirbyte pipelines to verify functionality
3. Explore the generated code and instructions
4. Customize the server for your specific needs if required
