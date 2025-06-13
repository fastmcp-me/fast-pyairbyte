# Airbyte MCP Server

This project provides an MCP server for creating data pipelines using PyAirbyte. You can create any source and destination contained in the [Airbyte Connector Catalog](https://connectors.airbyte.com/files/generated_reports/connector_registry_report.html). This is not an official Airbyte service. Use it for testing and experimentation only.

## Features

- 🚀 Generate PyAirbyte pipelines with a single command
- 🔄 Support for all Airbyte connectors
- 📝 Automatic .env file generation with required configuration
- 🔍 File search integration for context-aware pipeline generation
- 📊 Option to output to Pandas DataFrames for analysis
- 🔒 Secure credential management
- 🛠️ Easy deployment to Vercel

## Installation

The MCP service is hosted on Vercel. To add it to your IDE or AI tool, use the following configurations:

### Cursor

1. Open Cursor's settings (⌘ + ,)
2. Navigate to the MCP configuration section
3. Add the following configuration:
```json
{
  "name": "pyairbyte-mcp-server",
  "description": "Generates PyAirbyte pipelines with instructions using context from documentation.",
  "command": "curl -X POST https://your-vercel-deployment-url/api/generate-pipeline",
  "env": {
    "OPENAI_API_KEY": "your-openai-api-key"
  }
}
```

### Cline

1. Open Cline's configuration file (`~/.cline/config.yaml`)
2. Add the following MCP server configuration:
```yaml
mcp_servers:
  - name: pyairbyte-mcp-server
    description: Generates PyAirbyte pipelines with instructions using context from documentation.
    endpoint: https://your-vercel-deployment-url/api/generate-pipeline
    env:
      OPENAI_API_KEY: your-openai-api-key
```

### Claude Desktop

1. Open Claude Desktop's settings
2. Navigate to the MCP configuration section
3. Add the following configuration:
```json
{
  "servers": [
    {
      "name": "pyairbyte-mcp-server",
      "description": "Generates PyAirbyte pipelines with instructions using context from documentation.",
      "url": "https://your-vercel-deployment-url/api/generate-pipeline",
      "headers": {
        "Authorization": "Bearer your-openai-api-key"
      }
    }
  ]
}
```

## How to Use

### Basic Usage

Once installed in your IDE, all you need to do is provide a simple prompt:

```
@pyairbyte-mcp-server create pipeline from source-XX to destination-XX
```

Sources and destinations must be prefixed with either `source-` or `destination-` to match what is in the connector registry YAML definition, then substitute XX with the name of the connector you want to use. For example:

```
@pyairbyte-mcp-server create pipeline from source-postgres to destination-snowflake
```

### Example Workflows

1. **Postgres to Snowflake Pipeline**
```
@pyairbyte-mcp-server create pipeline from source-postgres to destination-snowflake
```

2. **GitHub to BigQuery Pipeline**
```
@pyairbyte-mcp-server create pipeline from source-github to destination-bigquery
```

3. **MongoDB to DataFrame Analysis**
```
@pyairbyte-mcp-server create pipeline from source-mongodb to dataframe
```

### Generated Files

The MCP server will generate two files:

1. `pyairbyte_pipeline.py` - The main pipeline script
2. `.env` - Configuration file with required credentials

Example `.env` file for Postgres to Snowflake:
```env
# Postgres Source Configuration
POSTGRES_HOST=localhost
POSTGRES_PORT=5432
POSTGRES_DATABASE=your_database
POSTGRES_USERNAME=your_username
POSTGRES_PASSWORD=your_password

# Snowflake Destination Configuration
SNOWFLAKE_HOST=your-account.snowflakecomputing.com
SNOWFLAKE_ROLE=your_role
SNOWFLAKE_WAREHOUSE=your_warehouse
SNOWFLAKE_DATABASE=your_database
SNOWFLAKE_SCHEMA=your_schema
SNOWFLAKE_USERNAME=your_username
SNOWFLAKE_PASSWORD=your_password
```

## Output to DataFrame

You can output the data to a Pandas DataFrame instead of a destination by using `dataframe` as the destination:

```
@pyairbyte-mcp-server create pipeline from source-postgres to dataframe
```

This will generate a script that:
1. Reads data from the source
2. Converts each stream to a Pandas DataFrame
3. Stores DataFrames in a dictionary for analysis
4. Includes example code for accessing and analyzing the data

## Environment Variables

The MCP server requires the following environment variables:

- `OPENAI_API_KEY`: Your OpenAI API key for file search functionality
- `VECTOR_STORE_ID`: (Optional) Vector store ID for file search functionality

### Setting Environment Variables

#### Local Development
```bash
# Linux/macOS
export OPENAI_API_KEY=your-openai-api-key
export VECTOR_STORE_ID=your-vector-store-id

# Windows (PowerShell)
$env:OPENAI_API_KEY="your-openai-api-key"
$env:VECTOR_STORE_ID="your-vector-store-id"
```

#### Vercel Deployment
1. Go to your project in the Vercel dashboard
2. Navigate to Settings > Environment Variables
3. Add the required variables

## Local Development

If you want to run the MCP server locally:

1. Clone this repository
```bash
git clone https://github.com/yourusername/airbyte-mcp.git
cd airbyte-mcp
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Set up environment variables:
```bash
export OPENAI_API_KEY=your-openai-api-key
export VECTOR_STORE_ID=your-vector-store-id  # Optional
```

4. Run the server:
```bash
python tools/pyairbyte-mcp-server.py
```

## Deployment

The server is deployed on Vercel. To deploy your own instance:

### Prerequisites

1. A [Vercel account](https://vercel.com/signup)
2. [Git](https://git-scm.com/) installed on your machine
3. [Node.js](https://nodejs.org/) (for the Vercel CLI)

### Deployment Steps

1. **Fork and Clone the Repository**
   ```bash
   # Fork the repository on GitHub first, then:
   git clone https://github.com/yourusername/airbyte-mcp.git
   cd airbyte-mcp
   ```

2. **Install Vercel CLI**
   ```bash
   npm install -g vercel
   ```

3. **Login to Vercel**
   ```bash
   vercel login
   ```

4. **Configure Environment Variables**
   Create a `.env` file in the project root:
   ```bash
   OPENAI_API_KEY=your-openai-api-key
   VECTOR_STORE_ID=your-vector-store-id  # Optional
   ```

5. **Deploy to Vercel**
   ```bash
   vercel
   ```
   
   During the deployment, Vercel will ask you some questions:
   - Set up and deploy: Yes
   - Which scope: Select your account
   - Link to existing project: No
   - Project name: airbyte-mcp (or your preferred name)
   - Directory: ./
   - Override settings: No

6. **Configure Environment Variables in Vercel**
   - Go to your project in the [Vercel Dashboard](https://vercel.com/dashboard)
   - Navigate to Settings > Environment Variables
   - Add the following variables:
     - `OPENAI_API_KEY`
     - `VECTOR_STORE_ID` (optional)

7. **Verify Deployment**
   - Vercel will provide a deployment URL (e.g., `https://your-project.vercel.app`)
   - Test the deployment by visiting the URL
   - You should see a message: "PyAirbyte MCP Server is running"

### Updating Your Deployment

To update your deployment after making changes:

1. **Commit your changes**
   ```bash
   git add .
   git commit -m "Your update message"
   git push
   ```

2. **Redeploy**
   ```bash
   vercel
   ```
   
   Or, for production deployment:
   ```bash
   vercel --prod
   ```

## Supported Connectors

The MCP server supports all connectors available in the [Airbyte Connector Registry](https://connectors.airbyte.com/files/generated_reports/connector_registry_report.html). This includes:

- All official Airbyte sources and destinations
- Community-maintained connectors
- Custom connectors that follow Airbyte's connector specification

To find the exact name of a connector to use with the MCP server:

1. Visit the [Airbyte Connector Registry](https://connectors.airbyte.com/files/generated_reports/connector_registry_report.html)
2. Find your desired connector
3. Use the connector name exactly as shown in the registry, with the appropriate prefix:
   - For sources: `source-{connector-name}`
   - For destinations: `destination-{connector-name}`

For example, if you find a connector named "postgres" in the registry:
- As a source: `source-postgres`
- As a destination: `destination-postgres`

The MCP server will automatically validate connector names against the registry and provide appropriate error messages if an invalid connector is specified.


This project is licensed under the MIT License - see the LICENSE file for details.

## Support
This project is not officially supported. It is intended for experimenting only.

# PostgreSQL to Snowflake Pipeline

This script creates a data pipeline using PyAirbyte to transfer data from PostgreSQL to Snowflake.

## Prerequisites

1. Python 3.7 or higher
2. pip (Python package installer)

## Installation

1. Create a virtual environment (recommended):
```bash
python3 -m venv venv
source venv/bin/activate  # On Windows, use: venv\Scripts\activate
```

2. Install the required packages:
```bash
pip install airbyte python-dotenv
```

## Configuration

1. Create a `.env` file in the same directory as the script with the following variables:

```env
# PostgreSQL Source Configuration
POSTGRES_HOST=your_postgres_host
POSTGRES_PORT=5432
POSTGRES_DATABASE=your_database_name
POSTGRES_USERNAME=your_username
POSTGRES_PASSWORD=your_password
POSTGRES_SSL=false

# Snowflake Destination Configuration
SNOWFLAKE_HOST=your_account.snowflakecomputing.com
SNOWFLAKE_ROLE=your_role
SNOWFLAKE_WAREHOUSE=your_warehouse
SNOWFLAKE_DATABASE=your_database
SNOWFLAKE_SCHEMA=your_schema
SNOWFLAKE_USERNAME=your_username
SNOWFLAKE_PASSWORD=your_password
```

Replace the placeholder values with your actual PostgreSQL and Snowflake credentials.

## Usage

1. Make sure your virtual environment is activated
2. Run the script:
```bash
python3 postgres_to_snowflake.py
```

The script will:
1. Connect to your PostgreSQL database
2. Verify the connection
3. Select all available streams (tables)
4. Connect to Snowflake
5. Transfer the data from PostgreSQL to Snowflake

## Error Handling

The script includes comprehensive error handling and logging. If any step fails:
- The error will be logged with details
- The script will exit with a non-zero status code
- Check the logs for specific error messages

## Customization

You can modify the script to:
- Select specific streams instead of all streams
- Add data transformation logic
- Configure additional connection parameters
- Change logging behavior

## Troubleshooting

Common issues and solutions:

1. Connection errors:
   - Verify your credentials in the `.env` file
   - Check network connectivity
   - Ensure the database servers are running

2. Permission errors:
   - Verify user permissions in both PostgreSQL and Snowflake
   - Check if the user has access to the specified databases and schemas

3. Package installation errors:
   - Make sure you're using the correct Python version
   - Try upgrading pip: `pip install --upgrade pip`
   - Install packages one by one to identify problematic dependencies

