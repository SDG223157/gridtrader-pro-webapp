#!/usr/bin/env python3
"""
Quick fix for user email mismatch issue
Updates debug@test.com to isky999@gmail.com while preserving all data
"""

import os
import sys
from database import SessionLocal, User, UserProfile
from sqlalchemy.orm import Session

def fix_user_email():
    """Fix the user email from debug@test.com to isky999@gmail.com"""
    
    # Get database session
    db = SessionLocal()
    
    try:
        # Find the debug user
        debug_user = db.query(User).filter(User.email == "debug@test.com").first()
        if not debug_user:
            print("❌ Debug user not found")
            return False
        
        print(f"🔍 Found user: {debug_user.email}")
        print(f"   User ID: {debug_user.id}")
        print(f"   Display Name: {debug_user.profile.display_name if debug_user.profile else 'None'}")
        
        # Check if target email already exists
        existing_target = db.query(User).filter(User.email == "isky999@gmail.com").first()
        if existing_target:
            print("❌ User isky999@gmail.com already exists")
            return False
        
        # Update the email
        old_email = debug_user.email
        debug_user.email = "isky999@gmail.com"
        debug_user.auth_provider = "google"
        debug_user.is_email_verified = True
        
        # Commit changes
        db.commit()
        db.refresh(debug_user)
        
        print(f"✅ User email updated successfully!")
        print(f"   Old email: {old_email}")
        print(f"   New email: {debug_user.email}")
        print(f"   Display name: {debug_user.profile.display_name if debug_user.profile else 'None'}")
        print(f"   User ID: {debug_user.id}")
        
        return True
        
    except Exception as e:
        db.rollback()
        print(f"❌ Error updating user email: {e}")
        return False
    
    finally:
        db.close()

if __name__ == "__main__":
    print("🔧 GridTrader Pro - User Email Fix")
    print("=" * 40)
    
    success = fix_user_email()
    
    if success:
        print("\n🎉 User email fix completed successfully!")
        print("\n📋 Next steps:")
        print("1. Refresh the Settings page in your browser")
        print("2. You should now see isky999@gmail.com as your email")
        print("3. Your profile data (Jiang Chen) is preserved")
        print("4. All portfolios, grids, and tokens remain intact")
    else:
        print("\n❌ User email fix failed!")
        print("Please check the error messages above.")
    
    print("\n" + "=" * 40)

