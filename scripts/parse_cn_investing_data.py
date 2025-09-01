#!/usr/bin/env python3
"""
Parse cn.investing.com ETF data and convert to GridTrader Pro format
Handles the specific format from cn.investing.com
"""

import pandas as pd
import re
import csv
from datetime import datetime
import sys

def parse_cn_investing_data(input_file="cn_investing_raw.csv"):
    """
    Parse the raw data from cn.investing.com and convert to our format
    
    Input format from cn.investing.com:
    名称, 代码, 最新价, 涨跌幅, 交易量, 时间
    """
    
    print("🔄 Parsing cn.investing.com ETF data...")
    
    try:
        # Read the raw data with proper encoding
        df = pd.read_csv(input_file, encoding='utf-8-sig')
        
        # Clean column names (remove extra spaces and Chinese characters)
        df.columns = df.columns.str.strip()
        
        # Map Chinese column names to English
        column_mapping = {
            '名称': 'Name',
            '代码': 'Code', 
            '最新价': 'Latest_Price',
            '涨跌幅': 'Change_Percent',
            '交易量': 'Volume',
            '时间': 'Time'
        }
        
        # Rename columns
        for chinese_col, english_col in column_mapping.items():
            if chinese_col in df.columns:
                df = df.rename(columns={chinese_col: english_col})
        
        # Clean and process the data
        processed_etfs = []
        
        for index, row in df.iterrows():
            try:
                # Skip empty rows
                if pd.isna(row.get('Name')) or pd.isna(row.get('Code')):
                    continue
                
                name = str(row['Name']).strip()
                code = str(row['Code']).strip()
                volume = str(row.get('Volume', '')).strip()
                
                # Skip if essential data is missing
                if not name or not code or name == 'nan' or code == 'nan':
                    continue
                
                # Convert code to proper symbol format
                symbol = convert_code_to_symbol(code)
                if not symbol:
                    print(f"⚠️  Skipping {code}: Could not determine exchange")
                    continue
                
                # Parse volume
                volume_numeric = parse_volume(volume)
                
                # Determine sector from name
                sector = determine_sector_from_name(name)
                
                # Create processed entry
                processed_etf = {
                    'Symbol': symbol,
                    'Chinese_Name': name,
                    'English_Name': extract_english_name(name),
                    'Volume_30d': volume,
                    'Volume_Numeric': volume_numeric,
                    'Sector': sector,
                    'Exchange': symbol.split('.')[1] if '.' in symbol else 'Unknown',
                    'Latest_Price': row.get('Latest_Price', ''),
                    'Change_Percent': row.get('Change_Percent', ''),
                    'Time': row.get('Time', ''),
                    'Notes': f"From cn.investing.com - {volume} volume"
                }
                
                processed_etfs.append(processed_etf)
                
            except Exception as e:
                print(f"⚠️  Error processing row {index}: {e}")
                continue
        
        # Convert to DataFrame and sort by volume
        result_df = pd.DataFrame(processed_etfs)
        
        if not result_df.empty:
            result_df = result_df.sort_values('Volume_Numeric', ascending=False)
            print(f"✅ Successfully processed {len(result_df)} ETFs")
        else:
            print("❌ No valid ETFs processed")
            return None
        
        return result_df
        
    except Exception as e:
        print(f"❌ Error parsing data: {e}")
        return None

def convert_code_to_symbol(code):
    """Convert ETF code to proper yfinance symbol format"""
    
    # Remove any non-numeric characters
    clean_code = re.sub(r'[^\d]', '', str(code))
    
    if len(clean_code) != 6:
        return None
    
    # Determine exchange based on code patterns
    # Shanghai Stock Exchange: 51xxxx, 58xxxx, 56xxxx, 52xxxx
    # Shenzhen Stock Exchange: 15xxxx, 16xxxx
    
    if clean_code.startswith(('51', '58', '56', '52', '50')):
        return f"{clean_code}.SS"  # Shanghai
    elif clean_code.startswith(('15', '16', '17')):
        return f"{clean_code}.SZ"  # Shenzhen
    else:
        # Default to Shanghai for unknown patterns
        return f"{clean_code}.SS"

def parse_volume(volume_str):
    """Parse volume string to numeric value for sorting"""
    
    if not volume_str or volume_str == 'nan':
        return 0
    
    # Remove any extra characters and convert
    volume_clean = str(volume_str).replace(',', '').strip()
    
    try:
        if 'B' in volume_clean:
            return float(volume_clean.replace('B', '')) * 1000  # Convert to millions
        elif 'M' in volume_clean:
            return float(volume_clean.replace('M', ''))
        elif 'K' in volume_clean:
            return float(volume_clean.replace('K', '')) / 1000  # Convert to millions
        else:
            # Assume it's already in millions
            return float(volume_clean)
    except:
        return 0

def extract_english_name(chinese_name):
    """Extract English name from Chinese name if present"""
    
    # Look for English text in parentheses
    english_match = re.search(r'\(([A-Za-z\s&\-\.]+)\)', chinese_name)
    if english_match:
        return english_match.group(1).strip()
    
    # Look for English text without parentheses
    english_parts = re.findall(r'[A-Za-z][A-Za-z\s&\-\.]*[A-Za-z]', chinese_name)
    if english_parts:
        return ' '.join(english_parts).strip()
    
    return ""

