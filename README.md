# PyAirbyte MCP Server

## What is the PyAirbyte MCP Service?

The PyAirbyte Managed Code Provider (MCP) service is an AI-powered backend that generates PyAirbyte pipeline code and instructions. It leverages OpenAI and connector documentation to help users quickly scaffold and configure data pipelines between sources and destinations supported by Airbyte. The MCP service automates code generation, provides context-aware guidance, and streamlines the process of building and deploying data pipelines.

- **Generates PyAirbyte pipeline code** based on user instructions and connector documentation.
- **Uses OpenAI and file search** to provide context-aware code and instructions.
- **Supports secure, environment-based configuration** for flexible deployments.

The MCP server is deployed and accessible at:

**https://pyairbyte-mcp-7b7b8566f2ce.herokuapp.com**

---

## Example `mcp.json` Files for Clients

Below are example `mcp.json` configuration files for connecting to this MCP server from different clients.


```json
{
  "mcpServers": {
    "pyairbyte-mcp": {
      "url": "https://pyairbyte-mcp-7b7b8566f2ce.herokuapp.com",
      "description": "Hosted PyAirbyte MCP server for generating pipelines from PostgreSQL to Snowflake and more."
    }
  }
}
```
