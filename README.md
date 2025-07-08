# Fast PyAirbyte

## One click install

[<img src="https://cursor.com/deeplink/mcp-install-dark.png" alt="Add fast-pyairbyte MCP server to Cursor" width="200">](cursor://anysphere.cursor-deeplink/mcp/install?name=fast-pyairbyte&config=eyJjb21tYW5kIjoibnB4IiwiYXJncyI6WyJmYXN0LXB5YWlyYnl0ZSJdLCJlbnYiOnsiT1BFTkFJX0FQSV9LRVkiOiJ5b3VyLW9wZW5haS1hcGkta2V5LWhlcmUifX0=)

Click the button above to automatically add Fast PyAirbyte to your Cursor IDE, or install manually using the instructions below.

### Manual Installation

The easiest way to get started is using npx to run the MCP server directly:

```bash
npx fast-pyairbyte
```

This will:
1. Download and install the package automatically
2. Check for Python and install dependencies
3. Start the MCP server locally
4. Display configuration instructions

---

## What is Fast PyAirbyte?

Fast PyAirbyte is an AI-powered tool that generates PyAirbyte pipeline code and instructions. It leverages OpenAI and connector documentation to help users quickly scaffold and configure data pipelines between sources and destinations supported by Airbyte. The MCP server automates code generation, provides context-aware guidance, and streamlines the process of building and deploying data pipelines.

- **Generates PyAirbyte pipeline code** based on user instructions and connector documentation
- **Uses OpenAI and file search** to provide context-aware code and instructions  
- **Available as an npm package** that can be executed via npx
- **Easy installation** with no local setup required

---

## MCP Configuration

Add this to your MCP configuration file:

**For Cursor (`.cursor/mcp.json`):**
```json
{
  "mcpServers": {
    "fast-pyairbyte": {
      "command": "npx",
      "args": ["fast-pyairbyte"],
      "env": {
        "OPENAI_API_KEY": "your-openai-api-key-here"
      }
    }
  }
}
```

**For Claude Desktop (`~/.config/claude/claude_desktop_config.json`):**
```json
{
  "mcpServers": {
    "fast-pyairbyte": {
      "command": "npx",
      "args": ["fast-pyairbyte"],
      "env": {
        "OPENAI_API_KEY": "your-openai-api-key-here"
      }
    }
  }
}
```

**For Cline (`~/.config/cline/mcp_settings.json`):**
```json
{
  "mcpServers": {
    "fast-pyairbyte": {
      "command": "npx",
      "args": ["fast-pyairbyte"],
      "env": {
        "OPENAI_API_KEY": "your-openai-api-key-here"
      }
    }
  }
}
```

**Requirements:**
- Your own OpenAI API key from [OpenAI Platform](https://platform.openai.com/)
- Python 3.7+ installed on your system
- Node.js 14+ for npx execution

**Configuration Steps:**
1. Get your OpenAI API key from [OpenAI Platform](https://platform.openai.com/)
2. Create or edit your MCP configuration file
3. Add the configuration above with your actual OpenAI API key
4. Restart your MCP client (Cursor/Claude/Cline)
5. Start generating PyAirbyte pipelines!

---

## Usage

Once configured, you can use the MCP server in your AI assistant by asking it to generate PyAirbyte pipelines.

### 🚀 How to Use

#### 1. Verify Connection
- Look for the MCP server status in your client's interface
- You should see "fast-pyairbyte" listed with 1 tool available
- If it shows 0 tools or is red, check your configuration

#### 2. Generate Pipelines with Natural Language
Simply ask your AI assistant to generate a PyAirbyte pipeline! Here are example prompts:

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

#### 3. Available Source/Destination Options
- **Sources**: Any Airbyte source connector (e.g., `source-postgres`, `source-github`, `source-stripe`, `source-mysql`, `source-salesforce`)
- **Destinations**: Any Airbyte destination connector (e.g., `destination-snowflake`, `destination-bigquery`, `destination-postgres`) OR `dataframe` for Pandas analysis

#### 4. Pro Tips
- **Use "dataframe"** as destination if you want to analyze data in Python/Pandas
- **Be specific** about your source and destination names (use official Airbyte connector names with `source-` or `destination-` prefixes)
- **Ask follow-up questions** if you need help with specific configuration or setup

The tool will automatically use your OpenAI API key (configured in the MCP settings) to generate enhanced, well-documented pipeline code with best practices and detailed setup instructions!

---

## Features

- **Automated Code Generation**: Creates complete PyAirbyte pipeline scripts
- **Configuration Management**: Handles environment variables and credentials securely
- **Documentation Integration**: Uses OpenAI to provide context-aware instructions
- **Multiple Output Formats**: Supports both destination connectors and DataFrame output
- **Best Practices**: Includes error handling, logging, and proper project structure
- **600+ Connectors**: If it's in the [Airbyte Connector Registry](https://connectors.airbyte.com/files/generated_reports/connector_registry_report.html), the MCP server can create pipelines for it
- **Easy Installation**: No local setup required - just use npx
- **Cross-Platform**: Works on macOS, Linux, and Windows

---

## Available Tools

### fast_pyairbyte

Creates a complete data pipeline using PyAirbyte and fast-pyairbyte to extract, transform, and load data between sources and destinations.

**Parameters:**
- `source_name`: The official Airbyte source connector name (e.g., 'source-postgres', 'source-github')
- `destination_name`: The official Airbyte destination connector name (e.g., 'destination-postgres', 'destination-snowflake') OR 'dataframe' to output to Pandas DataFrames

**Returns:**
- Complete Python pipeline code
- Setup and installation instructions
- Environment variable templates
- Best practices and usage guidelines

---

## Development

### Local Development

If you want to contribute or modify the server:

1. **Clone the repository:**
   ```bash
   git clone https://github.com/quintonwall/fast-pyairbyte.git
   cd fast-pyairbyte
   ```

2. **Install dependencies:**
   ```bash
   npm install
   ```

3. **Test locally:**
   ```bash
   npm start
   ```

### Project Structure

```
fast-pyairbyte/
├── package.json              # npm package configuration
├── bin/
│   └── fast-pyairbyte.js     # Node.js launcher script
├── python/
│   ├── main.py               # Python MCP server
│   ├── telemetry.py          # Usage analytics
│   └── requirements.txt      # Python dependencies
├── README.md                 # This file
└── docs/                     # Documentation
```

### Publishing

To publish a new version to npm:

```bash
npm version patch  # or minor/major
npm config set strict-ssl false
npm publish
```

---

## Security & Privacy

- **API Key Security**: OpenAI API keys are passed securely through MCP environment variables
- **No Data Storage**: The server doesn't store any user data or credentials
- **Anonymous Telemetry**: Basic usage analytics are collected (can be disabled with `DO_NOT_TRACK=1`)
- **Open Source**: Full source code is available for inspection

---

## Troubleshooting

### Common Issues

1. **"Python not found" error**
   - Install Python 3.7+ from [python.org](https://python.org)
   - Ensure Python is in your system PATH

2. **"Dependencies failed to install" error**
   - Check your internet connection
   - Try running `pip install --upgrade pip` first

3. **"OpenAI API key not found" error**
   - Verify your API key is correctly set in the MCP configuration
   - Check that you're using a valid OpenAI API key

4. **MCP server shows 0 tools**
   - Check the MCP configuration file syntax
   - Restart your MCP client after configuration changes
   - Check the server logs for error messages

### Getting Help

- **Issues**: Report bugs on [GitHub Issues](https://github.com/quintonwall/pyairbyte-mcp-npx/issues)
- **Discussions**: Join the conversation on [GitHub Discussions](https://github.com/quintonwall/pyairbyte-mcp-npx/discussions)
- **Slack**: Ask questions in the [Airbyte Slack](https://airbytehq.slack.com/archives/C091PCA614N)

---

## License

MIT License - see [LICENSE](LICENSE) file for details.

---

## Contributing

Contributions are welcome! Please read our contributing guidelines and submit pull requests to help improve the PyAirbyte MCP Server.
