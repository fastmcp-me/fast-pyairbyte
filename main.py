# PyAirbyte MCP Server
import os
import json
import logging
from typing import Optional, List, Dict, Any
from fastmcp import FastMCP, Context
from openai import OpenAI, BadRequestError
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# --- Configuration ---
# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Get port from environment variable (Heroku sets this)
port = int(os.environ.get("PORT", 8000))

# --- Initialize MCP Server ---
mcp = FastMCP("pyairbyte-mcp-server")

# --- OpenAI Client ---
# No global OpenAI client - will be created per request with user-provided API key

# Get VECTOR_STORE_ID from environment variables (required for file search)
VECTOR_STORE_ID = os.environ.get("VECTOR_STORE_ID")
if VECTOR_STORE_ID:
    logging.info(f"Vector Store ID loaded from environment: {VECTOR_STORE_ID}")
else:
    logging.warning("VECTOR_STORE_ID not set in environment variables. File search will be unavailable.")

def create_openai_client(api_key: str) -> Optional[OpenAI]:
    """Create OpenAI client with provided API key."""
    try:
        client = OpenAI(api_key=api_key)
        logging.info("OpenAI client created successfully")
        return client
    except Exception as e:
        logging.error(f"Failed to create OpenAI client: {e}")
        return None

# --- MCP Configuration Handler ---
# The server now requires each client to provide their own OpenAI API key
# No global initialization - API key must be provided with each request
logging.info("Server configured to require OpenAI API key from each client request")

# --- Helper Functions ---

async def get_connector_config_from_vector_store(connector_name: str, connector_type: str, vector_store_id: str, openai_client: OpenAI) -> List[str]:
    """
    Uses vector search to find connector configuration keys from the vector store.
    
    Args:
        connector_name: The connector name (e.g., 'source-postgres', 'destination-snowflake')
        connector_type: Either 'source' or 'destination'
        vector_store_id: The OpenAI vector store ID
        openai_client: The OpenAI client instance
        
    Returns:
        List of configuration keys for the connector
    """
    if not openai_client or not vector_store_id:
        logging.error("OpenAI client or Vector Store ID not available for connector config retrieval.")
        raise Exception("Vector store configuration is required but not available.")

    # Construct a specific query for configuration details
    query = f"""
    Find the configuration schema and required fields for the Airbyte {connector_type} connector '{connector_name}'.
    
    Please provide:
    1. All required configuration fields/keys
    2. Authentication/credential fields (if any)
    3. The exact field names as they appear in the connector specification
    4. Whether any fields are nested under 'credentials' or other objects
    
    Format the response as a clear list of configuration keys that would be used as environment variables.
    """
    
    logging.info(f"Querying vector store for {connector_type} connector: {connector_name}")
    
    try:
        # Use the enhanced file search to get connector information
        search_result = await query_file_search(query, vector_store_id, openai_client)
        
        if "File search unavailable" in search_result or "Error during file search" in search_result:
            logging.error(f"Vector search failed for {connector_name}: {search_result}")
            raise Exception(f"Failed to retrieve connector configuration from vector store: {search_result}")
        
        # Parse the search result to extract configuration keys
        config_keys = parse_config_keys_from_response(search_result, connector_name)
        
        if not config_keys:
            logging.warning(f"No configuration keys found for {connector_name} in vector search result")
            # Try a more specific query
            fallback_query = f"What are the required environment variables and configuration parameters for {connector_name}?"
            fallback_result = await query_file_search(fallback_query, vector_store_id, openai_client)
            config_keys = parse_config_keys_from_response(fallback_result, connector_name)
        
        if not config_keys:
            logging.error(f"Could not extract configuration keys for {connector_name} from vector search")
            raise Exception(f"No configuration information found for connector '{connector_name}' in vector store")
        
        logging.info(f"Successfully retrieved {len(config_keys)} config keys for {connector_name}: {config_keys}")
        return config_keys
        
    except Exception as e:
        logging.error(f"Error retrieving connector config from vector store: {e}")
        raise


