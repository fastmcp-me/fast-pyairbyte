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

Connect to the hosted server on Heroku. You'll provide your OpenAI API key when calling the tool.

#### For Cline (VS Code Extension)

Add this configuration to your Cline MCP settings:

```json
{
  "mcpServers": {
    "pyairbyte-mcp": {
      "url": "https://pyairbyte-mcp-7b7b8566f2ce.herokuapp.com/mcp",
      "disabled": false,
      "autoApprove": [],
      "timeout": 30
    }
  }
}
```

**Important for Cline**: Create a `.env` file in your project directory with your OpenAI API key:
```
OPENAI_API_KEY=your-openai-api-key-here
```

*Note: Cline's MCP settings schema doesn't support the `env` field for remote servers. The server will automatically use the OPENAI_API_KEY from your local .env file.*

#### For Cursor

Add this to your Cursor MCP configuration file (`.cursor/mcp.json`):

```json
{
  "mcpServers": {
    "pyairbyte-mcp": {
      "url": "https://pyairbyte-mcp-7b7b8566f2ce.herokuapp.com/mcp",
      "env": {
        "OPENAI_API_KEY": "your-openai-api-key-here"
      }
    }
  }
}
```

*Note: Cursor supports the `env` field for passing environment variables to remote servers.*

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
- **Cline**: Uses a local `.env` file for the OpenAI API key (MCP settings schema doesn't support `env` field for remote servers)
- **Cursor**: Supports passing OpenAI API key via `env` field in MCP configuration
- The server uses Server-Sent Events (SSE) for communication via the `/mcp` endpoint
- Uses the standard MCP fetch protocol via npx

#### Local Server
- Requires Python and the necessary dependencies installed locally
- You must provide your own OpenAI API key via MCP environment variables
- See [MCP_CONFIGURATION.md](./MCP_CONFIGURATION.md) for complete setup instructions
- Allows for custom configurations and development

### Server Environment Variables

The server uses environment variables from multiple sources:

#### MCP Configuration (Required for local servers, supported by Cursor for remote servers)
- **OPENAI_API_KEY**: OpenAI API key for accessing GPT models and file search functionality

#### .env File (Required for Cline with remote server, optional for local servers)
- **OPENAI_API_KEY**: OpenAI API key (required for Cline when using remote server)
- **VECTOR_STORE_ID**: OpenAI Vector Store ID for enhanced file search capabilities
- **PORT**: Port number for the server (defaults to 8000, mainly used for Heroku deployment)

### Security Note

- **Cline**: Uses local `.env` file for API key when connecting to remote server
- **Cursor**: Can pass API key via MCP configuration for remote servers
- **Local servers**: Use MCP environment variables for API key configuration
- This approach ensures secure API key handling while accommodating different client capabilities

---

## Usage

Once configured, you can use the MCP server in your AI assistant by asking it to generate PyAirbyte pipelines.

### 🚀 How to Use in Cline

#### 1. Verify Connection
- Look for the MCP server status in Cline's interface
- You should see "pyairbyte-mcp" listed with 1 tool available
- If it shows 0 tools or is red, restart Cline

#### 2. Generate Pipelines with Natural Language
Simply ask Cline to generate a PyAirbyte pipeline! Here are example prompts:

**Basic Examples:**
```
Generate a PyAirbyte pipeline from source-postgres to destination-snowflake
```

```
Create a pipeline to move data from source-github to dataframe
```

```
Build a PyAirbyte script for source-stripe to destination-bigquery
```

**More Detailed Examples:**
```
I need to sync data from a PostgreSQL database to Snowflake. Can you generate the PyAirbyte code for me?
```

```
Create a pipeline that reads from GitHub API and outputs to Pandas DataFrames for analysis
```

```
Generate PyAirbyte code to move Stripe payment data to BigQuery with proper error handling
```

```
Help me set up a data pipeline from Salesforce to a local PostgreSQL database
```

#### 3. What Cline Will Do
When you ask for a pipeline, Cline will:
1. **Automatically call the MCP tool** with your source and destination
2. **Generate complete Python code** for your pipeline
3. **Provide setup instructions** including:
   - Virtual environment setup
   - Dependency installation
   - Configuration file creation
   - Environment variable setup
   - Step-by-step usage guide

#### 4. Available Source/Destination Options
- **Sources**: Any Airbyte source connector (e.g., `source-postgres`, `source-github`, `source-stripe`, `source-mysql`, `source-salesforce`)
- **Destinations**: Any Airbyte destination connector (e.g., `destination-snowflake`, `destination-bigquery`, `destination-postgres`) OR `dataframe` for Pandas analysis

#### 5. Pro Tips
- **Use "dataframe"** as destination if you want to analyze data in Python/Pandas
- **Be specific** about your source and destination names (use official Airbyte connector names)
- **Ask follow-up questions** if you need help with specific configuration or setup

The tool will automatically use your OpenAI API key (configured in the MCP settings) to generate enhanced, well-documented pipeline code with best practices and detailed setup instructions!

Just start by asking Cline to generate a pipeline for your specific use case! 🎯

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
