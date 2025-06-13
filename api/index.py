import os
import json
import logging
from typing import Optional, List, Dict, Any
from mcp_core.server.fastmcp import FastMCP, Context
from openai import OpenAI, BadRequestError
from dotenv import load_dotenv
import sys
from pathlib import Path

# Add the tools directory to the Python path
sys.path.append(str(Path(__file__).parent.parent))

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Initialize MCP Server
mcp = FastMCP(
    "pyairbyte-mcp-server",
    description="Generates PyAirbyte pipelines with instructions using context from documentation.",
    dependencies=["openai", "python-dotenv"]
)

# Initialize OpenAI client
try:
    openai_client = OpenAI()
    VECTOR_STORE_ID = os.environ.get("VECTOR_STORE_ID")
    if not VECTOR_STORE_ID:
        logging.warning("VECTOR_STORE_ID environment variable not set. File search will fail.")
except Exception as e:
    logging.error(f"Failed to initialize OpenAI client or get VECTOR_STORE_ID: {e}")
    openai_client = None

# Import the helper functions from the original server
from tools.pyairbyte_mcp_server import (
    get_connector_config_keys,
    query_file_search,
    generate_pyairbyte_code,
    generate_instructions
)

# Import the MCP server from the tools directory
from tools.pyairbyte_mcp_server import mcp

@mcp.tool()
async def generate_pyairbyte_pipeline(
    source_name: str,
    destination_name: str,
    ctx: Context
) -> Dict[str, str]:
    """Generate a PyAirbyte pipeline from source to destination."""
    try:
        # Get config keys for source and destination
        source_config_keys = get_connector_config_keys(source_name, "source")
        dest_config_keys = get_connector_config_keys(destination_name, "destination")
        
        # Generate the pipeline code
        generated_code = generate_pyairbyte_code(
            source_name,
            destination_name,
            source_config_keys,
            dest_config_keys,
            output_to_dataframe=False
        )
        
        # Generate instructions
        instructions = generate_instructions(
            source_name,
            destination_name,
            source_config_keys,
            dest_config_keys,
            output_to_dataframe=False,
            generated_code=generated_code
        )
        
        return {
            "code": generated_code,
            "instructions": instructions
        }
        
    except Exception as e:
        logging.error(f"Error generating pipeline: {e}")
        raise

# Export the MCP app for Vercel
app = mcp.app

@app.get("/")
async def root():
    return {"message": "PyAirbyte MCP Server is running"} 