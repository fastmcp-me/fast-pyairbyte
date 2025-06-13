import os
import uvicorn
from fastmcp.server import FastMCP

def main():
    print("Starting PyAirbyte MCP Server directly...")
    server = FastMCP()
    
    # Get port from Heroku environment variable, default to 8000 for local development
    port = int(os.environ.get("PORT", 8000))
    
    # Run the server with host 0.0.0.0 to allow external connections
    uvicorn.run(
        server.app,
        host="0.0.0.0",
        port=port,
        log_level="info"
    )

if __name__ == "__main__":
    main() 