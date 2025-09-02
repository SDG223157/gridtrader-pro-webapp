// Debug script to test parsing logic
const testData = `有色金属冶炼和压延加工业: 营业收入同比增长 13.8%, 利润总额同比增长 6.9%
电子设备制造业: 营业收入同比增长 11.2%, 利润总额同比增长 15.3%  
电气机械和器材制造业: 营业收入同比增长 9.7%, 利润总额同比增长 12.1%
计算机、通信和其他电子设备制造业: 营业收入同比增长 8.9%, 利润总额同比增长 18.7%`;

function parseIndustrialData(data) {
    const sectors = [];
    const lines = data.split('\n');
    
    console.log('=== DEBUG: Parsing industrial data ===');
    console.log('Total lines:', lines.length);
    console.log('Raw data length:', data.length);
    console.log('Raw data:', JSON.stringify(data));
    
    for (let i = 0; i < lines.length; i++) {
        const line = lines[i];
        console.log(`\nLine ${i}: "${line}"`);
        console.log(`Line length: ${line.length}`);
        console.log(`Line bytes: ${JSON.stringify(line)}`);
        
        // Skip headers and empty lines
        if (!line.trim()) {
            console.log(`  -> Skipping empty line`);
            continue;
        }
        
        // Test regex patterns
        console.log('\n  Testing regex patterns:');
        
        // Pattern 1: Colon-separated format
        const colonRegex = /([^:]+):\s*营业收入同比增长\s*([-\d.]+)%.*?利润总额同比增长\s*([-\d.]+)%/;
        const colonMatch = line.match(colonRegex);
        console.log(`  1. Colon regex test:`, colonMatch ? 'MATCH' : 'NO MATCH');
        if (colonMatch) {
            console.log(`     Match groups:`, colonMatch);
            const sectorName = colonMatch[1].trim();
            const revenueGrowth = parseFloat(colonMatch[2]);
            const profitGrowth = parseFloat(colonMatch[3]);
            
            console.log(`     Parsed: sector="${sectorName}", revenue=${revenueGrowth}, profit=${profitGrowth}`);
            
            if (sectorName && !isNaN(revenueGrowth) && !isNaN(profitGrowth)) {
                const sector = {
                    name: sectorName,
                    revenueGrowth,
                    profitGrowth,
                    performance: revenueGrowth > 5 && profitGrowth > 5 ? 'strong' : 
                                revenueGrowth < 0 || profitGrowth < -5 ? 'weak' : 'mixed'
                };
                sectors.push(sector);
                console.log(`     ✅ Added sector:`, sector);
                continue;
            } else {
                console.log(`     ❌ Invalid data: sector="${sectorName}", revenue=${revenueGrowth}, profit=${profitGrowth}`);
            }
        }
        
        // Pattern 2: Simpler colon pattern
        const simpleColonRegex = /([^:]+):\s*.*?(\d+\.\d+)%.*?(\d+\.\d+)%/;
        const simpleColonMatch = line.match(simpleColonRegex);
        console.log(`  2. Simple colon regex test:`, simpleColonMatch ? 'MATCH' : 'NO MATCH');
        if (simpleColonMatch) {
            console.log(`     Match groups:`, simpleColonMatch);
        }
        
        // Pattern 3: Extract all numbers
        const numberRegex = /(\d+\.\d+)/g;
        const numbers = line.match(numberRegex);
        console.log(`  3. Numbers found:`, numbers);
        
        // Pattern 4: Split by common delimiters
        const colonSplit = line.split(':');
        console.log(`  4. Colon split:`, colonSplit.length, 'parts');
        if (colonSplit.length >= 2) {
            console.log(`     Part 0 (sector):`, JSON.stringify(colonSplit[0]));
            console.log(`     Part 1 (data):`, JSON.stringify(colonSplit[1]));
        }
    }
    
    console.log('\n=== Final parsed sectors:', sectors.length, '===');
    console.log(sectors);
    return sectors;
}

// Run the test
console.log('Starting parsing test...\n');
const result = parseIndustrialData(testData);
console.log('\nTest completed. Sectors found:', result.length);
