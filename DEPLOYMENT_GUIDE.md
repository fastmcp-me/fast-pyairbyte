# PyAirbyte MCP Server - Heroku Deployment Guide

## Issues Fixed

This document outlines the issues that were identified and fixed to ensure successful Heroku deployment:

### 1. Project Structure Simplification
**Problem**: The original project had two main.py files - one in the root and one in a subdirectory, creating unnecessary complexity and import issues.

**Solution**: Consolidated everything into a single main.py file at the root level, eliminating the need for complex import path manipulation.

### 2. Procfile Configuration
**Problem**: The Procfile was configured for uvicorn with incorrect module reference.

**Solution**: Updated Procfile to use Python directly:
```
web: python main.py
```

### 3. FastMCP Transport Configuration
**Problem**: The server was configured with `transport="streamable-http"` which is not compatible with Heroku's HTTP routing.

**Solution**: Changed to standard HTTP transport:
```python
mcp.run(transport="http", host="0.0.0.0", port=port)
```

### 4. Dependencies
**Problem**: Missing uvicorn dependency that was referenced in original Procfile.

**Solution**: Removed uvicorn from requirements.txt since we're using FastMCP's built-in server.

## Deployment Checklist

### Prerequisites
- [x] Heroku CLI installed
- [x] Git repository initialized
- [x] Heroku app created

### Required Environment Variables
Set these in your Heroku app configuration:

```bash
# Required for OpenAI integration
heroku config:set OPENAI_API_KEY=your_openai_api_key_here

# Optional for file search functionality
heroku config:set VECTOR_STORE_ID=your_vector_store_id_here
```

### Deployment Steps

1. **Commit your changes:**
   ```bash
   git add .
   git commit -m "Fix deployment configuration for Heroku"
   ```

2. **Deploy to Heroku:**
   ```bash
   git push heroku main
   ```

3. **Verify deployment:**
   ```bash
   heroku logs --tail
   ```

4. **Test the endpoint:**
   ```bash
   curl https://your-app-name.herokuapp.com
   ```

## File Structure

```
/
├── main.py                          # Complete MCP server implementation
├── Procfile                         # Heroku process definition (fixed)
├── requirements.txt                 # Python dependencies (cleaned)
├── runtime.txt                      # Python version
├── README.md                        # Project documentation
├── test_deployment.py               # Local testing script
├── DEPLOYMENT_GUIDE.md             # This file
└── airbyte-connector-catalog.json  # Connector definitions
```

## Key Configuration Files

### main.py
- Complete MCP server implementation in a single file
- Proper port configuration from environment variable
- Graceful handling of missing OpenAI credentials
- Changed transport from "streamable-http" to "http"

### Procfile
- Uses `python main.py` instead of uvicorn
- Heroku automatically sets PORT environment variable

### airbyte-connector-catalog.json
- Connector definitions for source and destination configuration
- Now located at the root level for easy access

## Testing Locally

Run the test script to verify everything works:
```bash
python test_deployment.py
```

## Troubleshooting

### Common Issues

1. **Import Errors**: Ensure the path manipulation in main.py is correct
2. **Port Binding**: Heroku sets the PORT environment variable automatically
3. **OpenAI Errors**: Set OPENAI_API_KEY in Heroku config vars
4. **File Search**: VECTOR_STORE_ID is optional but recommended for full functionality

### Logs
Monitor deployment with:
```bash
heroku logs --tail --app your-app-name
```

## MCP Client Configuration

Once deployed, clients can connect using:

```json
{
  "mcpServers": {
    "pyairbyte-mcp": {
      "url": "https://your-app-name.herokuapp.com",
      "description": "Hosted PyAirbyte MCP server for generating pipelines"
    }
  }
}
```

## Security Notes

- Never commit API keys to version control
- Use Heroku config vars for sensitive information
- The server gracefully handles missing OpenAI credentials
- File search functionality is optional and fails gracefully

## Next Steps

After successful deployment:
1. Test the MCP server with a client
2. Monitor logs for any runtime issues
3. Set up monitoring/alerting if needed
4. Consider adding health check endpoints
