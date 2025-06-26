# PyAirbyte MCP Server

## What is the PyAirbyte MCP Service?

The PyAirbyte Managed Code Provider (MCP) service is an AI-powered backend that generates PyAirbyte pipeline code and instructions. It leverages OpenAI and connector documentation to help users quickly scaffold and configure data pipelines between sources and destinations supported by Airbyte. The MCP service automates code generation, provides context-aware guidance, and streamlines the process of building and deploying data pipelines. If you want to learn more on how the service works check out [this video.](https://www.youtube.com/watch?v=t-o8YIfqA_g) 

- **Generates PyAirbyte pipeline code** based on user instructions and connector documentation.
- **Uses OpenAI and file search** to provide context-aware code and instructions.
- **Available as a remote MCP server** for Cursor.

---

## Quick Start

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
4. turn off / on the MCP server
5. Start generating PyAirbyte pipelines!

---

### Security Note

- API keys are provided via MCP environment variables in the configuration
- This ensures secure API key handling through the MCP protocol
- Cursor is currently the only client that appears to support passing in ENV for remote servers. We will add Cline support as soon as available.

---

## Usage

Once configured, you can use the MCP server in your AI assistant by asking it to generate PyAirbyte pipelines.

### 🚀 How to Use in Cline

#### 1. Verify Connection
- Look for the MCP server status in Cline's interface
- You should see "pyairbyte-mcp" listed with 1 tool available
- If it shows 0 tools or is red, check your mcp.json. If you need more help, please ask in [this slack channel.](https://airbytehq.slack.com/archives/C091PCA614N) 

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

```
Generate a data pipeline from source-salesforce to destination-postgres
```

```
Create a pipeline that reads from source-github to a dataframe, and then visualize the results using Streamlit
```

```
Help me set up a data pipeline from source-salesforce to destination-postgres
```



#### 4. Available Source/Destination Options
- **Sources**: Any Airbyte source connector (e.g., `source-postgres`, `source-github`, `source-stripe`, `source-mysql`, `source-salesforce`)
- **Destinations**: Any Airbyte destination connector (e.g., `destination-snowflake`, `destination-bigquery`, `destination-postgres`) OR `dataframe` for Pandas analysis

#### 5. Pro Tips
- **Use "dataframe"** as destination if you want to analyze data in Python/Pandas
- **Be specific** about your source and destination names (use official Airbyte connector names and use source- or destination- to specify)
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
- **Generate pipeline for over 600 connectors**: If it is in the [Airbyte Connector Registry](https://connectors.airbyte.com/files/generated_reports/connector_registry_report.html), the MCP server can create it. 

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