def determine_sector_from_name(name):
    """Determine sector category from ETF name"""
    
    name_lower = name.lower()
    
    # Technology & Innovation
    if any(keyword in name_lower for keyword in ['科技', '互联网', '人工智能', '5g', '通信', '软件', '芯片', '半导体', 'tech', 'ai', 'internet', 'semiconductor']):
        return "Technology & Innovation"
    
    # Healthcare & Biotech
    elif any(keyword in name_lower for keyword in ['医疗', '生物', '医药', '保健', '药', 'medical', 'biotech', 'health', 'pharma']):
        return "Healthcare & Biotech"
    
    # Financial Services
    elif any(keyword in name_lower for keyword in ['银行', '证券', '金融', '保险', 'bank', 'financial', 'insurance']):
        return "Financial Services"
    
    # Consumer & Retail
    elif any(keyword in name_lower for keyword in ['消费', '酒', '食品', '饮料', '零售', 'consumer', 'retail', 'food', 'beverage']):
        return "Consumer & Retail"
    
    # Energy & Materials
    elif any(keyword in name_lower for keyword in ['能源', '新能源', '电池', '光伏', '煤炭', '有色', '材料', 'energy', 'battery', 'solar', 'materials']):
        return "Energy & Materials"
    
    # Infrastructure & Defense
    elif any(keyword in name_lower for keyword in ['军工', '国防', '基建', '交通', '建筑', 'defense', 'military', 'infrastructure']):
        return "Infrastructure & Defense"
    
    # Hong Kong & International
    elif any(keyword in name_lower for keyword in ['香港', '恒生', 'qdii', 'hong kong', 'hang seng']):
        return "Hong Kong & International"
    
    # Broad Market
    elif any(keyword in name_lower for keyword in ['300', '500', '1000', '2000', 'a50', 'a500', '上证', '深证', '创业板']):
        return "Broad Market"
    
    else:
        return "Other"

def save_processed_data(df, output_file="china_etfs_processed.csv"):
    """Save processed data to CSV"""
    
    # Select and order columns for output
    output_columns = [
        'Symbol', 'Chinese_Name', 'English_Name', 'Volume_30d', 'Volume_Numeric',
        'Sector', 'Exchange', 'Latest_Price', 'Change_Percent', 'Notes'
    ]
    
    # Only include columns that exist
    available_columns = [col for col in output_columns if col in df.columns]
    output_df = df[available_columns]
    
    # Save to CSV
    output_df.to_csv(output_file, index=False, encoding='utf-8-sig')
    print(f"✅ Processed data saved to: {output_file}")
    
    # Generate summary
    print(f"\n📊 Processing Summary:")
    print(f"   Total ETFs: {len(df)}")
    print(f"   Sectors: {df['Sector'].nunique()}")
    print(f"   Exchanges: {df['Exchange'].nunique()}")
    
    # Show sector breakdown
    print(f"\n📈 Sector Breakdown:")
    sector_counts = df['Sector'].value_counts()
    for sector, count in sector_counts.items():
        print(f"   {sector}: {count} ETFs")
    
    return output_file

def generate_systematic_trading_code(df, top_n=50):
    """Generate code for systematic_trading.py"""
    
    # Take top N by volume
    top_etfs = df.head(top_n)
    
    code_lines = []
    code_lines.append("        # Chinese Market ETFs - Updated from cn.investing.com")
    code_lines.append(f"        # Top {len(top_etfs)} most actively traded ETFs - Updated {datetime.now().strftime('%Y-%m-%d')}")
    code_lines.append("        self.china_sector_etfs = {")
    
    # Group by sector
    sectors = top_etfs.groupby('Sector')
    
    for sector_name, sector_etfs in sectors:
        code_lines.append(f"            # {sector_name} - {len(sector_etfs)} ETFs")
        
        for _, etf in sector_etfs.iterrows():
            symbol = etf['Symbol']
            chinese_name = etf['Chinese_Name']
            volume = etf['Volume_30d']
            
            # Clean name for Python string
            cleaned_name = chinese_name.replace("'", "\\'").replace('"', '\\"')
            
            code_lines.append(f"            '{symbol}': '{cleaned_name}',  # {volume} volume")
        
        code_lines.append("")
    
    # Remove last empty line and close
    if code_lines[-1] == "":
        code_lines.pop()
    
    code_lines.append("        }")
    
    code_text = "\n".join(code_lines)
    
    # Save to file
    with open('china_etfs_systematic_trading_code.py', 'w', encoding='utf-8') as f:
        f.write(code_text)
    
    print(f"✅ Generated systematic_trading.py code for top {len(top_etfs)} ETFs")
    print(f"📁 Code saved to: china_etfs_systematic_trading_code.py")
    
    return code_text

def main():
    """Main processing function"""
    
    print("🇨🇳 cn.investing.com ETF Data Parser")
    print("=" * 45)
    
    # Get input file
    input_file = input("📁 Enter raw CSV file from cn.investing.com (default: cn_investing_raw.csv): ").strip()
    if not input_file:
        input_file = "cn_investing_raw.csv"
    
    # Parse the data
    df = parse_cn_investing_data(input_file)
    
    if df is None or df.empty:
        print("❌ No data to process")
        return False
    
    # Save processed data
    output_file = save_processed_data(df)
    
    # Generate code for systematic_trading.py
    top_n = int(input(f"\n🔢 How many top ETFs to include? (default: 50, max: {len(df)}): ").strip() or "50")
    top_n = min(top_n, len(df))
    
    generate_systematic_trading_code(df, top_n)
    
    print(f"\n🎉 Processing Complete!")
    print(f"📁 Files created:")
    print(f"   - {output_file} (processed data)")
    print(f"   - china_etfs_systematic_trading_code.py (code for systematic_trading.py)")
    
    print(f"\n📋 Next Steps:")
    print(f"1. Review the processed data in {output_file}")
    print(f"2. Copy code from china_etfs_systematic_trading_code.py")
    print(f"3. Replace china_sector_etfs in app/systematic_trading.py")
    print(f"4. Run: python scripts/validate_china_etfs.py")
    print(f"5. Run: python scripts/test_china_sector_analysis.py")
    
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