def parse_config_keys_from_response(response: str, connector_name: str) -> List[str]:
    """
    Parse configuration keys from the vector search response.
    
    Args:
        response: The response text from vector search
        connector_name: The connector name for context
        
    Returns:
        List of configuration keys in uppercase format suitable for environment variables
    """
    config_keys = []
    
    # Common patterns to look for in the response
    import re
    
    # Look for explicit lists of configuration keys
    key_patterns = [
        r'(?:config|configuration|field|parameter|key)(?:s)?[:\s]*["\']?([a-zA-Z_][a-zA-Z0-9_]*)["\']?',
        r'["\']([a-zA-Z_][a-zA-Z0-9_]*)["\'](?:\s*:|\s*=)',
        r'(?:required|needed|necessary)[^:]*:.*?["\']([a-zA-Z_][a-zA-Z0-9_]*)["\']',
        r'environment variable[s]?[:\s]*["\']?([A-Z_][A-Z0-9_]*)["\']?',
        r'ENV[:\s]*["\']?([A-Z_][A-Z0-9_]*)["\']?'
    ]
    
    # Common configuration field names to look for
    common_fields = [
        'host', 'port', 'database', 'username', 'password', 'api_key', 'access_token',
        'secret_key', 'client_id', 'client_secret', 'token', 'auth_token', 'bearer_token',
        'url', 'endpoint', 'server', 'schema', 'table', 'bucket', 'region', 'account',
        'tenant_id', 'subscription_id', 'project_id', 'dataset_id', 'warehouse',
        'role', 'authenticator', 'private_key', 'certificate', 'ssl_mode'
    ]
    
    # Extract potential keys using patterns
    for pattern in key_patterns:
        matches = re.findall(pattern, response, re.IGNORECASE)
        for match in matches:
            if len(match) > 1 and match.lower() in [field.lower() for field in common_fields]:
                config_keys.append(match.upper())
    
    # Look for credential-related fields that might be nested
    credential_patterns = [
        r'credential[s]?[^:]*:.*?["\']([a-zA-Z_][a-zA-Z0-9_]*)["\']',
        r'auth[^:]*:.*?["\']([a-zA-Z_][a-zA-Z0-9_]*)["\']'
    ]
    
    for pattern in credential_patterns:
        matches = re.findall(pattern, response, re.IGNORECASE)
        for match in matches:
            if len(match) > 1:
                config_keys.append(f"CREDENTIALS_{match.upper()}")
    
    # Remove duplicates and filter out very short or invalid keys
    config_keys = list(set([key for key in config_keys if len(key) > 2 and key.isalnum() or '_' in key]))
    
    # If we still don't have keys, try to extract from common connector patterns
    if not config_keys:
        # Fallback: provide common keys based on connector type
        if 'postgres' in connector_name.lower():
            config_keys = ['HOST', 'PORT', 'DATABASE', 'USERNAME', 'PASSWORD', 'SCHEMA']
        elif 'mysql' in connector_name.lower():
            config_keys = ['HOST', 'PORT', 'DATABASE', 'USERNAME', 'PASSWORD']
        elif 'snowflake' in connector_name.lower():
            config_keys = ['ACCOUNT', 'USERNAME', 'PASSWORD', 'WAREHOUSE', 'DATABASE', 'SCHEMA', 'ROLE']
        elif 'github' in connector_name.lower():
            config_keys = ['CREDENTIALS_ACCESS_TOKEN', 'REPOSITORY']
        elif 'google' in connector_name.lower():
            config_keys = ['CREDENTIALS_SERVICE_ACCOUNT_KEY', 'PROJECT_ID']
        elif 's3' in connector_name.lower():
            config_keys = ['BUCKET', 'AWS_ACCESS_KEY_ID', 'AWS_SECRET_ACCESS_KEY', 'REGION']
        else:
            # Generic fallback
            config_keys = ['API_KEY', 'HOST', 'USERNAME', 'PASSWORD']
    
    return config_keys


