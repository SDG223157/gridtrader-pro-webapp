#!/usr/bin/env python3
"""
Script to delete all portfolios using the GridTrader Pro API
"""

import requests
import json

# Configuration
API_URL = "https://gridsai.app"
ACCESS_TOKEN = "QqmnH9cvylz6guuz2in1gGPXoqbetFnFScl96ShggHg"

# Headers for API calls
headers = {
    "Authorization": f"Bearer {ACCESS_TOKEN}",
    "Content-Type": "application/json"
}

def get_portfolios():
    """Get all portfolios"""
    try:
        response = requests.get(f"{API_URL}/api/portfolios", headers=headers)
        if response.status_code == 200:
            return response.json()
        else:
            print(f"❌ Failed to get portfolios: {response.status_code}")
            print(f"Response: {response.text}")
            return None
    except Exception as e:
        print(f"❌ Error getting portfolios: {e}")
        return None

def delete_portfolio(portfolio_id, portfolio_name):
    """Delete a specific portfolio"""
    try:
        print(f"🗑️ Deleting portfolio: {portfolio_name} (ID: {portfolio_id})")
        response = requests.delete(f"{API_URL}/api/portfolios/{portfolio_id}", headers=headers)
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Successfully deleted portfolio: {portfolio_name}")
            print(f"   • Holdings deleted: {result.get('deleted_holdings', 0)}")
            print(f"   • Transactions deleted: {result.get('deleted_transactions', 0)}")
            print(f"   • Grids deleted: {result.get('deleted_grids', 0)}")
            print(f"   • Grid orders deleted: {result.get('deleted_grid_orders', 0)}")
            return True
        else:
            print(f"❌ Failed to delete portfolio {portfolio_name}: {response.status_code}")
            print(f"Response: {response.text}")
            return False
    except Exception as e:
        print(f"❌ Error deleting portfolio {portfolio_name}: {e}")
        return False

def main():
    print("🗑️ GridTrader Pro Portfolio Deletion Script")
    print("=" * 50)
    
    # Get all portfolios
    portfolios = get_portfolios()
    if not portfolios:
        print("❌ Could not retrieve portfolios")
        return
    
    print(f"📊 Found {len(portfolios)} portfolio(s):")
    for portfolio in portfolios:
        print(f"   • {portfolio['name']} (ID: {portfolio['id']}) - ${portfolio['current_value']:,.2f}")
    
    print("\n⚠️  WARNING: This will permanently delete ALL portfolios and their data!")
    print("⚠️  This action cannot be undone!")
    
    # Confirm deletion
    confirm = input("\nType 'DELETE ALL' to confirm: ")
    if confirm != "DELETE ALL":
        print("❌ Deletion cancelled")
        return
    
    # Delete each portfolio
    print(f"\n🗑️ Deleting {len(portfolios)} portfolio(s)...")
    success_count = 0
    
    for portfolio in portfolios:
        if delete_portfolio(portfolio['id'], portfolio['name']):
            success_count += 1
        print()  # Empty line for readability
    
    print("=" * 50)
    print(f"✅ Deletion complete: {success_count}/{len(portfolios)} portfolios deleted")
    
    if success_count == len(portfolios):
        print("🎉 All portfolios have been successfully deleted!")
    else:
        print("⚠️  Some portfolios could not be deleted. Check the errors above.")

if __name__ == "__main__":
    main()
