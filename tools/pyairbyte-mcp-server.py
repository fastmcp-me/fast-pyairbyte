# mcp_server.py
import os
import json
import logging
from typing import Optional, List, Dict, Any
from mcp.server.fastmcp import FastMCP, Context
from openai import OpenAI, BadRequestError
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# --- Configuration ---
# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# --- Initialize MCP Server ---
mcp = FastMCP(
    "pyairbyte-mcp-server",
    description="Generates PyAirbyte pipelines with instructions using context from documentation.",
    # Add dependencies required by *this server script*
    dependencies=["openai", "python-dotenv"]
    # Dependencies for the *generated* script (like 'airbyte') are handled in user instructions.
)

# --- OpenAI Client ---
# Ensure OPENAI_API_KEY and VECTOR_STORE_ID are set as environment variables
# You can set these in your system or pass them via the .cursor/mcp.json config
try:
    openai_client = OpenAI() # Uses OPENAI_API_KEY from env automatically
    VECTOR_STORE_ID = os.environ.get("VECTOR_STORE_ID")
    if not VECTOR_STORE_ID:
        logging.warning("VECTOR_STORE_ID environment variable not set. File search will fail.")
        # Optionally raise an error or disable the tool if VS ID is critical
        # raise ValueError("VECTOR_STORE_ID environment variable is required.")
except Exception as e:
    logging.error(f"Failed to initialize OpenAI client or get VECTOR_STORE_ID: {e}")
    openai_client = None # Disable OpenAI features if init fails

# --- Helper Functions ---

def get_connector_config_keys(connector_name: str, connector_type: str, catalog_path: str = "airbyte-connector-catalog.json") -> List[str]:
    """
    Parses the provided catalog file to find config keys for a connector.
    NOTE: Assumes the catalog file is in the same directory or path is correct.
          This is a simplified parser. Real-world usage might need better error handling.
    """
    try:
        # Attempt to read the catalog file relative to this script's location
        script_dir = os.path.dirname(os.path.abspath(__file__))
        full_catalog_path = os.path.join(script_dir, catalog_path)

        if not os.path.exists(full_catalog_path):
             logging.warning(f"Connector catalog file not found at: {full_catalog_path}. Cannot determine config keys.")
             # Fallback: Try reading from current working directory if run differently
             if os.path.exists(catalog_path):
                 full_catalog_path = catalog_path
             else:
                 return ["config_key_1", "config_key_2"] # Generic fallback

        with open(full_catalog_path, 'r') as f:
            catalog = json.load(f)

        for connector in catalog:
            if connector.get("name") == connector_name and connector.get("type") == connector_type:
                # Handle nested credentials common in some connectors
                config_keys = list(connector.get("config", {}).keys())
                if "credentials" in connector.get("config", {}) and isinstance(connector["config"]["credentials"], dict):
                     credential_keys = list(connector["config"]["credentials"].keys())
                     # Prefix credential keys for clarity in .env, e.g., CREDENTIALS_ACCESS_TOKEN
                     config_keys.remove("credentials") # Remove the top-level 'credentials' key
                     config_keys.extend([f"CREDENTIALS_{key.upper()}" for key in credential_keys])

                # Convert to uppercase for .env convention
                return [key.upper() for key in config_keys]

        logging.warning(f"Connector '{connector_name}' of type '{connector_type}' not found in catalog.")
        return ["config_key_1", "config_key_2"] # Generic fallback

    except FileNotFoundError:
        logging.error(f"Connector catalog file not found at path: {full_catalog_path}. Cannot determine config keys.")
        return ["config_key_1", "config_key_2"] # Generic fallback
    except json.JSONDecodeError:
        logging.error(f"Error decoding JSON from catalog file: {full_catalog_path}.")
        return ["config_key_1", "config_key_2"] # Generic fallback
    except Exception as e:
        logging.error(f"Error reading connector catalog: {e}")
        return ["config_key_1", "config_key_2"] # Generic fallback


