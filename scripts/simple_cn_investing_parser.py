#!/usr/bin/env python3
"""
Simple cn.investing.com ETF data parser (no external dependencies)
Converts cn.investing.com format to GridTrader Pro format
"""

import csv
import re
from datetime import datetime

def convert_code_to_symbol(code):
    """Convert 6-digit code to proper yfinance symbol"""
    clean_code = re.sub(r'[^\d]', '', str(code))
    
    if len(clean_code) != 6:
        return None
    
    # Shanghai: 51xxxx, 58xxxx, 56xxxx, 52xxxx, 50xxxx
    # Shenzhen: 15xxxx, 16xxxx, 17xxxx
    if clean_code.startswith(('51', '58', '56', '52', '50')):
        return f"{clean_code}.SS"
    elif clean_code.startswith(('15', '16', '17')):
        return f"{clean_code}.SZ"
    else:
        return f"{clean_code}.SS"  # Default to Shanghai

def parse_volume(volume_str):
    """Convert volume string to numeric (in millions)"""
    if not volume_str:
        return 0
    
    volume_clean = str(volume_str).replace(',', '').strip()
    
    try:
        if 'B' in volume_clean:
            return float(volume_clean.replace('B', '')) * 1000
        elif 'M' in volume_clean:
            return float(volume_clean.replace('M', ''))
        elif 'K' in volume_clean:
            return float(volume_clean.replace('K', '')) / 1000
        else:
            return float(volume_clean)
    except:
        return 0

def determine_sector(name):
    """Determine sector from ETF name"""
    name_lower = name.lower()
    
    if any(kw in name_lower for kw in ['科技', '互联网', '人工智能', '5g', '通信', '软件', '芯片', '半导体', 'tech', 'ai', 'internet', 'semiconductor']):
        return "Technology & Innovation"
    elif any(kw in name_lower for kw in ['医疗', '生物', '医药', '保健', 'medical', 'biotech', 'health', 'pharma']):
        return "Healthcare & Biotech"
    elif any(kw in name_lower for kw in ['银行', '证券', '金融', '保险', 'bank', 'financial', 'insurance']):
        return "Financial Services"
    elif any(kw in name_lower for kw in ['消费', '酒', '食品', '饮料', 'consumer', 'food', 'beverage']):
        return "Consumer & Retail"
    elif any(kw in name_lower for kw in ['能源', '新能源', '电池', '光伏', '煤炭', '有色', '材料', 'energy', 'battery', 'solar']):
        return "Energy & Materials"
    elif any(kw in name_lower for kw in ['军工', '国防', '基建', '交通', '建筑', 'defense', 'military']):
        return "Infrastructure & Defense"
    elif any(kw in name_lower for kw in ['香港', '恒生', 'qdii', 'hong kong', 'hang seng']):
        return "Hong Kong & International"
    elif any(kw in name_lower for kw in ['300', '500', '1000', '2000', 'a50', 'a500', '上证', '深证', '创业板']):
        return "Broad Market"
    else:
        return "Other"

def extract_english_name(chinese_name):
    """Extract English name from Chinese name"""
    english_match = re.search(r'\(([A-Za-z\s&\-\.]+)\)', chinese_name)
    if english_match:
        return english_match.group(1).strip()
    
    english_parts = re.findall(r'[A-Za-z][A-Za-z\s&\-\.]*[A-Za-z]', chinese_name)
    if english_parts:
        return ' '.join(english_parts).strip()
    
    return ""

def parse_cn_investing_csv(input_file):
    """Parse the CSV file from cn.investing.com"""
    
    etfs = []
    
    try:
        with open(input_file, 'r', encoding='utf-8-sig') as f:
            # Try to detect if first line is header
            first_line = f.readline().strip()
            f.seek(0)
            
            # Check if it's a header line
            if '名称' in first_line or 'Name' in first_line:
                reader = csv.DictReader(f)
            else:
                # No header, use default field names
                f.seek(0)
                reader = csv.DictReader(f, fieldnames=['名称', '代码', '最新价', '涨跌幅', '交易量', '时间'])
            
            for row_num, row in enumerate(reader, 1):
                try:
                    # Get name and code
                    name = row.get('名称', '').strip()
                    code = row.get('代码', '').strip()
                    volume = row.get('交易量', '').strip()
                    
                    if not name or not code:
                        continue
                    
                    # Convert to symbol
                    symbol = convert_code_to_symbol(code)
                    if not symbol:
                        print(f"⚠️  Row {row_num}: Could not convert code {code}")
                        continue
                    
                    # Process data
                    volume_numeric = parse_volume(volume)
                    sector = determine_sector(name)
                    english_name = extract_english_name(name)
                    
                    etf_data = {
                        'Symbol': symbol,
                        'Chinese_Name': name,
                        'English_Name': english_name,
                        'Volume_30d': volume,
                        'Volume_Numeric': volume_numeric,
                        'Sector': sector,
                        'Exchange': symbol.split('.')[1],
                        'Latest_Price': row.get('最新价', ''),
                        'Change_Percent': row.get('涨跌幅', ''),
                        'Time': row.get('时间', ''),
                        'Notes': f"cn.investing.com - {volume} volume"
                    }
                    
                    etfs.append(etf_data)
                    
                except Exception as e:
                    print(f"⚠️  Error processing row {row_num}: {e}")
                    continue
        
        # Sort by volume
        etfs.sort(key=lambda x: x['Volume_Numeric'], reverse=True)
        
        print(f"✅ Parsed {len(etfs)} ETFs from {input_file}")
        return etfs
        
    except Exception as e:
        print(f"❌ Error reading file: {e}")
        return []

