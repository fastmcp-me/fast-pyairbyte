#!/usr/bin/env python3
"""
Test script to verify the MCP server can be imported and started correctly.
Run this locally before deploying to Heroku.
"""

import sys
import os

def test_import():
    """Test that the main module can be imported correctly."""
    try:
        from main import mcp
        print("✅ Successfully imported MCP server")
        return True
    except ImportError as e:
        print(f"❌ Import error: {e}")
        return False
    except Exception as e:
        print(f"❌ Unexpected error during import: {e}")
        return False

def test_dependencies():
    """Test that all required dependencies are available."""
    required_packages = ['fastmcp', 'openai', 'dotenv', 'airbyte', 'pandas']
    missing_packages = []
    
    for package in required_packages:
        try:
            if package == 'dotenv':
                import python_dotenv
            else:
                __import__(package)
            print(f"✅ {package} is available")
        except ImportError:
            print(f"❌ {package} is missing")
            missing_packages.append(package)
    
    return len(missing_packages) == 0

def test_catalog_file():
    """Test that the connector catalog file is accessible."""
    catalog_path = 'airbyte-connector-catalog.json'
    if os.path.exists(catalog_path):
        print("✅ Connector catalog file found")
        return True
    else:
        print("❌ Connector catalog file not found")
        return False

def main():
    """Run all tests."""
    print("🧪 Testing PyAirbyte MCP Server deployment readiness...\n")
    
    tests = [
        ("Dependencies", test_dependencies),
        ("Catalog File", test_catalog_file),
        ("Import", test_import),
    ]
    
    all_passed = True
    for test_name, test_func in tests:
        print(f"\n📋 Testing {test_name}:")
        if not test_func():
            all_passed = False
    
    print("\n" + "="*50)
    if all_passed:
        print("🎉 All tests passed! Ready for Heroku deployment.")
        print("\nTo deploy to Heroku:")
        print("1. git add .")
        print("2. git commit -m 'Fix deployment issues'")
        print("3. git push heroku main")
        print("\nMake sure to set these environment variables in Heroku:")
        print("- OPENAI_API_KEY (required)")
        print("- VECTOR_STORE_ID (optional, for file search)")
    else:
        print("❌ Some tests failed. Please fix the issues before deploying.")
    
    return all_passed

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