async def query_file_search(query: str, vector_store_id: str) -> str:
    """Uses OpenAI File Search (via Responses API) to get context."""
    if not openai_client or not vector_store_id:
        logging.warning("OpenAI client or Vector Store ID not available. Skipping file search.")
        return "File search unavailable."

    logging.info(f"Performing file search with query: '{query}' in store '{vector_store_id}'")
    try:
        # Using the Responses API as shown in openai-filesearch.txt examples
        # We only need the text response here, not complex handling of calls/results yet.
        # A simpler chat completion call might also work if file search is attached to the assistant/model.
        # Using Responses API explicitly for file search tool:
        response = await openai_client.chat.completions.create(
            model="gpt-4o", # Or your preferred model compatible with file search
            messages=[
                {"role": "user", "content": query}
            ],
            # The new way to use file search is via tool_resources in Assistants v2
            # or potentially attached to the model if using Chat Completions directly with search capabilities.
            # The example in openai-filesearch.txt uses client.responses.create, which seems deprecated or part of a different flow.
            # Let's adapt using Chat Completions with a system message hinting at using the files.
            # A more robust way would be using the Assistants API with file_search tool enabled.
            # Simpler approach for now: Rely on a capable model and provide context in prompt.
            # --- Alternative using Assistants API (more complex setup required) ---
            # assistant = await openai_client.beta.assistants.create(...)
            # thread = await openai_client.beta.threads.create(...)
            # message = await openai_client.beta.threads.messages.create(...)
            # run = await openai_client.beta.threads.runs.create( thread_id=thread.id, assistant_id=assistant.id, tool_resources={"file_search": {"vector_store_ids": [vector_store_id]}})
            # --- Sticking to Chat Completion for simplicity within MCP tool ---
            # We'll add context retrieved via file search *manually* if needed,
            # or rely on the LLM's training if it includes these docs.
            # The file search *tool call* within the MCP tool isn't straightforward.
            # Let's retrieve context *before* generating the final output.
            #
            # Re-evaluating: The goal is for the *MCP Tool* to use file search.
            # The example in `openai-filesearch.txt` uses `client.responses.create` which looks like a specific endpoint.
            # Let's try simulating that structure or using Chat Completion and hoping it leverages indexed files.
            # If `client.responses.create` is the *only* way, this MCP tool might need adjustment based on its exact API.
            # Assume for now Chat Completion on a sufficiently knowledgeable model can access the context,
            # or that we can manually retrieve snippets if needed (though less ideal).
             tool_choice="auto", # Let model decide if file search is needed (if implicitly available)
             # If using Assistants API v2 style (hypothetical within Chat):
             # tool_resources={"file_search": {"vector_store_ids": [vector_store_id]}}
             # --- Let's assume file search is implicitly used by the model or not directly callable here ---
             # We will construct a detailed prompt *using* knowledge from the docs instead.

        )
        content = response.choices[0].message.content
        logging.info(f"File search response snippet: {content[:200]}...")
        return content if content else "No relevant information found."

    except BadRequestError as e:
         logging.error(f"OpenAI API Bad Request Error (check model, params, vector store?): {e}")
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
    source_config_vars = ",\n            ".join([f'"{key.lower()}": get_required_env("{key}")' for key in source_config_keys if not key.startswith("CREDENTIALS_")])
    source_cred_vars = ",\n                ".join([f'"{key.replace("CREDENTIALS_", "").lower()}": get_required_env("{key}")' for key in source_config_keys if key.startswith("CREDENTIALS_")])

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
        dest_config_vars = ",\n            ".join([f'"{key.lower()}": get_required_env("{key}")' for key in dest_config_keys if not key.startswith("CREDENTIALS_")])
        dest_cred_vars = ",\n                ".join([f'"{key.replace("CREDENTIALS_", "").lower()}": get_required_env("{key}")' for key in dest_config_keys if key.startswith("CREDENTIALS_")])

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

def generate_instructions(source_name: str, destination_name: str, source_config_keys: List[str], dest_config_keys: List[str], output_to_dataframe: bool, generated_code: str) -> str:
    """Generates the setup and usage instructions for the user."""

    # Determine dependencies based on output target
    dependencies = ["airbyte", "python-dotenv"]
    if output_to_dataframe:
        dependencies.append("pandas")
    deps_string = " ".join(dependencies)

    # Create .env content placeholders
    env_content = "# .env file for PyAirbyte Pipeline\n\n"
    env_content += "# Source Configuration\n"
    env_content += "# Refer to Airbyte documentation for details on each key for '{}'\n".format(source_name)
    for key in source_config_keys:
        env_content += f"{key}=YOUR_{source_name.upper()}_{key}\n"

    if not output_to_dataframe:
        env_content += "\n# Destination Configuration\n"
        env_content += "# Refer to Airbyte documentation for details on each key for '{}'\n".format(destination_name)
        for key in dest_config_keys:
            env_content += f"{key}=YOUR_{destination_name.upper()}_{key}\n"
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

