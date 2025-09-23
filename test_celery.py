#!/usr/bin/env python3
"""
Test Celery Configuration
Check if Celery can start correctly
"""

import os
import sys

def test_celery_imports():
    """Test if all required modules can be imported"""
    print("🧪 TESTING CELERY CONFIGURATION")
    print("=" * 50)
    
    # Test basic imports
    print("1. 📦 TESTING IMPORTS:")
    try:
        import celery
        print(f"   ✅ Celery: {celery.__version__}")
    except ImportError as e:
        print(f"   ❌ Celery import failed: {e}")
        return False
    
    try:
        import redis
        print(f"   ✅ Redis: {redis.__version__}")
    except ImportError as e:
        print(f"   ❌ Redis import failed: {e}")
        return False
    
    try:
        from database import engine, User, Portfolio, Grid
        print(f"   ✅ Database models imported")
    except ImportError as e:
        print(f"   ❌ Database import failed: {e}")
        return False
    
    try:
        from data_provider import YFinanceDataProvider
        print(f"   ✅ Data provider imported")
    except ImportError as e:
        print(f"   ❌ Data provider import failed: {e}")
        return False
    
    # Test tasks module
    print(f"\n2. 🔧 TESTING TASKS MODULE:")
    try:
        import tasks
        print(f"   ✅ Tasks module imported")
        
        # Test celery app
        if hasattr(tasks, 'celery_app'):
            print(f"   ✅ Celery app found")
            
            # Test Redis connection
            redis_url = os.getenv('REDIS_URL', 'redis://localhost:6379/0')
            print(f"   🔴 Redis URL: {redis_url[:30]}...")
            
            # Test if we can inspect tasks
            try:
                app = tasks.celery_app
                registered_tasks = list(app.tasks.keys())
                print(f"   ✅ Registered tasks: {len(registered_tasks)}")
                for task in registered_tasks:
                    if 'tasks.' in task:
                        print(f"      - {task}")
            except Exception as e:
                print(f"   ⚠️ Task inspection failed: {e}")
                
        else:
            print(f"   ❌ Celery app not found in tasks module")
            return False
            
    except ImportError as e:
        print(f"   ❌ Tasks module import failed: {e}")
        return False
    except Exception as e:
        print(f"   ❌ Tasks module error: {e}")
        return False
    
    # Test environment variables
    print(f"\n3. 🌍 TESTING ENVIRONMENT:")
    env_vars = ['REDIS_URL', 'DB_HOST', 'DB_NAME', 'SMTP_USERNAME']
    for var in env_vars:
        value = os.getenv(var)
        status = "✅" if value else "❌"
        display_value = f"{value[:20]}..." if value and len(value) > 20 else value
        print(f"   {var}: {status} {display_value or 'NOT SET'}")
    
    print(f"\n4. 🎯 CELERY STARTUP TEST:")
    try:
        # Test if we can create a Celery worker instance
        from celery import Celery
        redis_url = os.getenv('REDIS_URL', 'redis://localhost:6379/0')
        
        test_app = Celery('test', broker=redis_url, backend=redis_url)
        print(f"   ✅ Celery app can be created")
        
        # Test Redis connection
        try:
            import redis
            redis_client = redis.from_url(redis_url)
            redis_client.ping()
            print(f"   ✅ Redis connection successful")
        except Exception as e:
            print(f"   ❌ Redis connection failed: {e}")
            return False
            
    except Exception as e:
        print(f"   ❌ Celery startup test failed: {e}")
        return False
    
    print(f"\n✅ ALL TESTS PASSED!")
    print(f"🚀 Celery should be able to start correctly")
    return True

if __name__ == "__main__":
    success = test_celery_imports()
    sys.exit(0 if success else 1)