async def query_file_search(query: str, vector_store_id: str, openai_client: OpenAI) -> str:
    """Uses OpenAI Assistants API with file search to get context from vector store."""
    if not openai_client or not vector_store_id:
        logging.warning("OpenAI client or Vector Store ID not available. Skipping file search.")
        return "File search unavailable."

    logging.info(f"Performing file search with query: '{query}' in store '{vector_store_id}'")
    try:
        # Create an assistant with file search tool enabled
        assistant = openai_client.beta.assistants.create(
            name="PyAirbyte Connector Assistant",
            instructions="You are an expert on Airbyte connectors and PyAirbyte. Use the file search tool to find relevant information about connector configurations, authentication, and best practices.",
            model="gpt-4o",
            tools=[{"type": "file_search"}],
            tool_resources={
                "file_search": {
                    "vector_store_ids": [vector_store_id]
                }
            }
        )

        # Create a thread
        thread = openai_client.beta.threads.create()

        # Add the user's query as a message
        openai_client.beta.threads.messages.create(
            thread_id=thread.id,
            role="user",
            content=query
        )

        # Run the assistant
        run = openai_client.beta.threads.runs.create(
            thread_id=thread.id,
            assistant_id=assistant.id
        )

        # Wait for completion and get the response
        import time
        while run.status in ['queued', 'in_progress']:
            time.sleep(1)
            run = openai_client.beta.threads.runs.retrieve(
                thread_id=thread.id,
                run_id=run.id
            )

        if run.status == 'completed':
            # Get the assistant's response
            messages = openai_client.beta.threads.messages.list(
                thread_id=thread.id
            )
            
            # Get the latest assistant message
            for message in messages.data:
                if message.role == "assistant":
                    content = message.content[0].text.value
                    logging.info(f"File search response snippet: {content[:200]}...")
                    
                    # Clean up resources
                    try:
                        openai_client.beta.assistants.delete(assistant.id)
                        openai_client.beta.threads.delete(thread.id)
                    except Exception as cleanup_error:
                        logging.warning(f"Failed to cleanup resources: {cleanup_error}")
                    
                    return content if content else "No relevant information found."
        else:
            error_msg = f"Assistant run failed with status: {run.status}"
            logging.error(error_msg)
            return f"Error during file search: {error_msg}"

        return "No response from assistant."

    except BadRequestError as e:
        logging.error(f"OpenAI API Bad Request Error: {e}")
        return f"Error during file search: {e}"
    except Exception as e:
        logging.error(f"Error during OpenAI file search query: {e}")
        return f"Error during file search: {e}"