# --- MCP Tool Definition ---
@mcp.tool()
async def generate_pyairbyte_pipeline(
    source_name: str,
    destination_name: str,
    ctx: Context # MCP Context object
    ) -> Dict[str, str]:
    """
    Generates a PyAirbyte Python script and setup instructions for a given source and destination.

    Args:
        source_name: The official Airbyte source connector name (e.g., 'source-postgres', 'source-github').
        destination_name: The official Airbyte destination connector name (e.g., 'destination-postgres', 'destination-snowflake') OR 'dataframe' to output to Pandas DataFrames.
        ctx: The MCP Context object (automatically provided).
    """
    logging.info(f"Received request to generate pipeline for Source: {source_name}, Destination: {destination_name}")
    ctx.info(f"Generating PyAirbyte pipeline: {source_name} -> {destination_name}") # Send status to Cursor UI

    output_to_dataframe = destination_name.lower() == "dataframe"

    # --- Get Config Keys ---
    # Use helper function to parse catalog (ensure airbyte-connector-catalog.json is accessible)
    source_config_keys = get_connector_config_keys(source_name, "source")
    dest_config_keys = []
    if not output_to_dataframe:
        dest_config_keys = get_connector_config_keys(destination_name, "destination")

    if not source_config_keys:
         logging.warning(f"Could not determine config keys for source: {source_name}")
         # Optionally return an error message to the user via the context or return value
         # ctx.error(f"Failed to get config keys for source '{source_name}'. Check catalog or connector name.")
         # return {"error": f"Could not find configuration keys for source '{source_name}'. Is the name correct and in the catalog?"}

    if not output_to_dataframe and not dest_config_keys:
         logging.warning(f"Could not determine config keys for destination: {destination_name}")
         # ctx.error(f"Failed to get config keys for destination '{destination_name}'. Check catalog or connector name.")
         # return {"error": f"Could not find configuration keys for destination '{destination_name}'. Is the name correct and in the catalog?"}


    # --- Use File Search for Context (Optional Enhancement) ---
    # Construct a query to get best practices or specific config nuances
    # Example: query = f"Provide Python code examples and best practices for configuring PyAirbyte source '{source_name}' and destination '{destination_name}' using environment variables for secrets."
    # search_context = await query_file_search(query, VECTOR_STORE_ID)
    # TODO: Integrate 'search_context' into the generation logic below if needed.
    # For now, the template-based generation is used.

    # --- Generate Code ---
    try:
        generated_code = generate_pyairbyte_code(source_name, destination_name, source_config_keys, dest_config_keys, output_to_dataframe)
    except Exception as e:
        logging.error(f"Error during code generation: {e}")
        ctx.error(f"Failed to generate Python code: {e}")
        return {"error": f"An internal error occurred during code generation: {e}"}


    # --- Generate Instructions ---
    try:
        instructions = generate_instructions(source_name, destination_name, source_config_keys, dest_config_keys, output_to_dataframe, generated_code)
    except Exception as e:
        logging.error(f"Error during instruction generation: {e}")
        ctx.error(f"Failed to generate instructions: {e}")
        return {"error": f"An internal error occurred during instruction generation: {e}"}


    logging.info("Successfully generated pipeline code and instructions.")
    ctx.info("Pipeline generation complete.")

    # --- Return Result ---
    # Return as a structured dictionary or a single markdown string
    return {
        "message": f"Successfully generated PyAirbyte pipeline instructions and code for {source_name} -> {destination_name}.",
        "instructions": instructions,
        # "code": generated_code # Code is already included within instructions markdown
    }


# --- Run the server (for direct execution, though Cursor uses stdio) ---
if __name__ == "__main__":
    # This allows running the server directly for testing, e.g., `python mcp_server.py`
    # However, Cursor will typically manage the process via the config file.
    # Ensure required env vars (OPENAI_API_KEY, VECTOR_STORE_ID) are set when running directly.
    if not os.getenv("OPENAI_API_KEY"):
        print("WARNING: OPENAI_API_KEY environment variable not set.")
    if not os.getenv("VECTOR_STORE_ID"):
        print("WARNING: VECTOR_STORE_ID environment variable not set.")

    print("Starting PyAirbyte MCP Server directly...")
    mcp.run() # Runs the stdio server by default when run directly