def save_processed_csv(etfs, output_file="china_etfs_processed.csv"):
    """Save processed data to CSV"""
    
    if not etfs:
        print("❌ No data to save")
        return False
    
    fieldnames = [
        'Symbol', 'Chinese_Name', 'English_Name', 'Volume_30d', 'Volume_Numeric',
        'Sector', 'Exchange', 'Latest_Price', 'Change_Percent', 'Time', 'Notes'
    ]
    
    with open(output_file, 'w', newline='', encoding='utf-8-sig') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(etfs)
    
    print(f"✅ Saved to: {output_file}")
    return True

def generate_python_code(etfs, top_n=50):
    """Generate Python code for systematic_trading.py"""
    
    top_etfs = etfs[:top_n]
    
    # Group by sector
    sectors = {}
    for etf in top_etfs:
        sector = etf['Sector']
        if sector not in sectors:
            sectors[sector] = []
        sectors[sector].append(etf)
    
    code_lines = []
    code_lines.append("        # Chinese Market ETFs - Updated from cn.investing.com")
    code_lines.append(f"        # Top {len(top_etfs)} most actively traded ETFs - Updated {datetime.now().strftime('%Y-%m-%d')}")
    code_lines.append("        self.china_sector_etfs = {")
    
    for sector, sector_etfs in sectors.items():
        code_lines.append(f"            # {sector} - {len(sector_etfs)} ETFs")
        
        for etf in sector_etfs:
            symbol = etf['Symbol']
            name = etf['Chinese_Name'].replace("'", "\\'")
            volume = etf['Volume_30d']
            
            code_lines.append(f"            '{symbol}': '{name}',  # {volume} volume")
        
        code_lines.append("")
    
    if code_lines[-1] == "":
        code_lines.pop()
    
    code_lines.append("        }")
    
    code_text = "\n".join(code_lines)
    
    with open('china_etfs_systematic_trading_code.py', 'w', encoding='utf-8') as f:
        f.write(code_text)
    
    print(f"✅ Generated code for {len(top_etfs)} ETFs")
    print(f"📁 Code saved to: china_etfs_systematic_trading_code.py")
    
    return code_text

def main():
    """Main processing function"""
    
    print("🇨🇳 cn.investing.com ETF Data Parser")
    print("=" * 40)
    
    # Get input file
    input_file = input("📁 Enter CSV file from cn.investing.com (default: cn_investing_sample.csv): ").strip()
    if not input_file:
        input_file = "cn_investing_sample.csv"
    
    # Parse data
    etfs = parse_cn_investing_csv(input_file)
    
    if not etfs:
        print("❌ No ETF data parsed")
        return False
    
    # Save processed data
    save_processed_csv(etfs)
    
    # Show preview
    print(f"\n📊 Top 10 ETFs by Volume:")
    for i, etf in enumerate(etfs[:10], 1):
        print(f"   {i:2d}. {etf['Symbol']}: {etf['Chinese_Name'][:40]}... ({etf['Volume_30d']})")
    
    print(f"\n📈 Sector Distribution:")
    sector_counts = {}
    for etf in etfs:
        sector = etf['Sector']
        sector_counts[sector] = sector_counts.get(sector, 0) + 1
    
    for sector, count in sorted(sector_counts.items()):
        print(f"   {sector}: {count} ETFs")
    
    # Generate code
    top_n = int(input(f"\n🔢 How many top ETFs for systematic_trading.py? (default: 50, max: {len(etfs)}): ").strip() or "50")
    top_n = min(top_n, len(etfs))
    
    generate_python_code(etfs, top_n)
    
    print(f"\n🎉 Processing Complete!")
    print(f"📋 Next Steps:")
    print(f"1. Review: china_etfs_processed.csv")
    print(f"2. Copy code from: china_etfs_systematic_trading_code.py")
    print(f"3. Update: app/systematic_trading.py")
    print(f"4. Test: python scripts/validate_china_etfs.py")
    
    return True

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)
