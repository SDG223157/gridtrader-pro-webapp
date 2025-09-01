#!/usr/bin/env python3
"""
Test script for API token integration with MCP server
"""

import os
import sys
import json
import time
import requests
import subprocess
from datetime import datetime
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Test configuration
BASE_URL = "https://gridsai.app"
TEST_USER_EMAIL = "test@gridtrader.com"
TEST_USER_PASSWORD = "testpass123"

def test_api_connection():
    """Test basic API connection"""
    try:
        response = requests.get(f"{BASE_URL}/health", timeout=5)
        if response.status_code == 200:
            logger.info("✅ GridTrader Pro API is running")
            return True
        else:
            logger.error(f"❌ API health check failed: {response.status_code}")
            return False
    except Exception as e:
        logger.error(f"❌ Failed to connect to API: {e}")
        return False

def create_test_user():
    """Create a test user for token testing"""
    try:
        # Try to register a test user
        response = requests.post(f"{BASE_URL}/api/auth/register", json={
            "email": TEST_USER_EMAIL,
            "password": TEST_USER_PASSWORD,
            "first_name": "Test",
            "last_name": "User"
        })
        
        if response.status_code == 200:
            logger.info("✅ Test user created successfully")
            return response.json()
        elif response.status_code == 400 and "already exists" in response.text.lower():
            logger.info("✅ Test user already exists")
            return {"success": True}
        else:
            logger.error(f"❌ Failed to create test user: {response.status_code} - {response.text}")
            return None
    except Exception as e:
        logger.error(f"❌ Error creating test user: {e}")
        return None

def login_test_user():
    """Login test user and get session"""
    try:
        session = requests.Session()
        
        # Login
        response = session.post(f"{BASE_URL}/api/auth/login", data={
            "email": TEST_USER_EMAIL,
            "password": TEST_USER_PASSWORD
        })
        
        if response.status_code == 200:
            data = response.json()
            if data.get("success"):
                logger.info("✅ Test user logged in successfully")
                return session, data.get("access_token")
            else:
                logger.error(f"❌ Login failed: {data}")
                return None, None
        else:
            logger.error(f"❌ Login request failed: {response.status_code} - {response.text}")
            return None, None
    except Exception as e:
        logger.error(f"❌ Error logging in: {e}")
        return None, None

def create_api_token(session):
    """Create an API token"""
    try:
        token_data = {
            "name": "Test MCP Token",
            "description": "Token for testing MCP integration",
            "permissions": ["read", "write"],
            "expires_in_days": 30
        }
        
        response = session.post(f"{BASE_URL}/api/tokens", json=token_data)
        
        if response.status_code == 200:
            data = response.json()
            if data.get("success"):
                logger.info("✅ API token created successfully")
                return data["token"]["token"], data
            else:
                logger.error(f"❌ Token creation failed: {data}")
                return None, None
        else:
            logger.error(f"❌ Token creation request failed: {response.status_code} - {response.text}")
            return None, None
    except Exception as e:
        logger.error(f"❌ Error creating token: {e}")
        return None, None

def test_token_authentication(token):
    """Test API token authentication"""
    try:
        headers = {"Authorization": f"Bearer {token}"}
        
        # Test portfolios endpoint
        response = requests.get(f"{BASE_URL}/api/portfolios", headers=headers)
        
        if response.status_code == 200:
            logger.info("✅ Token authentication successful")
            return True
        else:
            logger.error(f"❌ Token authentication failed: {response.status_code} - {response.text}")
            return False
    except Exception as e:
        logger.error(f"❌ Error testing token: {e}")
        return False

