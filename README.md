# PyAirbyte MCP Server

## What is the PyAirbyte MCP Service?

The PyAirbyte Managed Code Provider (MCP) service is an AI-powered backend that generates PyAirbyte pipeline code and instructions. It leverages OpenAI and connector documentation to help users quickly scaffold and configure data pipelines between sources and destinations supported by Airbyte. The MCP service automates code generation, provides context-aware guidance, and streamlines the process of building and deploying data pipelines.

- **Generates PyAirbyte pipeline code** based on user instructions and connector documentation.
- **Uses OpenAI and file search** to provide context-aware code and instructions.
- **Available as both remote hosted service and local installation**

---

## Quick Start - Remote Server (Recommended)

### For Cursor

The easiest way to get started is using our hosted MCP server. Add this to your Cursor MCP configuration file (`.cursor/mcp.json`):

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

**Requirements:**
- Your own OpenAI API key
- No local installation required
- Works immediately after configuration

**Configuration Steps:**
1. Get your OpenAI API key from [OpenAI Platform](https://platform.openai.com/)
2. Create or edit `.cursor/mcp.json` in your project directory (for project-specific) or `~/.cursor/mcp.json` (for global access)
3. Add the configuration above with your actual OpenAI API key
4. Restart Cursor
5. Start generating PyAirbyte pipelines!

---

## Local Installation (Advanced)

### Local Server Configuration

For advanced users who prefer to run the server locally with full control. See [MCP_CONFIGURATION.md](./MCP_CONFIGURATION.md) for detailed setup instructions.

#### For Cline (VS Code Extension)

Add this configuration to your Cline MCP settings:

```json
{
  "mcpServers": {
    "pyairbyte-mcp": {
      "command": "python",
      "args": ["/path/to/airbyte-mcp/main.py"],
      "env": {
        "OPENAI_API_KEY": "your-openai-api-key-here"
      },
      "description": "PyAirbyte MCP server"
    }
  }
}
```

#### For Cursor (Local)

Add this to your Cursor MCP configuration file (`.cursor/mcp.json`):

```json
{
  "mcpServers": {
    "pyairbyte-mcp": {
      "command": "python",
      "args": ["/path/to/airbyte-mcp/main.py"],
      "env": {
        "OPENAI_API_KEY": "your-openai-api-key-here"
      },
      "description": "PyAirbyte MCP server"
    }
  }
}
```

### Local Configuration Requirements

- Requires Python and the necessary dependencies installed locally
- You must provide your own OpenAI API key via MCP environment variables
- See [MCP_CONFIGURATION.md](./MCP_CONFIGURATION.md) for complete setup instructions

### Server Environment Variables

#### MCP Configuration (Required)
- **OPENAI_API_KEY**: OpenAI API key for accessing GPT models and file search functionality

#### Optional Environment Variables
- **VECTOR_STORE_ID**: OpenAI Vector Store ID for enhanced file search capabilities
- **PORT**: Port number for the server (defaults to 8000)

### Security Note

- API keys are provided via MCP environment variables in the configuration
- This ensures secure API key handling through the MCP protocol

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