def generate_pyairbyte_code(source_name: str, destination_name: str, source_config_keys: List[str], dest_config_keys: List[str], output_to_dataframe: bool) -> str:
    """Generates the Python code for the PyAirbyte pipeline."""

    # --- Environment Variable Loading ---
    env_loading_code = """
import os
import sys
import logging
from dotenv import load_dotenv

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Load environment variables from .env file
if not load_dotenv():
    logging.warning("'.env' file not found. Please ensure it exists and contains the necessary credentials.")
    # Optionally exit if .env is strictly required
    # sys.exit("'.env' file is required. Please create it with the necessary credentials.")

# --- Helper to get env vars ---
def get_required_env(var_name: str) -> str:
    value = os.getenv(var_name)
    if value is None:
        logging.error(f"Missing required environment variable: {var_name}")
        sys.exit(f"Error: Environment variable '{var_name}' not set. Please add it to your .env file.")
    return value
"""

    # --- Source Configuration ---
    source_prefix = source_name.upper().replace("-", "_")
    source_config_vars = ",\n            ".join([f'"{key.lower()}": get_required_env("{source_prefix}_{key}")' for key in source_config_keys if not key.startswith("CREDENTIALS_")])
    source_cred_vars = ",\n                ".join([f'"{key.replace("CREDENTIALS_", "").lower()}": get_required_env("{source_prefix}_{key}")' for key in source_config_keys if key.startswith("CREDENTIALS_")])

    # Structure source config, handling nested 'credentials' if present
    source_config_dict = f"{source_config_vars}"
    if source_cred_vars:
        source_config_dict += f',\n            "credentials": {{\n                {source_cred_vars}\n            }}'

    source_code = f"""
# --- Source Configuration ---
source_name = "{source_name}"
logging.info(f"Configuring source: {{source_name}}")
source_config = {{
    {source_config_dict}
}}

# Optional: Add fixed configuration parameters here if needed
# source_config["some_other_parameter"] = "fixed_value"

try:
    source = ab.get_source(
        source_name,
        config=source_config,
        install_if_missing=True,
    )
except Exception as e:
    logging.error(f"Failed to initialize source '{{source_name}}': {{e}}")
    sys.exit(1)

# Verify the connection
logging.info("Checking source connection...")
try:
    source.check()
    logging.info("Source connection check successful.")
except Exception as e:
    logging.error(f"Source connection check failed: {{e}}")
    sys.exit(1)

# Select streams to sync (use select_all_streams() or specify)
logging.info("Selecting all streams from source.")
source.select_all_streams()
# Example for selecting specific streams:
# source.select_streams(["users", "products"])
"""

    # --- Destination Configuration / DataFrame ---
    if output_to_dataframe:
        destination_code = """
# --- Read data into Cache and then Pandas DataFrame ---
logging.info("Reading data from source into cache...")
# By default, reads into a temporary DuckDB cache
# Specify a cache explicitly: cache = ab.get_cache(config=...)
try:
    results = source.read()
    logging.info("Finished reading data.")
except Exception as e:
    logging.error(f"Failed to read data from source: {{e}}")
    sys.exit(1)

# --- Process Streams into DataFrames ---
dataframes = {}
if results.streams:
    logging.info(f"Converting {len(results.streams)} streams to Pandas DataFrames...")
    for stream_name, stream_data in results.streams.items():
        try:
            df = stream_data.to_pandas()
            dataframes[stream_name] = df
            logging.info(f"Successfully converted stream '{stream_name}' to DataFrame ({len(df)} rows).")
            # --- !! IMPORTANT !! ---
            # Add your data processing/analysis logic here!
            # Example: print(f"\\nDataFrame for stream '{stream_name}':")
            # print(df.head())
            # print("-" * 30)
        except Exception as e:
            logging.error(f"Failed to convert stream '{stream_name}' to DataFrame: {{e}}")
    logging.info("Finished processing streams.")
else:
    logging.info("No streams found in the read result.")

# Example: Access a specific dataframe
# if "users" in dataframes:
#     users_df = dataframes["users"]
#     print("\\nUsers DataFrame Head:")
#     print(users_df.head())

"""
        imports = "import airbyte as ab\nimport pandas as pd"
    else:
        dest_prefix = destination_name.upper().replace("-", "_")
        dest_config_vars = ",\n            ".join([f'"{key.lower()}": get_required_env("{dest_prefix}_{key}")' for key in dest_config_keys if not key.startswith("CREDENTIALS_")])
        dest_cred_vars = ",\n                ".join([f'"{key.replace("CREDENTIALS_", "").lower()}": get_required_env("{dest_prefix}_{key}")' for key in dest_config_keys if key.startswith("CREDENTIALS_")])

        # Structure dest config, handling nested 'credentials' if present
        dest_config_dict = f"{dest_config_vars}"
        if dest_cred_vars:
            dest_config_dict += f',\n            "credentials": {{\n                {dest_cred_vars}\n            }}'


        destination_code = f"""
# --- Destination Configuration ---
destination_name = "{destination_name}"
logging.info(f"Configuring destination: {{destination_name}}")
dest_config = {{
    {dest_config_dict}
}}

# Optional: Add fixed configuration parameters here if needed
# dest_config["some_other_parameter"] = "fixed_value"

try:
    destination = ab.get_destination(
        destination_name,
        config=dest_config,
        install_if_missing=True,
    )
except Exception as e:
    logging.error(f"Failed to initialize destination '{{destination_name}}': {{e}}")
    sys.exit(1)

# Verify the connection
logging.info("Checking destination connection...")
try:
    destination.check()
    logging.info("Destination connection check successful.")
except Exception as e:
    logging.error(f"Destination connection check failed: {{e}}")
    # Depending on the destination, a check might not be possible or fail spuriously.
    # Consider logging a warning instead of exiting for some destinations.
    # logging.warning(f"Destination connection check failed: {{e}} - Continuing cautiously.")
    sys.exit(1) # Exit for safety by default


# --- Read data and Write to Destination ---
# This reads incrementally and writes to the destination.
# Data is processed in memory or using a temporary cache if needed by the destination connector.
logging.info("Starting data read from source and write to destination...")
try:
    # source.read() returns a result object even when writing directly
    # The write() method consumes this result
    read_result = source.read() # Reads into default cache first usually
    logging.info(f"Finished reading data. Starting write to {{destination_name}}...")
    destination.write(read_result)
    logging.info("Successfully wrote data to destination.")
except Exception as e:
    logging.error(f"Failed during data read/write: {{e}}")
    sys.exit(1)

"""
        imports = "import airbyte as ab"

    # --- Main Execution Block ---
    main_block = """

# --- Main execution ---
if __name__ == "__main__":
    logging.info("Starting PyAirbyte pipeline script.")
    # The core logic is executed when the script runs directly
    # If converting to dataframe, analysis happens within the 'if output_to_dataframe:' block above.
    # If writing to destination, the write operation is the main action.
    logging.info("PyAirbyte pipeline script finished.")

"""

    # --- Combine Code Parts ---
    full_code = f"""#!/usr/bin/env python
# -*- coding: utf-8 -*-

# --- Generated by pyairbyte-mcp-server ---

{imports}
{env_loading_code}
{source_code}
{destination_code}
{main_block}
"""
    return full_code

