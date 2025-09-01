#!/usr/bin/env python3
"""
China ETFs Update Script
Updates systematic_trading.py with new ETF data from CSV
"""

import pandas as pd
import re
import shutil
from datetime import datetime
import sys
import os

def backup_systematic_trading():
    """Create backup of current systematic_trading.py"""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_file = f"app/systematic_trading_backup_{timestamp}.py"
    
    try:
        shutil.copy("app/systematic_trading.py", backup_file)
        print(f"✅ Backup created: {backup_file}")
        return backup_file
    except Exception as e:
        print(f"❌ Backup failed: {e}")
        return None

def load_etf_data(csv_file="china_etfs_update.csv"):
    """Load ETF data from CSV file"""
    try:
        df = pd.read_csv(csv_file, encoding='utf-8-sig')
        
        required_columns = ['Symbol', 'Chinese_Name', 'Volume_30d', 'Sector']
        missing_columns = [col for col in required_columns if col not in df.columns]
        
        if missing_columns:
            print(f"❌ Missing required columns: {missing_columns}")
            return None
        
        # Clean and sort data
        df = df.dropna(subset=['Symbol', 'Chinese_Name'])
        
        # Convert volume to numeric for sorting
        df['Volume_Numeric'] = df['Volume_30d'].str.replace('B', '').str.replace('M', '').astype(float)
        df = df.sort_values('Volume_Numeric', ascending=False)
        
        print(f"✅ Loaded {len(df)} ETFs from {csv_file}")
        return df
        
    except FileNotFoundError:
        print(f"❌ File not found: {csv_file}")
        print("Please create the CSV file with ETF data first")
        return None
    except Exception as e:
        print(f"❌ Error loading data: {e}")
        return None

def generate_etfs_dict_code(df):
    """Generate Python dictionary code for systematic_trading.py"""
    
    code_lines = []
    code_lines.append("        # Chinese Market ETFs - Updated from cn.investing.com")
    code_lines.append(f"        # Top {len(df)} most actively traded ETFs - Updated {datetime.now().strftime('%Y-%m-%d')}")
    code_lines.append("        self.china_sector_etfs = {")
    
    # Group by sector for better organization
    sectors = df.groupby('Sector')
    
    for sector_name, sector_etfs in sectors:
        # Add sector comment
        code_lines.append(f"            # {sector_name} - {len(sector_etfs)} ETFs")
        
        for _, etf in sector_etfs.iterrows():
            symbol = etf['Symbol']
            chinese_name = etf['Chinese_Name']
            volume = etf['Volume_30d']
            
            # Clean the Chinese name for Python string (escape quotes)
            cleaned_name = chinese_name.replace("'", "\\'").replace('"', '\\"')
            
            # Add comment with volume info
            code_lines.append(f"            '{symbol}': '{cleaned_name}',  # {volume} volume")
        
        code_lines.append("")  # Empty line between sectors
    
    # Remove last empty line and close dict
    if code_lines[-1] == "":
        code_lines.pop()
    
    code_lines.append("        }")
    
    return "\n".join(code_lines)

def update_systematic_trading_file(new_etfs_code):
    """Update systematic_trading.py with new ETFs dictionary"""
    
    try:
        with open("app/systematic_trading.py", "r", encoding="utf-8") as f:
            content = f.read()
        
        # Find the china_sector_etfs section
        # Pattern to match the entire dictionary definition
        pattern = r"(# Chinese Market ETFs.*?self\.china_sector_etfs\s*=\s*{.*?})"
        
        match = re.search(pattern, content, re.DOTALL)
        
        if match:
            # Replace the entire section
            updated_content = re.sub(pattern, new_etfs_code, content, flags=re.DOTALL)
            
            # Write updated content
            with open("app/systematic_trading.py", "w", encoding="utf-8") as f:
                f.write(updated_content)
            
            print("✅ systematic_trading.py updated successfully")
            return True
        else:
            print("❌ Could not find china_sector_etfs section")
            print("Available patterns in file:")
            
            # Show available patterns for debugging
            china_patterns = re.findall(r"china.*?etf", content, re.IGNORECASE)
            for pattern in china_patterns[:5]:
                print(f"   {pattern}")
            
            return False
            
    except Exception as e:
        print(f"❌ Error updating file: {e}")
        return False

def preview_changes(df):
    """Preview the changes before applying"""
    
    print("\n📋 PREVIEW OF CHANGES")
    print("=" * 50)
    
    # Show sector breakdown
    sector_counts = df['Sector'].value_counts()
    print("📊 ETFs by Sector:")
    for sector, count in sector_counts.items():
        print(f"   {sector}: {count} ETFs")
    
    print(f"\n🏆 Top 10 by Volume:")
    top_10 = df.head(10)
    for i, (_, etf) in enumerate(top_10.iterrows(), 1):
        print(f"   {i:2d}. {etf['Symbol']}: {etf['Volume_30d']} volume")
    
    print(f"\n📈 Exchange Distribution:")
    exchange_counts = df['Symbol'].str.extract(r'\.([SZ]+)$')[0].value_counts()
    for exchange, count in exchange_counts.items():
        exchange_name = "Shanghai" if exchange == "SS" else "Shenzhen" if exchange == "SZ" else exchange
        print(f"   {exchange_name} (.{exchange}): {count} ETFs")

def main():
    """Main update process"""
    
    print("🇨🇳 China ETFs Update Tool")
    print("=" * 40)
    print(f"⏰ Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Check if we're in the right directory
    if not os.path.exists("app/systematic_trading.py"):
        print("❌ Please run this script from the GridTrader Pro root directory")
        return False
    
    # Step 1: Load new ETF data
    csv_file = input("📁 Enter CSV file path (default: china_etfs_update.csv): ").strip()
    if not csv_file:
        csv_file = "china_etfs_update.csv"
    
    df = load_etf_data(csv_file)
    if df is None:
        return False
    
    # Step 2: Preview changes
    preview_changes(df)
    
    # Step 3: Confirm update
    print("\n" + "=" * 50)
    confirm = input("🔄 Apply these changes to systematic_trading.py? (y/N): ").strip().lower()
    
    if confirm != 'y':
        print("📝 Update cancelled")
        return False
    
    # Step 4: Create backup
    backup_file = backup_systematic_trading()
    if not backup_file:
        return False
    
    # Step 5: Generate new code
    print("🔄 Generating new ETFs dictionary...")
    new_code = generate_etfs_dict_code(df)
    
    # Step 6: Save generated code for review
    with open('new_china_etfs_code.py', 'w', encoding='utf-8') as f:
        f.write(new_code)
    print("✅ Generated code saved to: new_china_etfs_code.py")
    
    # Step 7: Apply changes
    success = update_systematic_trading_file(new_code)
    
    if success:
        print("\n🎉 Update completed successfully!")
        print(f"📁 Backup available at: {backup_file}")
        print(f"📊 Updated with {len(df)} ETFs")
        
        print("\n📋 Next Steps:")
        print("1. Run validation: python scripts/validate_china_etfs.py")
        print("2. Test sector analysis: python -c \"from app.systematic_trading import systematic_trading_engine; print('Test:', len(systematic_trading_engine.calculate_sector_scores('China', 90)))\"")
        print("3. Commit changes: git add app/systematic_trading.py && git commit -m 'Update China ETFs'")
        
        return True
    else:
        print("\n❌ Update failed - please check the error messages above")
        print(f"🔄 Restore from backup: cp {backup_file} app/systematic_trading.py")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
