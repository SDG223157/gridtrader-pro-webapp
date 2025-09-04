#!/usr/bin/env python3
"""
Test script for security middleware functionality
Run this to verify the security features are working correctly
"""

import requests
import time
import sys
from typing import List

def test_security_middleware(base_url: str = "http://localhost:3000"):
    """Test the security middleware functionality"""
    
    print("🛡️ Testing GridTrader Pro Security Middleware")
    print(f"Base URL: {base_url}")
    print("=" * 50)
    
    # Test 1: Normal health check (should work)
    print("\n1. Testing normal health check...")
    try:
        response = requests.get(f"{base_url}/health", timeout=5)
        if response.status_code == 200:
            print("✅ Health check successful")
        else:
            print(f"❌ Health check failed: {response.status_code}")
    except Exception as e:
        print(f"❌ Health check error: {e}")
        return
    
    # Test 2: Security status endpoint
    print("\n2. Testing security status endpoint...")
    try:
        response = requests.get(f"{base_url}/debug/security-status", timeout=5)
        if response.status_code == 200:
            status = response.json()
            print("✅ Security status retrieved:")
            for key, value in status.items():
                print(f"   {key}: {value}")
        else:
            print(f"❌ Security status failed: {response.status_code}")
    except Exception as e:
        print(f"❌ Security status error: {e}")
    
    # Test 3: Attack pattern detection
    print("\n3. Testing attack pattern detection...")
    attack_urls = [
        "/wp-admin/setup-config.php",
        "/wordpress/wp-admin/setup-config.php",
        "/admin.php",
        "/../../../etc/passwd",
        "/?id=1' UNION SELECT * FROM users--"
    ]
    
    blocked_count = 0
    for url in attack_urls:
        try:
            response = requests.get(f"{base_url}{url}", timeout=5)
            if response.status_code == 403:
                print(f"✅ Blocked attack pattern: {url}")
                blocked_count += 1
            elif response.status_code == 404:
                print(f"⚠️ Got 404 for: {url} (might be blocked by rate limiting)")
            else:
                print(f"❌ Attack pattern not blocked: {url} (status: {response.status_code})")
        except Exception as e:
            print(f"❌ Error testing {url}: {e}")
    
    if blocked_count > 0:
        print(f"✅ Attack detection working: {blocked_count}/{len(attack_urls)} patterns blocked")
    else:
        print("⚠️ Attack detection may not be working as expected")
    
    # Test 4: Rate limiting (be careful with this)
    print("\n4. Testing rate limiting (light test)...")
    print("   Making 5 requests to a non-existent page...")
    
    rate_limit_triggered = False
    for i in range(5):
        try:
            response = requests.get(f"{base_url}/test-rate-limit-{i}", timeout=5)
            if response.status_code == 429:
                print(f"✅ Rate limiting triggered at request {i+1}")
                rate_limit_triggered = True
                break
            elif response.status_code == 403:
                print(f"✅ Attack detection triggered at request {i+1}")
                break
            else:
                print(f"   Request {i+1}: {response.status_code}")
        except Exception as e:
            print(f"❌ Error in rate limit test: {e}")
        
        time.sleep(0.1)  # Small delay between requests
    
    if not rate_limit_triggered:
        print("ℹ️ Rate limiting not triggered (this is normal for light testing)")
    
    # Test 5: Security headers
    print("\n5. Testing security headers...")
    try:
        response = requests.get(f"{base_url}/", timeout=5)
        headers_to_check = [
            'X-Content-Type-Options',
            'X-Frame-Options', 
            'X-XSS-Protection',
            'Content-Security-Policy'
        ]
        
        headers_found = 0
        for header in headers_to_check:
            if header in response.headers:
                print(f"✅ {header}: {response.headers[header]}")
                headers_found += 1
            else:
                print(f"❌ Missing header: {header}")
        
        if headers_found >= 3:
            print(f"✅ Security headers working: {headers_found}/{len(headers_to_check)} present")
        else:
            print(f"⚠️ Some security headers missing: {headers_found}/{len(headers_to_check)} present")
    
    except Exception as e:
        print(f"❌ Error testing security headers: {e}")
    
    print("\n" + "=" * 50)
    print("🛡️ Security middleware test completed!")
    print("\nNote: If you see 403 responses for attack patterns, that's good!")
    print("The security middleware is working to protect your application.")

if __name__ == "__main__":
    # Allow custom URL from command line
    url = sys.argv[1] if len(sys.argv) > 1 else "http://localhost:3000"
    test_security_middleware(url)