def generate_instructions(source_name: str, destination_name: str, source_config_keys: List[str], dest_config_keys: List[str], output_to_dataframe: bool, generated_code: str, additional_context: str = "") -> str:
    """Generates the setup and usage instructions for the user."""

    # Determine dependencies based on output target
    dependencies = ["airbyte", "python-dotenv"]
    if output_to_dataframe:
        dependencies.append("pandas")
    deps_string = " ".join(dependencies)

    # Create .env content placeholders with prefixed names
    source_prefix = source_name.upper().replace("-", "_")
    env_content = "# .env file for PyAirbyte Pipeline\n\n"
    env_content += "# Source Configuration\n"
    env_content += "# Refer to Airbyte documentation for details on each key for '{}'\n".format(source_name)
    for key in source_config_keys:
        env_content += f"{source_prefix}_{key}=YOUR_{source_name.upper()}_{key}\n"

    if not output_to_dataframe:
        dest_prefix = destination_name.upper().replace("-", "_")
        env_content += "\n# Destination Configuration\n"
        env_content += "# Refer to Airbyte documentation for details on each key for '{}'\n".format(destination_name)
        for key in dest_config_keys:
            env_content += f"{dest_prefix}_{key}=YOUR_{destination_name.upper()}_{key}\n"
    else:
         env_content += "\n# No destination secrets needed when outputting to DataFrame\n"

    instructions = f"""
**PyAirbyte Pipeline Setup and Usage**

This guide helps you run the generated PyAirbyte script to move data from `{source_name}` {'to a Pandas DataFrame' if output_to_dataframe else f'to `{destination_name}`'}.

**1. Project Setup:**

   *   **Create a project directory:**
      ```bash
      mkdir pyairbyte-pipeline-project
      cd pyairbyte-pipeline-project
      ```
   *   **Initialize a virtual environment (using uv):**
      ```bash
      uv venv
      source .venv/bin/activate # On Windows use `.venv\\Scripts\\activate`
      ```
      *Note: If you don't have `uv`, install it: `pip install uv`*

**2. Install Dependencies:**

   *   Install the required Python libraries:
      ```bash
      uv pip install {deps_string}
      ```

**3. Create the Python Script:**

   *   Save the following code into a file named `pyairbyte_pipeline.py` in your project directory:

      ```python
      {generated_code}
      ```

**4. Configure Credentials (.env file):**

   *   Create a file named `.env` in the **same directory** as your `pyairbyte_pipeline.py` script.
   *   Paste the following content into the `.env` file and **replace the placeholder values** with your actual credentials and configuration details.
   *   **IMPORTANT:** Never commit your `.env` file to version control (add it to your `.gitignore`).

      ```dotenv
      {env_content}
      ```
   *   Refer to the official Airbyte documentation for `{source_name}` {('and `' + destination_name + '`') if not output_to_dataframe else ''} to understand what values are needed for each key.

**5. Run the Pipeline:**

   *   Execute the script from your terminal (make sure your virtual environment is active):
      ```bash
      python pyairbyte_pipeline.py
      ```
   *   The script will:
      *   Load credentials from your `.env` file.
      *   Install the necessary Airbyte connector(s) if they aren't already installed in the environment.
      *   Check connections to the source {('and destination' if not output_to_dataframe else '')}.
      *   Read data from `{source_name}`.
      *   {'Convert the data streams into Pandas DataFrames (you can add your analysis code in the script where indicated).' if output_to_dataframe else f'Write the data to `{destination_name}`.'}

**Next Steps:**

   *   {'Modify the `pyairbyte_pipeline.py` script to add your data processing or analysis logic using the Pandas DataFrames.' if output_to_dataframe else f'Verify the data in your `{destination_name}` destination.'}
   *   Explore PyAirbyte documentation for more advanced features like stream selection, caching options, and error handling: [https://docs.airbyte.com/using-airbyte/pyairbyte/](https://docs.airbyte.com/using-airbyte/pyairbyte/)
"""
    return instructions

