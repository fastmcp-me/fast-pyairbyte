# PyAirbyte MCP Server

## What is the PyAirbyte MCP Service?

The PyAirbyte Managed Code Provider (MCP) service is an AI-powered backend that generates PyAirbyte pipeline code and instructions. It leverages OpenAI and connector documentation to help users quickly scaffold and configure data pipelines between sources and destinations supported by Airbyte. The MCP service automates code generation, provides context-aware guidance, and streamlines the process of building and deploying data pipelines.

- **Generates PyAirbyte pipeline code** based on user instructions and connector documentation.
- **Uses OpenAI and file search** to provide context-aware code and instructions.
- **Supports secure, environment-based configuration** for flexible deployments.

The MCP server is deployed and accessible at:

**https://pyairbyte-mcp-7b7b8566f2ce.herokuapp.com**

---

## MCP Client Configuration

Below are example configuration files for connecting to this MCP server from different clients.

### For Cline (VS Code Extension)

Add this configuration to your Cline MCP settings:

```json
{
  "mcpServers": {
    "pyairbyte-mcp": {
      "url": "https://pyairbyte-mcp-7b7b8566f2ce.herokuapp.com",
      "description": "Hosted PyAirbyte MCP server for generating pipelines",
      "config": {
        "openai_api_key": "your-openai-api-key-here"
      }
    }
  }
}
```

### For Cursor

Add this to your Cursor MCP configuration file (`.cursor/mcp.json`):

```json
{
  "mcpServers": {
    "pyairbyte-mcp": {
      "url": "https://pyairbyte-mcp-7b7b8566f2ce.herokuapp.com",
      "description": "Hosted PyAirbyte MCP server for generating PyAirbyte pipelines",
      "config": {
        "openai_api_key": "your-openai-api-key-here"
      }
    }
  }
}
```

### Configuration Parameters

- **openai_api_key** (required): Your OpenAI API key for generating enhanced pipeline code and instructions

### Server Environment Variables

The server requires the following environment variable to be set on Heroku:

- **VECTOR_STORE_ID** (optional): OpenAI Vector Store ID for enhanced file search capabilities

### Security Note

Replace `"your-openai-api-key-here"` with your actual OpenAI API key. The API key is securely transmitted to the server and used only for generating pipeline code and documentation.

---

## Usage

Once configured, you can use the MCP server in your AI assistant by asking it to generate PyAirbyte pipelines. For example:

- "Generate a PyAirbyte pipeline from PostgreSQL to Snowflake"
- "Create a pipeline that reads from GitHub and outputs to a DataFrame"
- "Help me set up a data pipeline from Salesforce to BigQuery"

The server will generate complete Python code with setup instructions, environment variable templates, and best practices for your specific source and destination combination.

---

## Features

- **Automated Code Generation**: Creates complete PyAirbyte pipeline scripts
- **Configuration Management**: Handles environment variables and credentials securely
- **Documentation Integration**: Uses OpenAI to provide context-aware instructions
- **Multiple Output Formats**: Supports both destination connectors and DataFrame output
- **Best Practices**: Includes error handling, logging, and proper project structure

---

## Available Tools

### generate_pyairbyte_pipeline

Generates a complete PyAirbyte pipeline with setup instructions.

**Parameters:**
- `source_name`: The official Airbyte source connector name (e.g., 'source-postgres', 'source-github')
- `destination_name`: The official Airbyte destination connector name (e.g., 'destination-postgres', 'destination-snowflake') OR 'dataframe' to output to Pandas DataFrames

**Returns:**
- Complete Python pipeline code
- Setup and installation instructions
- Environment variable templates
- Best practices and usage guidelines

---

## Deployment

This MCP server is deployed on Heroku and ready to use. The configuration separates concerns:

- **Client Configuration**: Only requires your OpenAI API key
- **Server Environment**: Vector Store ID is set as an environment variable on the server

This approach ensures your OpenAI API key is only shared with the MCP server when needed, while server-specific configuration remains on the deployment platform.
