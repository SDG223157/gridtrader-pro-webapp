# Portfolio Initiated Date Feature - Implementation Summary

## Overview
Added support for tracking the actual initiated date of a portfolio, which can be different from the `created_at` timestamp. This allows users to specify when they actually started a portfolio in real life, even if they're creating the record later in the system.

## Changes Made

### 1. Database Schema (`database.py`)
- Added `initiated_date` column to the `Portfolio` model
- Type: `Date` (nullable)
- Position: After `last_rebalanced` column
- Purpose: Track the actual date when the portfolio was initiated

### 2. Migration Script (`add_initiated_date_migration.py`)
- Created migration script to add the column to existing databases
- Includes safety checks to prevent duplicate column creation
- Shows table structure after successful migration
- **To run**: `python add_initiated_date_migration.py` (with database configured)

### 3. API Changes (`main.py`)
- Updated `CreatePortfolioRequest` model to accept optional `initiated_date` field
  - Format: ISO date string (YYYY-MM-DD)
  - Optional field (defaults to None)
- Modified `create_portfolio()` endpoint to:
  - Parse and validate the date format
  - Store the initiated_date if provided
  - Return proper error if date format is invalid

### 4. Frontend Changes

#### Create Portfolio Form (`templates/create_portfolio.html`)
- Added date input field for "Initiated Date"
- Field is optional with helpful hint text
- JavaScript updated to handle the new field
- Only sends initiated_date if user provides a value

#### Portfolio Detail Page (`templates/portfolio_detail.html`)
- Displays initiated date in the portfolio header
- Format: "Initiated: MMM DD, YYYY" (e.g., "Initiated: Oct 16, 2025")
- Only shows if initiated_date is set
- Positioned next to strategy type with visual separator

### 5. MCP Server Updates (`mcp-server/src/index.ts`)
- Updated `Portfolio` interface to include `initiated_date?: string`
- Updated `CreatePortfolioRequest` interface to include `initiated_date?: string`

## Usage

### Creating a Portfolio with Initiated Date
```json
POST /api/portfolios
{
  "name": "My Portfolio",
  "description": "Long-term growth",
  "strategy_type": "balanced",
  "initial_capital": 10000.00,
  "initiated_date": "2024-01-15"  // Optional
}
```

### UI Workflow
1. Navigate to "Create Portfolio" page
2. Fill in required fields (name, strategy, initial capital)
3. Optionally select "Initiated Date" using the date picker
4. Submit the form

### Viewing Initiated Date
- Portfolio detail page shows: "Initiated: Jan 15, 2024" (if set)
- Located in portfolio header, next to strategy type

## Migration Instructions

### Option 1: Using App Route (Recommended for Production)

Simply visit the migration endpoint after deployment:

```
GET https://gridsai.app/admin/migrate-initiated-date
```

Or using curl:
```bash
curl https://gridsai.app/admin/migrate-initiated-date
```

Response:
```json
{
  "success": true,
  "message": "initiated_date column added successfully",
  "details": "Column added after last_rebalanced column"
}
```

If column already exists:
```json
{
  "success": true,
  "message": "initiated_date column already exists"
}
```

### Option 2: Using Migration Script (Local/Development)

```bash
# Activate virtual environment
source venv/bin/activate

# Run migration script
python add_initiated_date_migration.py
```

The migration will:
1. Check if the column already exists
2. Add the column if needed
3. Show the updated table structure
4. Handle errors gracefully

## Benefits

1. **Historical Accuracy**: Track when portfolios were actually started, not just when they were entered into the system
2. **Flexibility**: Optional field - existing portfolios continue to work without the date
3. **User-Friendly**: Date picker makes it easy to select any date
4. **Data Integrity**: Server-side validation ensures correct date format

## Technical Notes

- The field is nullable, so existing portfolios won't be affected
- Date is stored as SQL `Date` type (not DateTime)
- Frontend uses HTML5 date input for browser-native date picking
- MCP server interfaces updated for consistency
- No breaking changes to existing API endpoints

## Files Modified

1. `database.py` - Added column to Portfolio model
2. `add_initiated_date_migration.py` - New migration script
3. `main.py` - Updated API models and endpoints
4. `templates/create_portfolio.html` - Added date input field
5. `templates/portfolio_detail.html` - Display initiated date
6. `mcp-server/src/index.ts` - Updated TypeScript interfaces

## Testing Recommendations

1. Test creating portfolio without initiated_date (should work)
2. Test creating portfolio with valid initiated_date (should save correctly)
3. Test creating portfolio with invalid date format (should return 400 error)
4. Test viewing portfolio with initiated_date (should display correctly)
5. Test viewing portfolio without initiated_date (should hide the field)
6. Test existing portfolios still work correctly
7. Run migration on test database first

## Future Enhancements

Potential improvements for later:
- Allow editing initiated_date after portfolio creation
- Show portfolio age based on initiated_date
- Filter/sort portfolios by initiated_date
- Performance analytics based on time since initiation
- Bulk update initiated_date for multiple portfolios