# --- MCP Configuration Handler ---
# Note: FastMCP doesn't have a configure decorator, so we rely on environment variables
# The OpenAI client is initialized from environment variables at startup

# --- MCP Tool Definition ---
@mcp.tool()
async def generate_pyairbyte_pipeline(
    source_name: str,
    destination_name: str,
    ctx: Context # MCP Context object
    ) -> Dict[str, Any]:
    """
    Generates a PyAirbyte Python script and setup instructions for a given source and destination.

    Args:
        source_name: The official Airbyte source connector name (e.g., 'source-postgres', 'source-github').
        destination_name: The official Airbyte destination connector name (e.g., 'destination-postgres', 'destination-snowflake') OR 'dataframe' to output to Pandas DataFrames.
        ctx: The MCP Context object (automatically provided).
    """
    logging.info(f"Received request to generate pipeline for Source: {source_name}, Destination: {destination_name}")
    await ctx.info(f"Generating PyAirbyte pipeline: {source_name} -> {destination_name}") # Send status to Cursor UI

    # Get OpenAI API key from MCP configuration only
    openai_api_key = os.environ.get("OPENAI_API_KEY")

    if not openai_api_key:
        error_msg = "OPENAI_API_KEY not found. Please configure it in your MCP settings environment variables."
        logging.error(error_msg)
        await ctx.error(error_msg)
        return {
            "message": f"Error: {error_msg}",
            "instructions": error_msg
        }

    # Create OpenAI client with API key
    openai_client = create_openai_client(openai_api_key)
    if not openai_client:
        error_msg = "Failed to initialize OpenAI client with provided API key. Please check your API key."
        logging.error(error_msg)
        await ctx.error(error_msg)
        return {
            "message": f"Error: {error_msg}",
            "instructions": error_msg
        }

    output_to_dataframe = destination_name.lower() == "dataframe"

    # Check if vector store is available
    if not VECTOR_STORE_ID:
        error_msg = "VECTOR_STORE_ID not configured. Vector store is required for connector configuration retrieval."
        logging.error(error_msg)
        await ctx.error(error_msg)
        return {
            "message": f"Error: {error_msg}",
            "instructions": error_msg
        }

    # --- Get Config Keys from Vector Store ---
    try:
        await ctx.info("Retrieving source connector configuration from vector store...")
        source_config_keys = await get_connector_config_from_vector_store(
            source_name, "source", VECTOR_STORE_ID, openai_client
        )
        
        dest_config_keys = []
        if not output_to_dataframe:
            await ctx.info("Retrieving destination connector configuration from vector store...")
            dest_config_keys = await get_connector_config_from_vector_store(
                destination_name, "destination", VECTOR_STORE_ID, openai_client
            )
            
    except Exception as e:
        error_msg = f"Failed to retrieve connector configuration from vector store: {e}"
        logging.error(error_msg)
        await ctx.error(error_msg)
        return {
            "message": f"Error: {error_msg}",
            "instructions": error_msg
        }

    # --- Use Vector Search for Additional Context ---
    try:
        await ctx.info("Gathering additional context and best practices from vector store...")
        context_query = f"""
        Provide best practices, common configuration patterns, and important notes for:
        - Source connector: {source_name}
        {f'- Destination connector: {destination_name}' if not output_to_dataframe else ''}
        
        Include any special authentication requirements, common pitfalls, or configuration tips.
        """
        additional_context = await query_file_search(context_query, VECTOR_STORE_ID, openai_client)
        logging.info(f"Retrieved additional context: {additional_context[:200]}...")
        
    except Exception as e:
        logging.warning(f"Failed to retrieve additional context: {e}")
        additional_context = "No additional context available."

    # --- Generate Code ---
    try:
        generated_code = generate_pyairbyte_code(source_name, destination_name, source_config_keys, dest_config_keys, output_to_dataframe)
    except Exception as e:
        error_msg = f"An internal error occurred during code generation: {e}"
        logging.error(f"Error during code generation: {e}")
        await ctx.error(f"Failed to generate Python code: {e}")
        return {
            "message": f"Error: {error_msg}",
            "instructions": error_msg
        }


    # --- Generate Instructions ---
    try:
        instructions = generate_instructions(source_name, destination_name, source_config_keys, dest_config_keys, output_to_dataframe, generated_code, additional_context)
    except Exception as e:
        error_msg = f"An internal error occurred during instruction generation: {e}"
        logging.error(f"Error during instruction generation: {e}")
        await ctx.error(f"Failed to generate instructions: {e}")
        return {
            "message": f"Error: {error_msg}",
            "instructions": error_msg
        }


    logging.info("Successfully generated pipeline code and instructions.")
    await ctx.info("Pipeline generation complete.")

    # --- Return Result ---
    # Return as a structured dictionary or a single markdown string
    return {
        "message": f"Successfully generated PyAirbyte pipeline instructions and code for {source_name} -> {destination_name}.",
        "instructions": instructions,
        # "code": generated_code # Code is already included within instructions markdown
    }


# --- Run the server ---
if __name__ == "__main__":
    logging.info("Starting PyAirbyte MCP Server...")
    # Use FastMCP's built-in streamable HTTP transport for web deployment
    mcp.run(
        transport="streamable-http",
        host="0.0.0.0",
        port=port
    )
