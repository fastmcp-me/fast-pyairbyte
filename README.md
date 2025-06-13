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

There are two ways to use this MCP server:

### Option 1: Hosted Server (Recommended for most users)

Connect to the hosted server on Heroku - no local setup required.

#### For Cline (VS Code Extension)

Add this configuration to your Cline MCP settings:

```json
{
  "mcpServers": {
    "pyairbyte-mcp": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-fetch", "https://pyairbyte-mcp-7b7b8566f2ce.herokuapp.com/mcp"],
      "description": "Hosted PyAirbyte MCP server for generating pipelines"
    }
  }
}
```

#### For Cursor

Add this to your Cursor MCP configuration file (`.cursor/mcp.json`):

```json
{
  "mcpServers": {
    "pyairbyte-mcp": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-fetch", "https://pyairbyte-mcp-7b7b8566f2ce.herokuapp.com/mcp"],
      "description": "Hosted PyAirbyte MCP server for generating PyAirbyte pipelines"
    }
  }
}
```

### Option 2: Local Server (For development or custom configurations)

Run the server locally with your own OpenAI API key. See [MCP_CONFIGURATION.md](./MCP_CONFIGURATION.md) for detailed setup instructions.

#### For Cline (VS Code Extension)

Add this configuration to your Cline MCP settings:

```json
{
  "mcpServers": {
    "pyairbyte-mcp-local": {
      "command": "python",
      "args": ["/path/to/airbyte-mcp/main.py"],
      "env": {
        "OPENAI_API_KEY": "your-openai-api-key-here"
      },
      "description": "Local PyAirbyte MCP server"
    }
  }
}
```

#### For Cursor

Add this to your Cursor MCP configuration file (`.cursor/mcp.json`):

```json
{
  "mcpServers": {
    "pyairbyte-mcp-local": {
      "command": "python",
      "args": ["/path/to/airbyte-mcp/main.py"],
      "env": {
        "OPENAI_API_KEY": "your-openai-api-key-here"
      },
      "description": "Local PyAirbyte MCP server"
    }
  }
}
```

### Configuration Notes

#### Hosted Server
- The server uses Server-Sent Events (SSE) for communication via the `/mcp` endpoint
- The `@modelcontextprotocol/server-fetch` package handles the HTTP-to-MCP protocol translation
- No additional configuration parameters are needed as the server uses environment variables
- The OpenAI API key is securely configured as an environment variable on the server

#### Local Server
- Requires Python and the necessary dependencies installed locally
- You must provide your own OpenAI API key via MCP environment variables
- See [MCP_CONFIGURATION.md](./MCP_CONFIGURATION.md) for complete setup instructions
- Allows for custom configurations and development

### Server Environment Variables

The server uses environment variables from two sources:

#### MCP Configuration (Required for local server)
- **OPENAI_API_KEY**: OpenAI API key for accessing GPT models and file search functionality

#### .env File (Optional)
- **VECTOR_STORE_ID**: OpenAI Vector Store ID for enhanced file search capabilities
- **PORT**: Port number for the server (defaults to 8000, mainly used for Heroku deployment)

### Security Note

When using the hosted server, the OpenAI API key is securely configured as an environment variable on the server, so no sensitive information needs to be included in your client configuration. For local deployments, only the OpenAI API key needs to be passed via MCP configuration, while other optional settings can be configured in a .env file.

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

## Local Development

For local development and testing:

1. Clone this repository
2. Install dependencies: `pip install -r requirements.txt`
3. Set up your environment variables (see [MCP_CONFIGURATION.md](./MCP_CONFIGURATION.md))
4. Run the server: `python main.py`
5. Configure your MCP client to connect to the local server

---

## Deployment

This MCP server is deployed on Heroku and ready to use. The configuration separates concerns:

- **Client Configuration**: Uses the standard MCP fetch protocol via npx
- **Server Environment**: All sensitive configuration is set as environment variables on the server

This approach ensures no sensitive information needs to be shared in client configurations, while the server handles all authentication and external service integration securely.