def test_mcp_server_with_token(token):
    """Test MCP server with the generated token"""
    try:
        # Update environment for MCP server
        env = os.environ.copy()
        env["GRIDTRADER_API_URL"] = BASE_URL
        env["GRIDTRADER_ACCESS_TOKEN"] = token
        
        # Test MCP server
        mcp_server_path = "/Users/sdg223157/gridsai_webapp/gridtrader-pro-webapp/mcp-server/dist/index.js"
        
        if not os.path.exists(mcp_server_path):
            logger.error(f"❌ MCP server not found at {mcp_server_path}")
            return False
        
        # Create test input for MCP server
        test_input = json.dumps({
            "jsonrpc": "2.0",
            "id": 1,
            "method": "tools/list"
        })
        
        # Run MCP server test
        process = subprocess.Popen(
            ["node", mcp_server_path],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            env=env,
            cwd="/Users/sdg223157/gridsai_webapp/gridtrader-pro-webapp/mcp-server"
        )
        
        stdout, stderr = process.communicate(input=test_input.encode(), timeout=10)
        
        if process.returncode == 0:
            try:
                response = json.loads(stdout.decode())
                if "result" in response and "tools" in response["result"]:
                    tools = response["result"]["tools"]
                    logger.info(f"✅ MCP server working! Found {len(tools)} tools")
                    return True
                else:
                    logger.error(f"❌ MCP server response invalid: {response}")
                    return False
            except json.JSONDecodeError:
                logger.error(f"❌ MCP server response not JSON: {stdout.decode()}")
                return False
        else:
            logger.error(f"❌ MCP server failed: {stderr.decode()}")
            return False
            
    except subprocess.TimeoutExpired:
        logger.error("❌ MCP server test timed out")
        return False
    except Exception as e:
        logger.error(f"❌ Error testing MCP server: {e}")
        return False

def test_cursor_config_generation(session):
    """Test MCP configuration generation"""
    try:
        # Get list of tokens
        response = session.get(f"{BASE_URL}/api/tokens")
        
        if response.status_code == 200:
            data = response.json()
            tokens = data.get("tokens", [])
            
            if tokens:
                token_id = tokens[0]["id"]
                
                # Get MCP config
                response = session.get(f"{BASE_URL}/api/tokens/{token_id}/mcp-config")
                
                if response.status_code == 200:
                    config_data = response.json()
                    if "mcp_config" in config_data:
                        logger.info("✅ MCP configuration generation successful")
                        return True
                    else:
                        logger.error(f"❌ MCP config missing: {config_data}")
                        return False
                else:
                    logger.error(f"❌ MCP config request failed: {response.status_code}")
                    return False
            else:
                logger.error("❌ No tokens found for MCP config test")
                return False
        else:
            logger.error(f"❌ Failed to get tokens: {response.status_code}")
            return False
    except Exception as e:
        logger.error(f"❌ Error testing MCP config: {e}")
        return False

def main():
    """Run all tests"""
    print("🧪 GridTrader Pro API Token Integration Test")
    print("=" * 50)
    
    # Test 1: API Connection
    print("\n1. Testing API connection...")
    if not test_api_connection():
        print("❌ API connection failed. Make sure GridTrader Pro is running.")
        return False
    
    # Test 2: Create test user
    print("\n2. Creating test user...")
    if not create_test_user():
        print("❌ Failed to create test user")
        return False
    
    # Test 3: Login
    print("\n3. Testing user login...")
    session, jwt_token = login_test_user()
    if not session:
        print("❌ Failed to login test user")
        return False
    
    # Test 4: Create API token
    print("\n4. Creating API token...")
    api_token, token_data = create_api_token(session)
    if not api_token:
        print("❌ Failed to create API token")
        return False
    
    print(f"   Token: {api_token[:20]}...")
    
    # Test 5: Test token authentication
    print("\n5. Testing token authentication...")
    if not test_token_authentication(api_token):
        print("❌ Token authentication failed")
        return False
    
    # Test 6: Test MCP configuration
    print("\n6. Testing MCP configuration generation...")
    if not test_cursor_config_generation(session):
        print("❌ MCP configuration generation failed")
        return False
    
    # Test 7: Test MCP server
    print("\n7. Testing MCP server with token...")
    if not test_mcp_server_with_token(api_token):
        print("❌ MCP server test failed")
        return False
    
    print("\n🎉 All tests passed!")
    print("\n📋 Summary:")
    print(f"   • API Token: {api_token}")
    print(f"   • Token Name: {token_data['token']['name']}")
    print(f"   • Permissions: {token_data['token']['permissions']}")
    print(f"   • Created: {token_data['token']['created_at']}")
    
    print("\n🔧 Cursor Configuration:")
    mcp_config = token_data["mcp_config"]
    print(json.dumps(mcp_config, indent=2))
    
    print("\n✅ Ready for Cursor integration!")
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
