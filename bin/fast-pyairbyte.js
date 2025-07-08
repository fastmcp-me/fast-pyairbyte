#!/usr/bin/env node

const { spawn } = require('child_process');
const path = require('path');
const fs = require('fs');
const os = require('os');

// Configuration
const PYTHON_DIR = path.join(__dirname, '..', 'python');
const MAIN_PY = path.join(PYTHON_DIR, 'main.py');
const REQUIREMENTS_TXT = path.join(PYTHON_DIR, 'requirements-minimal.txt');

// Hard-coded VECTOR_STORE_ID (as requested by user)
const VECTOR_STORE_ID = 'vs_67e6e08d2474819190173cbb80bed014';

console.error('🐙 Starting Fast PyAirbyte...');

// Function to check if Python is available
async function checkPython() {
    // Common Python installation paths
    const pythonPaths = [
        'python3',
        'python',
        '/opt/homebrew/bin/python3',
        '/usr/local/bin/python3',
        '/usr/bin/python3',
        '/opt/homebrew/bin/python',
        '/usr/local/bin/python',
        '/usr/bin/python'
    ];
    
    for (const cmd of pythonPaths) {
        try {
            console.error(`🔍 Checking: ${cmd}`);
            
            const result = await new Promise((resolve) => {
                const proc = spawn(cmd, ['--version'], { stdio: 'pipe' });
                
                proc.on('close', (code) => {
                    console.error(`   ${cmd}: exit code ${code}`);
                    resolve(code === 0 ? cmd : null);
                });
                
                proc.on('error', (err) => {
                    console.error(`   ${cmd}: error - ${err.message}`);
                    resolve(null);
                });
                
                // Add timeout to prevent hanging
                setTimeout(() => {
                    proc.kill();
                    console.error(`   ${cmd}: timeout`);
                    resolve(null);
                }, 5000);
            });
            
            if (result) {
                console.error(`✅ Found working Python: ${result}`);
                return result;
            }
        } catch (error) {
            console.error(`   ${cmd}: exception - ${error.message}`);
        }
    }
    
    return null;
}

// Function to create virtual environment and install dependencies
function setupVirtualEnvironment(pythonCmd) {
    return new Promise((resolve, reject) => {
        const venvPath = path.join(__dirname, '..', 'venv');
        
        console.error('🔧 Creating virtual environment...');
        
        // Create virtual environment
        const venvProc = spawn(pythonCmd, ['-m', 'venv', venvPath], {
            stdio: 'inherit'
        });
        
        venvProc.on('close', (code) => {
            if (code === 0) {
                console.error('✅ Virtual environment created successfully');
                
                // Determine the path to the virtual environment's Python
                const venvPython = os.platform() === 'win32' 
                    ? path.join(venvPath, 'Scripts', 'python.exe')
                    : path.join(venvPath, 'bin', 'python');
                
                console.error('📦 Installing Python dependencies in virtual environment...');
                
                // Install dependencies in virtual environment
                const installProc = spawn(venvPython, ['-m', 'pip', 'install', '-r', REQUIREMENTS_TXT], {
                    stdio: ['inherit', 'pipe', 'inherit']  // stdin: inherit, stdout: pipe, stderr: inherit
                });
                
                // Redirect pip stdout to stderr to avoid JSON parsing issues
                installProc.stdout.on('data', (data) => {
                    process.stderr.write(data);
                });
                
                installProc.on('close', (installCode) => {
                    if (installCode === 0) {
                        console.error('✅ Dependencies installed successfully in virtual environment');
                        resolve(venvPython);
                    } else {
                        reject(new Error(`Failed to install dependencies. Exit code: ${installCode}`));
                    }
                });
                
                installProc.on('error', (err) => {
                    reject(new Error(`Failed to install dependencies: ${err.message}`));
                });
                
            } else {
                reject(new Error(`Failed to create virtual environment. Exit code: ${code}`));
            }
        });
        
        venvProc.on('error', (err) => {
            reject(new Error(`Failed to create virtual environment: ${err.message}`));
        });
    });
}

// Function to start the MCP server
function startMCPServer(pythonCmd) {
    console.error('🔧 Starting MCP server...');
    
    // Set up environment variables
    const env = {
        ...process.env,
        VECTOR_STORE_ID: VECTOR_STORE_ID,
        PORT: process.env.PORT || '8000'
    };
    
    // Start the Python MCP server
    const proc = spawn(pythonCmd, [MAIN_PY], {
        stdio: 'inherit',
        env: env
    });
    
    proc.on('close', (code) => {
        console.error(`\n🛑 MCP server stopped with exit code: ${code}`);
        process.exit(code);
    });
    
    proc.on('error', (err) => {
        console.error(`❌ Failed to start MCP server: ${err.message}`);
        process.exit(1);
    });
    
    // Handle graceful shutdown
    process.on('SIGINT', () => {
        console.error('\n🛑 Shutting down MCP server...');
        proc.kill('SIGINT');
    });
    
    process.on('SIGTERM', () => {
        console.error('\n🛑 Shutting down MCP server...');
        proc.kill('SIGTERM');
    });
    
    return proc;
}

// Function to display usage instructions
function displayInstructions() {
    console.error(`
📋 MCP Server Configuration Instructions:

Add this to your MCP configuration file:

For Cursor (.cursor/mcp.json):
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

For Claude Desktop (~/.config/claude/claude_desktop_config.json):
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

⚠️  Important: Replace "your-openai-api-key-here" with your actual OpenAI API key.

The server will be available at: http://localhost:${process.env.PORT || '8000'}
`);
}

// Main execution
async function main() {
    try {
        // Check if required files exist
        if (!fs.existsSync(MAIN_PY)) {
            throw new Error(`Python main file not found: ${MAIN_PY}`);
        }
        
        if (!fs.existsSync(REQUIREMENTS_TXT)) {
            throw new Error(`Requirements file not found: ${REQUIREMENTS_TXT}`);
        }
        
        // Check Python availability
        console.error('🔍 Checking Python installation...');
        const pythonCmd = await checkPython();
        
        if (!pythonCmd) {
            throw new Error('Python is not installed or not available in PATH. Please install Python 3.7+ and try again.');
        }
        
        console.error(`✅ Found Python: ${pythonCmd}`);
        
        // Check if virtual environment already exists
        const venvPath = path.join(__dirname, '..', 'venv');
        const venvPython = os.platform() === 'win32' 
            ? path.join(venvPath, 'Scripts', 'python.exe')
            : path.join(venvPath, 'bin', 'python');
        
        let finalPythonCmd;
        
        if (fs.existsSync(venvPython)) {
            console.error('✅ Virtual environment already exists, using it');
            finalPythonCmd = venvPython;
        } else {
            // Setup virtual environment and install dependencies
            finalPythonCmd = await setupVirtualEnvironment(pythonCmd);
        }
        
        // Display configuration instructions
        displayInstructions();
        
        // Start the MCP server
        startMCPServer(finalPythonCmd);
        
    } catch (error) {
        console.error(`❌ Error: ${error.message}`);
        process.exit(1);
    }
}

// Run the main function
main();
