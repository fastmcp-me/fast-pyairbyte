# MCP Configuration Guide

This guide explains how to configure the PyAirbyte MCP Server. Both local and remote servers now require you to provide your own OpenAI API key when using the tools.

## Configuration File Location

The MCP configuration file is typically located at:
- **Cline/Claude Dev Extension**: `/Users/quintonwall/Library/Application Support/Code/User/globalStorage/saoudrizwan.claude-dev/settings/cline_mcp_settings.json`
- **Claude Desktop App**: `~/Library/Application Support/Claude/claude_desktop_config.json`

## Configuration Format

The configuration approach differs between remote/hosted and local servers:

### For Remote/Hosted Server:
```json
{
  "mcpServers": {
    "pyairbyte-mcp": {
      "url": "https://pyairbyte-mcp-7b7b8566f2ce.herokuapp.com/mcp"
    }
  }
}
```
*Note: No environment variables needed in MCP configuration. You provide your OpenAI API key when calling the tool.*

### For Local Server:
```json
{
  "mcpServers": {
    "pyairbyte-mcp-server": {
      "command": "python",
      "args": ["/Users/quintonwall/code/airbyte-mcp/main.py"],
      "env": {
        "OPENAI_API_KEY": "your-openai-api-key-here"
      }
    }
  }
}
```

## Environment Variables

### MCP Configuration (Required for local servers only)
- `OPENAI_API_KEY`: Your OpenAI API key for accessing GPT models and file search functionality

### .env File (Optional, local server only)
- `VECTOR_STORE_ID`: OpenAI Vector Store ID for file search capabilities (if you have uploaded PyAirbyte documentation)
- `PORT`: Port number for the server (defaults to 8000, mainly used for Heroku deployment)

### Remote/Hosted Server Usage
- No MCP environment variables required
- Provide your OpenAI API key when calling the `generate_pyairbyte_pipeline` tool
- Example: `generate_pyairbyte_pipeline(source_name="source-postgres", destination_name="destination-snowflake", openai_api_key="sk-proj-your-key-here")`

## Getting Your OpenAI API Key

1. Go to [OpenAI Platform](https://platform.openai.com/)
2. Sign in to your account or create a new one
3. Navigate to the API Keys section
4. Create a new API key
5. Copy the key and add it to your MCP configuration

## Example Complete Configuration

Here's an example of a complete MCP settings file with the PyAirbyte server configured:

```json
{
  "mcpServers": {
    "pyairbyte-mcp-server": {
      "command": "python",
      "args": ["/Users/quintonwall/code/airbyte-mcp/main.py"],
      "env": {
        "OPENAI_API_KEY": "sk-proj-abc123..."
      }
    },
    "other-server": {
      "command": "node",
      "args": ["/path/to/other/server.js"]
    }
  }
}
```

## Verification

After updating your MCP configuration:

1. Restart your Cline/Claude application
2. The server should automatically connect and initialize with your OpenAI API key
3. Check the server logs for confirmation that the OpenAI client was initialized successfully
4. You should see the `generate_pyairbyte_pipeline` tool available in your MCP tools

## Security Notes

- Never commit your API keys to version control
- Keep your OpenAI API key secure and rotate it regularly
- Monitor your OpenAI usage to avoid unexpected charges
- The API key is only used for generating PyAirbyte pipeline code and documentation search

## Troubleshooting

If the server fails to start:

1. **Check the file path**: Ensure the path in `args` points to the correct location of `main.py`
2. **Verify Python installation**: Make sure Python is available in your PATH
3. **Check dependencies**: Ensure required packages are installed (`pip install openai python-dotenv fastmcp`)
4. **Validate API key**: Test your OpenAI API key with a simple API call
5. **Check logs**: Look for error messages in the MCP server logs

## Migration from .env File

If you were previously using a `.env` file for configuration, you can now remove the `OPENAI_API_KEY` from the `.env` file and configure it through the MCP settings instead. The server will still fall back to environment variables if the MCP configuration doesn't provide the API key.
